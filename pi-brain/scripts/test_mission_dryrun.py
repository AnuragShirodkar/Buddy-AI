"""
Simulate find-and-approach loop without motors/camera (dry-run).

Uses canned vision frames to verify stop/timeout/lost-target safety paths.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.config import load_settings
from brain.policy import FinderRobot, MissionState
from brain.vision import VisionResult


def main() -> int:
    settings = load_settings()
    robot = FinderRobot(settings)
    robot.camera = MagicMock()
    robot.motor = MagicMock()
    robot.speaker = MagicMock()
    robot.speaker.say = MagicMock()

    frames = [
        VisionResult(False, "searching", None, None, None, "missing", False, "search", {}),
        VisionResult(True, "target left", 0.25, 0.5, 0.2, "left", False, "turn_left", {}),
        VisionResult(True, "target center", 0.5, 0.5, 0.28, "center", False, "forward", {}),
        VisionResult(True, "Found the bottle", 0.5, 0.5, 0.5, "center", True, "stop", {}),
    ]
    idx = {"i": 0}

    def fake_analyze(_bytes, _goal):
        i = min(idx["i"], len(frames) - 1)
        idx["i"] += 1
        return frames[i]

    robot.camera.capture_to = MagicMock(side_effect=lambda p: p.write_bytes(b"\xff\xd8fake") or p)
    robot.vision.analyze = fake_analyze
    robot._pulse = MagicMock()

    robot.start_mission("red bottle")
    if robot._thread:
        robot._thread.join(timeout=15)

    assert robot.status.state == MissionState.DONE, robot.status
    assert "found" in robot.status.message.lower() or robot.status.last_vision is not None
    robot.motor.stop.assert_called()
    print("Dry-run approach OK:", robot.status.message)

    # Emergency stop mid-mission
    idx["i"] = 0
    infinite = VisionResult(True, "far", 0.5, 0.5, 0.1, "center", False, "forward", {})

    def forever(_b, _g):
        time.sleep(0.05)
        return infinite

    robot2 = FinderRobot(settings)
    robot2.camera = MagicMock()
    robot2.camera.capture_to = MagicMock(side_effect=lambda p: p.write_bytes(b"\xff\xd8fake") or p)
    robot2.motor = MagicMock()
    robot2.speaker = MagicMock()
    robot2.vision.analyze = forever
    robot2._pulse = lambda *a, **k: time.sleep(0.1)
    robot2.start_mission("keys")
    time.sleep(0.3)
    robot2.abort("Stopped by user")
    assert robot2.status.state == MissionState.ABORTED
    robot2.motor.stop.assert_called()
    print("Emergency stop OK")

    # Lost target
    robot3 = FinderRobot(settings)
    robot3.camera = MagicMock()
    robot3.camera.capture_to = MagicMock(side_effect=lambda p: p.write_bytes(b"\xff\xd8fake") or p)
    robot3.motor = MagicMock()
    robot3.speaker = MagicMock()
    robot3.vision.analyze = lambda *_: VisionResult(
        False, "gone", None, None, None, "missing", False, "search", {}
    )
    robot3._pulse = MagicMock()
    # lower lost threshold via decide path — max_lost_frames from settings
    robot3.start_mission("keys")
    if robot3._thread:
        robot3._thread.join(timeout=20)
    assert robot3.status.state == MissionState.DONE
    assert "lost" in robot3.status.message.lower()
    print("Lost target OK:", robot3.status.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
