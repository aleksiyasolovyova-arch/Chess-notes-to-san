import base64

import anthropic

from .base import OCRProvider

_PROMPT = """\
Transcribe this chess scoresheet image.

Return a JSON object with exactly these fields:
{
  "white": "<player name as a string, or null if not readable>",
  "white_elo": <integer rating or null>,
  "black": "<player name as a string, or null if not readable>",
  "black_elo": <integer rating or null>,
  "date": "<date in YYYY-MM-DD format, or null if not present>",
  "tournament": "<tournament name as a string, or null if not present>",
  "lang": "<language code: en, fr, or nl>",
  "raw_moves": ["<move1>", "<move2>", ...]
}

Rules:
- raw_moves: flat list of individual moves in play order, alternating white then black (no move numbers, no pairing)
- Preserve move notation exactly as written on the scoresheet (keep original piece letters — e.g. Dutch uses P/L/T/D/K, French uses C/F/T/D/R)
- lang: infer from piece letter conventions or header text (en=English, fr=French, nl=Dutch)
- Return only the JSON object — no markdown, no explanation, no extra text
"""


class ClaudeOCRProvider(OCRProvider):

    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self._client = anthropic.Anthropic()
        self._model = model

    @property
    def name(self) -> str:
        return f"Claude ({self._model})"

    def recognize(self, image_bytes: bytes) -> str:
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
        )

        return response.content[0].text if response.content else ""