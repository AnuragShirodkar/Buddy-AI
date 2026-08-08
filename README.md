# ESP AI Finder Robot

Voice-driven finder robot: **Raspberry Pi 3 B+** brain, **ESP32-CAM** eyes (no Pi Camera), **ESP32-WROOM** motors/servos, phone/laptop mic for commands, Bluetooth speaker for replies.

Pin map PDF: [`docs/Buddy_AI_Pin_Connections.pdf`](docs/Buddy_AI_Pin_Connections.pdf).

## Repo layout

| Path | Role |
|------|------|
| [`pi-brain/`](pi-brain/) | Python orchestrator (vision, TTS, motors, find/approach loop) |
| [`esp32-cam/`](esp32-cam/) | Camera firmware — JPEG `/capture` + MJPEG `/stream` |
| [`esp32-motor/`](esp32-motor/) | Motor firmware — HTTP/UDP drive commands |
| [`cad/`](cad/) | OpenSCAD chassis, Pi tray, camera mast |
| [`docs/`](docs/) | Wiring, bench checklist, field test |

## Quick start

1. Flash [`esp32-cam`](esp32-cam/) and [`esp32-motor`](esp32-motor/) (set Wi‑Fi SSID/password).
2. On the Pi 3 B+: install deps, copy `.env`, run bench scripts, then the brain.
3. Pair a Bluetooth speaker; use phone/laptop to `POST` text commands.

See [`docs/bench-checklist.md`](docs/bench-checklist.md) for Phase 0.

## Voice command examples

- `Find my keys`
- `Look for a red bottle`
- `What's in front of you?`
- `Stop`
