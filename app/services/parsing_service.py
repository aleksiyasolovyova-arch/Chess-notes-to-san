from pathlib import Path
import json
from typing import Dict, Any, List

from app.domain.parser.chess_parser import ChessParser
from app.domain.parsed_output import ParsedMove
from app.api.dtos.move_dto import MoveDTO

class ParsingService:

    def __init__(self) -> None:
        self._parser = ChessParser(self._load_language_configs())

    def _load_language_configs(self) -> Dict[str, Any]:
        base = Path(__file__).parents[1] / "corpus" / "language_specific"
        configs: Dict[str, Any] = {}
        for code, fname in [("en", "english.json"), ("nl", "dutch.json"), ("fr", "french.json")]:
            path = base / fname
            with path.open(encoding="utf-8") as f:
                configs[code] = json.load(f)
        return configs

    def parse_moves(self, raw_moves: List[str], lang: str) -> List[MoveDTO]:
        parsed: List[ParsedMove] = self._parser.parse_batch(raw_moves, lang)
        return [self._to_dto(p) for p in parsed]

    def _to_dto(self, move: ParsedMove) -> MoveDTO:
        return MoveDTO(
            raw_input=move.raw_input,
            san_intent=move.san_intent,
            move_type=move.move_type,
            piece=move.piece,
            destination=move.destination,
            disambiguation=move.disambiguation,
            promotion=move.promotion,
            check_state=move.check_state,
            is_capture=move.is_capture,
            is_valid_syntax=move.is_valid_syntax,
        )