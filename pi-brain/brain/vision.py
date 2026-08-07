from __future__ import annotations

import base64
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

from .config import Settings

log = logging.getLogger(__name__)

VISION_SYSTEM = """You are the vision brain for a small wheeled finder robot.
Analyze the camera image for the user's target.
Reply with ONLY compact JSON (no markdown) using this schema:
{
  "visible": true|false,
  "description": "short human sentence",
  "cx": 0.0-1.0 center-x of target bbox or null,
  "cy": 0.0-1.0 center-y of target bbox or null,
  "bbox_h": 0.0-1.0 normalized bbox height or null,
  "direction": "left"|"center"|"right"|"missing",
  "close_enough": true|false,
  "action": "turn_left"|"turn_right"|"forward"|"search"|"stop"|"describe"
}
Rules:
- direction left/right/center from image center; missing if not visible.
- close_enough true if the object is large/near (bbox_h roughly > 0.4) or clearly within arm reach.
- If the user only asks what is in view (no find goal), set action to describe and visible may be true for the scene.
"""


@dataclass
class VisionResult:
    visible: bool
    description: str
    cx: Optional[float]
    cy: Optional[float]
    bbox_h: Optional[float]
    direction: str
    close_enough: bool
    action: str
    raw: dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VisionResult":
        return cls(
            visible=bool(data.get("visible", False)),
            description=str(data.get("description") or ""),
            cx=_opt_float(data.get("cx")),
            cy=_opt_float(data.get("cy")),
            bbox_h=_opt_float(data.get("bbox_h")),
            direction=str(data.get("direction") or "missing").lower(),
            close_enough=bool(data.get("close_enough", False)),
            action=str(data.get("action") or "search").lower(),
            raw=data,
        )


def _opt_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


class VisionBrain:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, image_bytes: bytes, user_goal: str) -> VisionResult:
        provider = self.settings.ai_provider
        if provider == "gemini":
            data = self._gemini(image_bytes, user_goal)
        else:
            data = self._openai(image_bytes, user_goal)
        return VisionResult.from_dict(data)

    def describe(self, image_bytes: bytes, prompt: str = "Describe what you see briefly.") -> str:
        result = self.analyze(image_bytes, prompt)
        return result.description or str(result.raw)

    def _openai(self, image_bytes: bytes, user_goal: str) -> dict:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        b64 = base64.b64encode(image_bytes).decode("ascii")
        resp = client.chat.completions.create(
            model=self.settings.openai_vision_model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": VISION_SYSTEM},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"User goal: {user_goal}"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                },
            ],
        )
        content = resp.choices[0].message.content or "{}"
        return _extract_json(content)

    def _gemini(self, image_bytes: bytes, user_goal: str) -> dict:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        model = genai.GenerativeModel(
            self.settings.gemini_model,
            system_instruction=VISION_SYSTEM,
        )
        resp = model.generate_content(
            [
                f"User goal: {user_goal}",
                {"mime_type": "image/jpeg", "data": image_bytes},
            ]
        )
        content = getattr(resp, "text", None) or "{}"
        return _extract_json(content)
