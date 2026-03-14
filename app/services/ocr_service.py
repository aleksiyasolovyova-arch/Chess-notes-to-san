import json
import re

from app.domain.scoresheet import ScoresheetHeader
from app.services.ocr.base import OCRProvider
from app.services.preprocessing.pipeline import PreprocessingPipeline

_MOVE_NUMBER_RE = re.compile(r"^(\d+)\.{1,3}\s*(.+)$")


class OCRService:
    def __init__(self, provider: OCRProvider, pipeline: PreprocessingPipeline) -> None:
        self._provider = provider
        self._pipeline = pipeline

    def process_scoresheet(self, file_bytes: bytes) -> tuple[ScoresheetHeader, list[str]]:
        preprocessed = self._pipeline.run(file_bytes)
        raw_text = self._provider.recognize(preprocessed)
        return self._parse(raw_text)

    def process_second_page(self, file_bytes: bytes) -> list[str]:
        preprocessed = self._pipeline.run(file_bytes)
        raw_text = self._provider.recognize(preprocessed)
        return self._parse_moves_only(raw_text)

    def _parse_moves_only(self, raw_text: str) -> list[str]:
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0].strip()

        data = json.loads(text)
        raw_moves: list[str] = data.get("raw_moves") or []
        return sort_and_strip_move_numbers([m for m in raw_moves if m is not None])

    def _parse(self, raw_text: str) -> tuple[ScoresheetHeader, list[str]]:
        text = raw_text.strip()

        # Strip markdown code fences if the model wrapped the JSON in them
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0].strip()

        data = json.loads(text)
        print(f"[DEBUG] raw OCR data: {data}\n")
        header = ScoresheetHeader(
            white=data.get("white") or "Unknown",
            white_elo=data.get("white_elo") or 0,
            black=data.get("black") or "Unknown",
            black_elo=data.get("black_elo") or 0,
            date=data.get("date") or "",
            tournament=data.get("tournament") or "",
            lang=data.get("lang") or "en",
            result=data.get("result") or "",
        )
        raw_moves: list[str] = [m for m in (data.get("raw_moves") or []) if m is not None]

        return header, sort_and_strip_move_numbers(raw_moves)


def sort_and_strip_move_numbers(moves: list[str]) -> list[str]:
    numbered: list[tuple[int, str]] = []
    unnumbered: list[str] = []

    for move in moves:
        match = _MOVE_NUMBER_RE.match(move.strip())
        if match:
            numbered.append((int(match.group(1)), match.group(2)))
        else:
            unnumbered.append(move)

    numbered.sort(key=lambda x: x[0])
    return [move for _, move in numbered] + unnumbered
