#!/usr/bin/env python3
"""Speak a test phrase to the default audio device (pair BT speaker first)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.config import load_settings
from brain.tts import Speaker


def main() -> int:
    settings = load_settings()
    speaker = Speaker(settings)
    speaker.say("Finder robot speaker test. Bluetooth audio is working.")
    print("If you heard the phrase on the BT speaker, Phase 0 audio passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
