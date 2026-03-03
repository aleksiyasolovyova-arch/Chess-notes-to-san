import re
from pathlib import Path
import json
from typing import Dict, Any, List

from app.domain.parser.chess_parser import ChessParser
from app.domain.parsed_output import ParsedMove
from app.api.dtos.move_dto import MoveDTO
from app.domain.scoresheet import ScoresheetHeader


class ParsingService:

    def __init__(self):
        self._header_config = self._load_common_header()
        self.parser = ChessParser(self._load_grid_configs())

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

    def parse_scoresheet(
        self,
        header: ScoresheetHeader,
        raw_moves: List[str],
    ) -> Dict[str, Any]:
        clean_header = self._validate_header(header)

        lang = clean_header.lang
        if lang not in self.parser.grid_configs:
            lang = self.parser.detect_notation_language(raw_moves)

        parsed_moves = self.parser.parse_batch(raw_moves, lang)

        return {
            "lang": lang,
            "header": clean_header,
            "moves": [self._to_dto(m) for m in parsed_moves],
        }

    def _validate_header(self, header: ScoresheetHeader) -> ScoresheetHeader:
        fields_cfg = self._header_config.get("fields", {})

        date = header.date
        date_pattern = fields_cfg.get("date", {}).get("pattern")
        if date and date_pattern and not re.fullmatch(date_pattern, date):
            date = ""

        rating_pattern = fields_cfg.get("rating", {}).get("pattern")
        white_elo = header.white_elo
        black_elo = header.black_elo
        if rating_pattern:
            if not re.fullmatch(rating_pattern, str(white_elo)):
                white_elo = 0
            if not re.fullmatch(rating_pattern, str(black_elo)):
                black_elo = 0

        return ScoresheetHeader(
            white=header.white,
            white_elo=white_elo,
            black=header.black,
            black_elo=black_elo,
            date=date,
            tournament=header.tournament,
            lang=header.lang,
        )

    def _to_dto(self, move: ParsedMove) -> MoveDTO:
        return MoveDTO(
            raw_input=move.raw_input,
            san_intent=move.san_intent,
            is_valid_syntax=move.is_valid_syntax,
        )