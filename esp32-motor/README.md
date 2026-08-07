# ESP32-WROOM motor firmware

Drives a dual H-bridge from Wi‑Fi commands. Edit pins in [`config.h`](config.h); see [`docs/wiring.md`](../docs/wiring.md).

## Setup

1. Board: **ESP32 Dev Module** (WROOM).
2. Library: **ArduinoJson** (v6+).
3. Copy `secrets.h.example` → `secrets.h` with Wi‑Fi credentials.
4. Match `PIN_*` and `MOTOR_HAS_PWM` to your driver.

## Commands

```text
GET  /cmd?dir=forward&speed=180&ms=300
POST /cmd   {"dir":"left","speed":160,"ms":250}
UDP  4210   forward 180 300
```

`dir`: `forward` | `back` | `left` | `right` | `stop`

Safety: timed moves auto-stop; watchdog stops motors if no command within `WATCHDOG_MS`.
