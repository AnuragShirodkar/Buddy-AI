# ESP32-CAM firmware

Arduino IDE / Arduino-CLI sketch for **AI-Thinker ESP32-CAM**.

## Setup

1. Install **esp32** board package (Espressif).
2. Board: `AI Thinker ESP32-CAM` (or ESP32 Wrover Module + PSRAM).
3. Copy `secrets.h.example` → `secrets.h` and set Wi‑Fi SSID/password.
4. Upload with an FTDI adapter (GPIO0 → GND for flash).

## Endpoints

| URL | Description |
|-----|-------------|
| `GET /` | Status JSON + IP |
| `GET /capture` | Single JPEG |
| `GET /stream` | MJPEG on port **81** |

Serial monitor @ 115200 prints the IP after connect.
