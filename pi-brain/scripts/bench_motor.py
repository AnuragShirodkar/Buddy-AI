#!/usr/bin/env python3
"""Pulse motors briefly — lift wheels off the ground first."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.config import load_settings
from brain.motor import MotorClient


def main() -> int:
    settings = load_settings()
    motor = MotorClient(
        settings.motor_url,
        udp_host=settings.motor_udp_host,
        udp_port=settings.motor_udp_port,
        use_udp=settings.use_motor_udp,
    )
    print(f"Motor at {settings.motor_url}")
    try:
        print("Status:", motor.status())
    except Exception as exc:  # noqa: BLE001
        print("Status failed:", exc)
        return 1

    print("forward 300ms...")
    motor.forward(settings.default_speed, 300)
    time.sleep(0.45)
    print("stop")
    motor.stop()
    time.sleep(0.2)
    print("left 250ms...")
    motor.left(settings.default_speed, 250)
    time.sleep(0.4)
    motor.stop()
    print("OK — confirm wheel directions; invert in esp32-motor/config.h if needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
