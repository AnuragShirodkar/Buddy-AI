#!/usr/bin/env python3
"""
Laptop/phone helper: send text commands to the Pi brain.
For voice: use OS dictation or any STT, then paste/send the transcript.

  python scripts/send_command.py --host 192.168.1.20 "Find my keys"
  python scripts/send_command.py --host 192.168.1.20 --interactive
"""
from __future__ import annotations

import argparse
import json
import sys

import requests


def send(host: str, port: int, text: str) -> dict:
    url = f"http://{host}:{port}/command"
    r = requests.post(url, json={"text": text}, timeout=120)
    r.raise_for_status()
    return r.json()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1", help="Pi IP address")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--interactive", "-i", action="store_true")
    p.add_argument("text", nargs="*")
    args = p.parse_args()

    if args.interactive:
        print("Type commands (stop / quit to exit). Use phone dictation into this terminal if available.")
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if not line or line.lower() in {"quit", "exit", "q"}:
                return 0
            try:
                print(json.dumps(send(args.host, args.port, line), indent=2))
            except Exception as exc:  # noqa: BLE001
                print("Error:", exc)
        return 0

    text = " ".join(args.text).strip()
    if not text:
        p.print_help()
        return 2
    print(json.dumps(send(args.host, args.port, text), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
