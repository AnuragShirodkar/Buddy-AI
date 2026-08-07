# Phase 0 — Bench prove checklist

Run these on a table with wheels lifted (blocks/books) before free driving.

## 1. Same Wi‑Fi

- [ ] Pi 3 B+ joined to home Wi‑Fi (or hosting AP)
- [ ] ESP32-CAM firmware flashed with SSID/password
- [ ] ESP32-WROOM motor firmware flashed with same SSID/password
- [ ] Note IPs from each ESP serial monitor

## 2. Camera JPEG

On the Pi:

```bash
cd ~/ESP_AI_CAM_32/pi-brain
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit CAM_URL / MOTOR_URL
python scripts/bench_cam.py
```

Expect: `captures/bench.jpg` written and file size > 0.

## 3. Motor ping

```bash
python scripts/bench_motor.py
```

Expect: brief forward then stop. Confirm wheel direction; swap IN wires or set `MOTOR_INVERT_LEFT/RIGHT` if needed.

## 4. Bluetooth speaker

```bash
# Pair speaker in Raspberry Pi OS Bluetooth UI, then:
python scripts/bench_speaker.py
```

Expect: spoken test phrase on the BT speaker (uses `espeak` or Piper if installed; falls back to printing the phrase).

## 5. Cloud vision smoke test

```bash
# Set OPENAI_API_KEY or GEMINI_API_KEY in .env
python scripts/bench_vision.py
```

Expect: short description of `captures/bench.jpg` printed.

## Pass criteria

All five steps succeed → proceed to Phase 1 (`python -m brain.server` and text commands).
