# Wiring checklist

**Eyes = ESP32-CAM** (no Raspberry Pi Camera Module).  
**Brain = Pi 3 B+**. **Drive / servos / distance = ESP32-WROOM**.

Also see printable PDF: [`Buddy_AI_Pin_Connections.pdf`](Buddy_AI_Pin_Connections.pdf).

Update motor pin numbers to match your driver before flashing `esp32-motor`.

## Power (keep grounds common where logic shares a rail)

| Device | Supply | Notes |
|--------|--------|-------|
| Pi 3 B+ | 5 V power bank / official PSU | Do not power motors from Pi 5 V |
| ESP32-CAM | 5 V (≥500 mA capable) | Prefer external 5 V; avoid weak USB-only under load |
| ESP32-WROOM | 5 V or 3.3 V (board dependent) | Logic level for driver inputs |
| Motors | Battery matching motor rating (often 6–12 V) | Through motor driver only |
| Motor driver logic | 3.3–5 V per datasheet | Shared GND with ESP32-WROOM |
| Servos | External 5 V | Common GND with ESP32-WROOM; never from 3.3 V |

**Rule:** Motor battery negative and ESP32-WROOM GND must be tied together when the driver expects shared ground. Keep Pi power isolated except for Wi‑Fi (no shared motor current through Pi).

## ESP32-CAM (AI-Thinker style) — eyes

Camera sensor pins are onboard (`CAMERA_MODEL_AI_THINKER` in firmware). You wire:

| CAM pin | Connect to |
|---------|------------|
| 5 V | Solid 5 V supply |
| GND | Supply GND |
| (flash only) | FTDI TX/RX + GPIO0→GND while uploading |

- Put CAM on the **same Wi‑Fi** as the Pi and motor ESP32  
- Serial @ 115200 prints IP after boot  
- Pi uses `CAM_URL=http://CAM_IP` → `GET /capture`  
- **No motor wires on the CAM board**  
- Mount on pan-tilt; servos are driven by **ESP32-WROOM**

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

## Pan-tilt servos → ESP32-WROOM

| Servo | GPIO | Notes |
|-------|------|-------|
| Pan signal | 18 | External 5 V for servo power; common GND |
| Tilt signal | 19 | Do not draw servo current from ESP32 3.3 V |

## Distance sensor → ESP32-WROOM

### HC-SR04

| Sensor | ESP32-WROOM |
|--------|-------------|
| VCC | 5 V |
| GND | GND |
| TRIG | GPIO 12 |
| ECHO | GPIO 13 (level-shift 5 V → 3.3 V if possible) |

### VL53L0X (ToF alternative)

| Sensor | ESP32-WROOM |
|--------|-------------|
| VCC | 3.3 V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

## Audio (no pins)

| Device | Connection |
|--------|------------|
| Bluetooth speaker | Pair to Pi 3 B+ (voice out) |
| Phone / laptop mic (v1) | Commands over Wi‑Fi to Pi `:8080` |
| ReSpeaker (later) | Next version onboard mic |

## Inventory worksheet (fill in)

- Motor type: _________________ (e.g. TT gear 3–6 V)
- Motor voltage: _______________
- Driver IC / board: ___________ (L298N / L9110 / DRV8833 / other)
- Left motor pins used: ________
- Right motor pins used: _______
- Wheel diameter (mm): _________ (for future odometry)

## Network

Put **Pi 3 B+, ESP32-CAM, and ESP32-WROOM** on the **same Wi‑Fi**.

| Device | Example | Set in |
|--------|---------|--------|
| CAM | `http://192.168.x.y` (`/capture`) | Serial log after boot → `pi-brain/.env` `CAM_URL` |
| Motor | `http://192.168.x.z` (`/cmd`) | Serial log after boot → `MOTOR_URL` |
| Pi brain | `:8080` | phone / laptop browser |
