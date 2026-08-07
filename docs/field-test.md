# Field test — find & approach

Prerequisites: Phase 0 bench checklist passed; chassis assembled or temporary tape mount; good lighting.

## Safety before free run

- [ ] Clear floor; no cliffs/stairs
- [ ] Know how to shout/send `stop` (HTTP or CLI)
- [ ] Motor max pulse durations limited in brain config (`MAX_MOVE_MS`, `MISSION_TIMEOUT_S`)
- [ ] Watchdog: motor board stops if no command within `WATCHDOG_MS`

## Test A — Describe only

```bash
curl -X POST http://PI_IP:8080/command -H 'Content-Type: application/json' \
  -d '{"text":"What is in front of you?"}'
```

Robot should capture, speak/print a description, **not** drive far.

## Test B — Find a high-contrast object

Place a brightly colored bottle 1–2 m ahead, centered-ish.

```bash
curl -X POST http://PI_IP:8080/command -H 'Content-Type: application/json' \
  -d '{"text":"Find the red bottle"}'
```

Expect: search turns if needed → center → creep forward → stop → “Found it” (or timeout message).

## Test C — Emergency stop

While approaching:

```bash
curl -X POST http://PI_IP:8080/command -H 'Content-Type: application/json' \
  -d '{"text":"stop"}'
```

Expect: immediate motor stop; mission aborted.

## Test D — Lost target

Start find, then cover/remove the object mid-run.

Expect: “lost” / search retries then timeout; motors stop.

## Pass criteria

- Stop always works
- No continuous motor spin after mission end
- Speaks status on BT speaker (or logs clearly if TTS unavailable)
- Approaches object without violent oscillation (tune `TURN_MS` / `FORWARD_MS` in `.env`)
