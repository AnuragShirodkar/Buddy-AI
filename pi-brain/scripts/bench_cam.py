#!/usr/bin/env python3
"""Fetch a JPEG from ESP32-CAM and save to captures/bench.jpg."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brain.camera import CameraClient
from brain.config import load_settings


def main() -> int:
    settings = load_settings()
    cam = CameraClient(settings.cam_url)
    print(f"GET {settings.cam_url}/capture ...")
    try:
        status = cam.status()
        print("Camera status:", status)
    except Exception as exc:  # noqa: BLE001
        print("Status check failed (continuing to capture):", exc)
    out = settings.captures_dir / "bench.jpg"
    cam.capture_to(out)
    size = out.stat().st_size
    print(f"Wrote {out} ({size} bytes)")
    if size < 1000:
        print("WARNING: file looks too small")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
