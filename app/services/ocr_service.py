import json

from app.domain.scoresheet import ScoresheetHeader
from app.services.ocr.base import OCRProvider
from app.services.preprocessing.pipeline import PreprocessingPipeline


class OCRService:
    def __init__(self, provider: OCRProvider, pipeline: PreprocessingPipeline) -> None:
        self._provider = provider
        self._pipeline = pipeline

    def process_scoresheet(self, file_bytes: bytes) -> tuple[ScoresheetHeader, list[str]]:
        preprocessed = self._pipeline.run(file_bytes)
        raw_text = self._provider.recognize(preprocessed)
        return self._parse(raw_text)

    def _parse(self, raw_text: str) -> tuple[ScoresheetHeader, list[str]]:
        text = raw_text.strip()

        # Strip markdown code fences if the model wrapped the JSON in them
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.rsplit("```", 1)[0].strip()

        data = json.loads(text)

        header = ScoresheetHeader(
            white=data.get("white") or "Unknown",
            white_elo=data.get("white_elo") or 0,
            black=data.get("black") or "Unknown",
            black_elo=data.get("black_elo") or 0,
            date=data.get("date") or "",
            tournament=data.get("tournament") or "",
            lang=data.get("lang") or "en",
        )
        raw_moves: list[str] = data.get("raw_moves") or []

        return header, raw_moves
