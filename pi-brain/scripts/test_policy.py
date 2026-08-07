#!/usr/bin/env python3
"""Offline unit check for policy decision logic (no hardware/API)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.config import load_settings
from brain.policy import FinderRobot
from brain.vision import VisionResult


def main() -> int:
    robot = FinderRobot(load_settings())
    cases = [
        (
            VisionResult(True, "keys left", 0.2, 0.5, 0.2, "left", False, "turn_left", {}),
            "turn_left",
        ),
        (
            VisionResult(True, "keys right", 0.8, 0.5, 0.2, "right", False, "turn_right", {}),
            "turn_right",
        ),
        (
            VisionResult(True, "keys center", 0.5, 0.5, 0.25, "center", False, "forward", {}),
            "forward",
        ),
        (
            VisionResult(True, "close", 0.5, 0.5, 0.55, "center", True, "stop", {}),
            "stop_found",
        ),
        (
            VisionResult(False, "missing", None, None, None, "missing", False, "search", {}),
            "search",
        ),
    ]
    failed = 0
    for vision, expect in cases:
        got = robot._decide(vision)
        ok = got == expect
        print(("OK" if ok else "FAIL"), expect, "->", got, vision.description)
        failed += int(not ok)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
