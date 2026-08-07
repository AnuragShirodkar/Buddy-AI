from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from .config import load_settings
from .policy import FinderRobot

log = logging.getLogger(__name__)

PHONE_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Finder Robot</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 28rem; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.25rem; }
    textarea { width: 100%; min-height: 4rem; font-size: 1.1rem; }
    button { font-size: 1.1rem; padding: 0.6rem 1rem; margin: 0.4rem 0.4rem 0 0; }
    #out { white-space: pre-wrap; background: #f4f4f4; padding: 0.75rem; border-radius: 6px; }
    .row { display: flex; flex-wrap: wrap; }
  </style>
</head>
<body>
  <h1>ESP AI Finder</h1>
  <p>Type a command, or use your phone keyboard mic for dictation.</p>
  <textarea id="cmd" placeholder="Find my keys"></textarea>
  <div class="row">
    <button id="go">Send</button>
    <button id="stop">Stop</button>
    <button id="look">What's in front?</button>
  </div>
  <h2>Status</h2>
  <div id="out">idle</div>
  <script>
    const out = document.getElementById('out');
    async function send(text) {
      out.textContent = 'Sending…';
      const r = await fetch('/command', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
      });
      out.textContent = JSON.stringify(await r.json(), null, 2);
    }
    document.getElementById('go').onclick = () => send(document.getElementById('cmd').value);
    document.getElementById('stop').onclick = () => send('stop');
    document.getElementById('look').onclick = () => send("What is in front of you?");
    setInterval(async () => {
      try {
        const r = await fetch('/status');
        const j = await r.json();
        if (j.state !== 'idle') out.textContent = JSON.stringify(j, null, 2);
      } catch (e) {}
    }, 2000);
  </script>
</body>
</html>
"""


def create_app(robot: FinderRobot | None = None) -> Flask:
    settings = load_settings()
    robot = robot or FinderRobot(settings)
    app = Flask(__name__)

    @app.get("/")
    def index():
        return PHONE_UI

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "state": robot.status.state.value})

    @app.get("/status")
    def status():
        s = robot.status
        return jsonify(
            {
                "state": s.state.value,
                "goal": s.goal,
                "message": s.message,
                "last_vision": s.last_vision,
            }
        )

    @app.post("/command")
    def command():
        data = request.get_json(silent=True) or {}
        text = data.get("text") or data.get("command") or ""
        if not text and request.data:
            text = request.data.decode("utf-8", errors="ignore")
        log.info("Command: %s", text)
        result = robot.handle_command(text)
        return jsonify(
            {
                "state": result.state.value,
                "goal": result.goal,
                "message": result.message,
                "last_vision": result.last_vision,
            }
        )

    @app.post("/stop")
    def stop():
        robot.abort("Stopped")
        return jsonify({"ok": True, "state": robot.status.state.value})

    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()
    robot = FinderRobot(settings)
    app = create_app(robot)
    print(f"Finder brain listening on http://{settings.brain_host}:{settings.brain_port}")
    print("Open the Pi IP in a phone browser for voice-dictation commands.")
    print('POST /command {"text":"Find my keys"}')
    app.run(host=settings.brain_host, port=settings.brain_port, threaded=True)


if __name__ == "__main__":
    main()
