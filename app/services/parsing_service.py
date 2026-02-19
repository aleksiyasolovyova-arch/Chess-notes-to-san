from pathlib import Path
import json
from typing import Dict, Any, List

from app.domain.parser.chess_parser import ChessParser
from app.domain.parsed_output import ParsedMove
from app.api.dtos.move_dto import MoveDTO

class ParsingService:

    def __init__(self):
        self.parser = ChessParser(
            self._load_common_header(),
            self._load_grid_configs()
        )

    def _load_common_header(self) -> Dict[str, Any]:
        path = Path(__file__).parents[1] / "corpus/common_header.json"
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def _load_grid_configs(self) -> Dict[str, Any]:
        configs = {}
        base = Path(__file__).parents[1] / "corpus/language_specific"
        for fname in ["english.json", "dutch.json", "french.json"]:
            path = base / fname
            with path.open(encoding="utf-8") as f:
                config = json.load(f)
                configs[config["iso_code"]] = config
        return configs

    def parse_scoresheet(self, ocr_text: str, raw_moves: List[str]) -> Dict[str, Any]:
        print(f"OCR TEXT:\n{ocr_text}\n")
        header = self.parser.extract_header(ocr_text)
        print(f"HEADER: {header}\n")
        parsed_moves = self.parser.parse_moves(raw_moves)
        lang = self.parser.detect_notation_language(raw_moves)

        return {
            "lang": lang,
            "header": header,
            "moves": [self._to_dto(m) for m in parsed_moves]
        }

    def _to_dto(self, move: ParsedMove) -> MoveDTO:
        return MoveDTO(
            raw_input=move.raw_input,
            san_intent=move.san_intent,
            is_valid_syntax=move.is_valid_syntax,
        )