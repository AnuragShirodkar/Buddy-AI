#!/usr/bin/env python3
"""Cloud vision smoke test using captures/bench.jpg (run bench_cam.py first)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.config import load_settings
from brain.vision import VisionBrain


def main() -> int:
    settings = load_settings()
    path = settings.captures_dir / "bench.jpg"
    if not path.exists():
        print(f"Missing {path} — run scripts/bench_cam.py first")
        return 1
    if settings.ai_provider == "gemini" and not settings.gemini_api_key:
        print("Set GEMINI_API_KEY in .env")
        return 1
    if settings.ai_provider != "gemini" and not settings.openai_api_key:
        print("Set OPENAI_API_KEY in .env (or AI_PROVIDER=gemini + GEMINI_API_KEY)")
        return 1

    brain = VisionBrain(settings)
    result = brain.analyze(path.read_bytes(), "Describe what you see briefly for a robot operator.")
    print("description:", result.description)
    print("raw:", result.raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
