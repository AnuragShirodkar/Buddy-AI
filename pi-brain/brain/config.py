from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    cam_url: str
    motor_url: str
    motor_udp_host: str
    motor_udp_port: int
    use_motor_udp: bool
    ai_provider: str
    openai_api_key: str
    openai_vision_model: str
    gemini_api_key: str
    gemini_model: str
    turn_ms: int
    forward_ms: int
    search_turn_ms: int
    default_speed: int
    max_move_ms: int
    mission_timeout_s: float
    center_tolerance: float
    close_bbox_height: float
    max_lost_frames: int
    brain_host: str
    brain_port: int
    tts_engine: str
    piper_model: str
    espeak_voice: str
    captures_dir: Path


def load_settings() -> Settings:
    captures = ROOT / "captures"
    captures.mkdir(parents=True, exist_ok=True)
    return Settings(
        cam_url=os.getenv("CAM_URL", "http://192.168.1.50").rstrip("/"),
        motor_url=os.getenv("MOTOR_URL", "http://192.168.1.51").rstrip("/"),
        motor_udp_host=os.getenv("MOTOR_UDP_HOST", "192.168.1.51"),
        motor_udp_port=_int("MOTOR_UDP_PORT", 4210),
        use_motor_udp=_bool("USE_MOTOR_UDP", False),
        ai_provider=os.getenv("AI_PROVIDER", "openai").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_vision_model=os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        turn_ms=_int("TURN_MS", 280),
        forward_ms=_int("FORWARD_MS", 350),
        search_turn_ms=_int("SEARCH_TURN_MS", 400),
        default_speed=_int("DEFAULT_SPEED", 170),
        max_move_ms=_int("MAX_MOVE_MS", 800),
        mission_timeout_s=_float("MISSION_TIMEOUT_S", 90.0),
        center_tolerance=_float("CENTER_TOLERANCE", 0.12),
        close_bbox_height=_float("CLOSE_BBOX_HEIGHT", 0.45),
        max_lost_frames=_int("MAX_LOST_FRAMES", 5),
        brain_host=os.getenv("BRAIN_HOST", "0.0.0.0"),
        brain_port=_int("BRAIN_PORT", 8080),
        tts_engine=os.getenv("TTS_ENGINE", "espeak").strip().lower(),
        piper_model=os.getenv("PIPER_MODEL", ""),
        espeak_voice=os.getenv("ESPEAK_VOICE", "en"),
        captures_dir=captures,
    )
