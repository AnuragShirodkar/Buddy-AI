from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import Settings

log = logging.getLogger(__name__)


class Speaker:
    """TTS to the default audio device (Bluetooth speaker once paired on the Pi)."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def say(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        log.info("TTS: %s", text)
        engine = self.settings.tts_engine
        try:
            if engine == "piper" and self.settings.piper_model:
                self._piper(text)
            elif engine == "espeak" and shutil.which("espeak"):
                subprocess.run(
                    ["espeak", "-v", self.settings.espeak_voice, text],
                    check=False,
                )
            elif engine == "espeak" and shutil.which("espeak-ng"):
                subprocess.run(
                    ["espeak-ng", "-v", self.settings.espeak_voice, text],
                    check=False,
                )
            else:
                print(f"[speak] {text}")
        except OSError as exc:
            log.warning("TTS failed: %s", exc)
            print(f"[speak] {text}")

    def _piper(self, text: str) -> None:
        model = self.settings.piper_model
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav = Path(tmp.name)
        try:
            proc = subprocess.run(
                ["piper", "--model", model, "--output_file", str(wav)],
                input=text.encode("utf-8"),
                check=False,
            )
            if proc.returncode != 0:
                print(f"[speak] {text}")
                return
            player = "aplay" if shutil.which("aplay") else None
            if player:
                subprocess.run([player, str(wav)], check=False)
            else:
                print(f"[speak] {text} (wrote {wav})")
        finally:
            if wav.exists():
                wav.unlink(missing_ok=True)
