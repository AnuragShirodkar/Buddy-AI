from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .camera import CameraClient
from .config import Settings
from .motor import MotorClient
from .tts import Speaker
from .vision import VisionBrain, VisionResult

log = logging.getLogger(__name__)


class MissionState(str, Enum):
    IDLE = "idle"
    SEARCH = "search"
    APPROACH = "approach"
    DONE = "done"
    ABORTED = "aborted"


@dataclass
class MissionStatus:
    state: MissionState
    goal: str
    message: str
    last_vision: Optional[dict] = None


STOP_RE = re.compile(r"\b(stop|halt|freeze|emergency)\b", re.I)
DESCRIBE_RE = re.compile(
    r"(what('s| is) in front|describe|what do you see|look around)",
    re.I,
)
FIND_RE = re.compile(r"\b(find|look for|search for|locate|where is|where's)\b", re.I)


class FinderRobot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.camera = CameraClient(settings.cam_url)
        self.motor = MotorClient(
            settings.motor_url,
            udp_host=settings.motor_udp_host,
            udp_port=settings.motor_udp_port,
            use_udp=settings.use_motor_udp,
        )
        self.vision = VisionBrain(settings)
        self.speaker = Speaker(settings)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.status = MissionStatus(state=MissionState.IDLE, goal="", message="idle")

    def handle_command(self, text: str) -> MissionStatus:
        text = (text or "").strip()
        if not text:
            return self.status

        if STOP_RE.search(text):
            self.abort("Stopped by user")
            return self.status

        if DESCRIBE_RE.search(text) and not FIND_RE.search(text):
            return self.describe_scene(text)

        # Default: treat as find / approach goal
        self.start_mission(text)
        return self.status

    def describe_scene(self, prompt: str) -> MissionStatus:
        with self._lock:
            self.speaker.say("Looking")
            path = self.settings.captures_dir / "live.jpg"
            self.camera.capture_to(path)
            result = self.vision.analyze(path.read_bytes(), prompt)
            self.status = MissionStatus(
                state=MissionState.DONE,
                goal=prompt,
                message=result.description,
                last_vision=result.raw,
            )
            self.speaker.say(result.description or "I am not sure what I see")
            return self.status

    def start_mission(self, goal: str) -> None:
        self.abort("Restarting mission", speak=False)
        self._stop.clear()
        self.status = MissionStatus(
            state=MissionState.SEARCH,
            goal=goal,
            message="Starting search",
        )
        self.speaker.say(f"Looking for {goal}")
        self._thread = threading.Thread(
            target=self._run_mission,
            args=(goal,),
            name="finder-mission",
            daemon=True,
        )
        self._thread.start()

    def abort(self, reason: str = "Aborted", speak: bool = True) -> None:
        self._stop.set()
        try:
            self.motor.stop()
        except Exception as exc:  # noqa: BLE001 — hardware may be offline during bench
            log.warning("Motor stop failed: %s", exc)
        if self._thread and self._thread.is_alive() and threading.current_thread() is not self._thread:
            self._thread.join(timeout=2.0)
        self.status = MissionStatus(
            state=MissionState.ABORTED,
            goal=self.status.goal,
            message=reason,
            last_vision=self.status.last_vision,
        )
        if speak:
            self.speaker.say(reason)

    def _run_mission(self, goal: str) -> None:
        settings = self.settings
        deadline = time.time() + settings.mission_timeout_s
        lost = 0
        try:
            while not self._stop.is_set() and time.time() < deadline:
                path = settings.captures_dir / "live.jpg"
                try:
                    self.camera.capture_to(path)
                    vision = self.vision.analyze(path.read_bytes(), f"Find and approach: {goal}")
                except Exception as exc:  # noqa: BLE001
                    log.exception("Vision/capture failed")
                    self.speaker.say("Camera or vision error")
                    self.status = MissionStatus(
                        state=MissionState.ABORTED,
                        goal=goal,
                        message=str(exc),
                    )
                    return

                self.status = MissionStatus(
                    state=MissionState.APPROACH if vision.visible else MissionState.SEARCH,
                    goal=goal,
                    message=vision.description,
                    last_vision=vision.raw,
                )
                action = self._decide(vision)
                log.info("Vision action=%s dir=%s visible=%s", action, vision.direction, vision.visible)

                if action == "stop_found":
                    self.motor.stop()
                    msg = vision.description or "Found it"
                    self.status = MissionStatus(
                        state=MissionState.DONE,
                        goal=goal,
                        message=msg,
                        last_vision=vision.raw,
                    )
                    self.speaker.say(msg if "found" in msg.lower() else f"Found it. {msg}")
                    return

                if action == "search":
                    lost += 1
                    if lost > settings.max_lost_frames:
                        self.motor.stop()
                        self.status = MissionStatus(
                            state=MissionState.DONE,
                            goal=goal,
                            message="I lost the target",
                            last_vision=vision.raw,
                        )
                        self.speaker.say("I lost the target")
                        return
                    self.speaker.say("Searching")
                    self._pulse("left", settings.search_turn_ms)
                    continue

                lost = 0
                if action == "turn_left":
                    self._pulse("left", settings.turn_ms)
                elif action == "turn_right":
                    self._pulse("right", settings.turn_ms)
                elif action == "forward":
                    self.speaker.say("Moving closer")
                    self._pulse("forward", settings.forward_ms)
                else:
                    self._pulse("left", settings.search_turn_ms)

            if not self._stop.is_set():
                self.motor.stop()
                self.status = MissionStatus(
                    state=MissionState.DONE,
                    goal=goal,
                    message="Mission timed out",
                )
                self.speaker.say("I could not find it in time")
        finally:
            try:
                self.motor.stop()
            except Exception:  # noqa: BLE001
                pass

    def _decide(self, vision: VisionResult) -> str:
        settings = self.settings
        if vision.close_enough or (
            vision.bbox_h is not None and vision.bbox_h >= settings.close_bbox_height
        ):
            return "stop_found"
        if vision.action == "stop" and vision.visible and vision.close_enough:
            return "stop_found"
        if not vision.visible or vision.direction == "missing":
            return "search"

        # Prefer bbox center when present
        if vision.cx is not None:
            if vision.cx < 0.5 - settings.center_tolerance:
                return "turn_left"
            if vision.cx > 0.5 + settings.center_tolerance:
                return "turn_right"
            return "forward"

        if vision.direction == "left":
            return "turn_left"
        if vision.direction == "right":
            return "turn_right"
        if vision.direction == "center" or vision.action == "forward":
            return "forward"
        if vision.action in {"turn_left", "turn_right", "search", "forward"}:
            return vision.action
        return "search"

    def _pulse(self, direction: str, ms: int) -> None:
        ms = min(ms, self.settings.max_move_ms)
        if self._stop.is_set():
            return
        self.motor.command(direction, speed=self.settings.default_speed, ms=ms)
        # Wait for move + small settle; allow abort mid-wait
        end = time.time() + (ms / 1000.0) + 0.15
        while time.time() < end:
            if self._stop.is_set():
                self.motor.stop()
                return
            time.sleep(0.05)
