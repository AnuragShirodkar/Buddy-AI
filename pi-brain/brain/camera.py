from __future__ import annotations

from pathlib import Path

import requests


class CameraClient:
    def __init__(self, base_url: str, timeout: float = 8.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def status(self) -> dict:
        r = requests.get(f"{self.base_url}/", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def capture_bytes(self) -> bytes:
        r = requests.get(f"{self.base_url}/capture", timeout=self.timeout)
        r.raise_for_status()
        if not r.content:
            raise RuntimeError("Empty image from camera")
        return r.content

    def capture_to(self, path: Path) -> Path:
        data = self.capture_bytes()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path
