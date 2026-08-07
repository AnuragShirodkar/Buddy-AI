from __future__ import annotations

import socket
from typing import Optional

import requests


class MotorClient:
    def __init__(
        self,
        base_url: str,
        udp_host: str = "",
        udp_port: int = 4210,
        use_udp: bool = False,
        timeout: float = 3.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.use_udp = use_udp
        self.timeout = timeout

    def status(self) -> dict:
        r = requests.get(f"{self.base_url}/", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def command(self, direction: str, speed: int = 170, ms: int = 300) -> None:
        direction = direction.lower().strip()
        ms = max(0, ms)
        if self.use_udp and self.udp_host:
            self._udp(f"{direction} {speed} {ms}")
            return
        r = requests.post(
            f"{self.base_url}/cmd",
            json={"dir": direction, "speed": speed, "ms": ms},
            timeout=self.timeout,
        )
        r.raise_for_status()

    def stop(self) -> None:
        self.command("stop", speed=0, ms=0)

    def forward(self, speed: int, ms: int) -> None:
        self.command("forward", speed=speed, ms=ms)

    def back(self, speed: int, ms: int) -> None:
        self.command("back", speed=speed, ms=ms)

    def left(self, speed: int, ms: int) -> None:
        self.command("left", speed=speed, ms=ms)

    def right(self, speed: int, ms: int) -> None:
        self.command("right", speed=speed, ms=ms)

    def _udp(self, payload: str) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(payload.encode("utf-8"), (self.udp_host, self.udp_port))
        finally:
            sock.close()
