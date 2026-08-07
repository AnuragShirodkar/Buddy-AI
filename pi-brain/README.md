# Pi brain (Raspberry Pi 3 B+)

Python orchestrator: capture from ESP32-CAM → cloud vision → speak on BT speaker → drive ESP32-WROOM.

## Install (on the Pi)

```bash
cd pi-brain
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo apt-get install -y espeak espeak-ng  # TTS to Bluetooth speaker
cp .env.example .env
# Edit CAM_URL, MOTOR_URL, OPENAI_API_KEY or GEMINI_API_KEY
```

Pair your Bluetooth speaker in Raspberry Pi OS before TTS tests.

## Bench scripts (Phase 0)

```bash
python scripts/bench_cam.py
python scripts/bench_motor.py
python scripts/bench_speaker.py
python scripts/bench_vision.py
```

## Run

HTTP API (phone/laptop send text commands):

```bash
python -m brain.server
# POST http://PI_IP:8080/command  {"text":"Find my keys"}
```

CLI:

```bash
python -m brain "What is in front of you?"
python -m brain "Find the red bottle"
python -m brain stop
```

Voice in (v1): use any phone/laptop speech-to-text, then POST the transcript to `/command`.
