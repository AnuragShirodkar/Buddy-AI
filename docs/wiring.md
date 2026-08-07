# Wiring checklist

Update pin numbers to match your motor driver before flashing `esp32-motor`.

## Power (keep grounds common where logic shares a rail)

| Device | Supply | Notes |
|--------|--------|-------|
| Pi 3 B+ | 5 V power bank / official PSU | Do not power motors from Pi 5 V |
| ESP32-CAM | 5 V (≥500 mA capable) | Prefer external 5 V; avoid weak USB-only under load |
| ESP32-WROOM | 5 V or 3.3 V (board dependent) | Logic level for driver inputs |
| Motors | Battery matching motor rating (often 6–12 V) | Through motor driver only |
| Motor driver logic | 3.3–5 V per datasheet | Shared GND with ESP32-WROOM |

**Rule:** Motor battery negative and ESP32 GND must be tied together when the driver expects shared ground. Keep Pi power isolated except for Wi‑Fi (no shared motor current through Pi).

## ESP32-CAM (AI-Thinker style)

Default pins are set in firmware (`CAMERA_MODEL_AI_THINKER`). Connect:

- 5 V and GND
- Antenna / board as usual
- Optional: external antenna if your module supports it

No motor wires on the CAM board.

## ESP32-WROOM ↔ motor driver (defaults in firmware)

Defaults assume a dual H-bridge (L298N / L9110-style). Change in `esp32-motor/config.h` if needed.

| Function | Default GPIO | Wire to |
|----------|--------------|---------|
| Motor A IN1 | 26 | Driver IN1 / A-IA |
| Motor A IN2 | 27 | Driver IN2 / A-IB |
| Motor A PWM (ENA) | 25 | Driver ENA (tie HIGH if no PWM pin) |
| Motor B IN1 | 33 | Driver IN3 / B-IA |
| Motor B IN2 | 32 | Driver IN4 / B-IB |
| Motor B PWM (ENB) | 14 | Driver ENB (tie HIGH if no PWM pin) |
| GND | GND | Driver GND |

### L298N notes

- Jumpers on ENA/ENB: remove if using PWM from ESP32; leave on for full speed only.
- VCC (logic) often 5 V; 3.3 V ESP32 inputs usually work for IN pins — verify with your module.
- 5 V jumper: only if motor supply is ≤12 V and you want onboard 5 V regulator for logic.

### L9110 / DRV8833

- Often no separate ENA/ENB — set `MOTOR_HAS_PWM 0` in `config.h` and drive direction pins only (or map PWM pins unused).

## Optional pan-tilt servos (future)

| Servo | Suggested GPIO | Notes |
|-------|----------------|-------|
| Pan | 18 | External 5 V for servos; common GND |
| Tilt | 19 | Do not draw servo current from ESP32 3.3 V |

## Inventory worksheet (fill in)

- Motor type: _________________ (e.g. TT gear 3–6 V)
- Motor voltage: _______________
- Driver IC / board: ___________ (L298N / L9110 / DRV8833 / other)
- Left motor pins used: ________
- Right motor pins used: _______
- Wheel diameter (mm): _________ (for future odometry)

## Network

Put Pi 3 B+, ESP32-CAM, and ESP32-WROOM on the **same Wi‑Fi**.

| Device | Example | Set in |
|--------|---------|--------|
| CAM | `http://192.168.x.y/capture` | Serial log after boot |
| Motor | `http://192.168.x.z/cmd?dir=stop` | Serial log after boot |
| Pi brain | `.env` → `CAM_URL`, `MOTOR_URL` | `pi-brain/.env` |
