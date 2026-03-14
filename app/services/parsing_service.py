import re
from pathlib import Path
import json
from typing import Dict, Any, List


from app.domain.parser.chess_parser import ChessParser
from app.domain.parsed_output import ParsedMove
from app.api.dtos.move_dto import MoveDTO
from app.domain.scoresheet import ScoresheetHeader
from app.domain.parser.pgn import to_pgn


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


        notation_lang = self.parser.detect_notation_language(raw_moves)

        parsed_moves: List[ParsedMove] = self.parser.parse_batch(raw_moves, notation_lang)

        return {
            "notation_lang": notation_lang,
            "header": clean_header,
            "moves": [self._to_dto(m) for m in parsed_moves],
            "parsed_moves": parsed_moves,
        }

    def _validate_header(self, header: ScoresheetHeader) -> ScoresheetHeader:
        print(f"[DEBUG] raw result from OCR: repr={repr(header.result)}")
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
        result_cfg = fields_cfg.get("result", {})
        result = header.result
        valid_values = result_cfg.get("valid_values", [])
        split_cfg = result_cfg.get("split_box", {})

        if result not in valid_values:
            combine_map = split_cfg.get("combine_map", {})
            valid_parts = split_cfg.get("valid_parts", [])

            normalized = (
                result
                .replace(" ", "+")
                .replace("/", "+", 1)
                .replace("-", "+", 1)
            )

            if result not in valid_values and len(result) == 2 and result[0] in valid_parts and result[
                1] in valid_parts:
                normalized = f"{result[0]}+{result[1]}"

            result = combine_map.get(normalized, "*")


        return ScoresheetHeader(
            white=header.white,
            white_elo=white_elo,
            black=header.black,
            black_elo=black_elo,
            date=date,
            tournament=header.tournament,
            lang=header.lang,
            result=result,
        )

    def _to_dto(self, move: ParsedMove) -> MoveDTO:
        return MoveDTO(
            raw_input=move.raw_input,
            san_intent=move.san_intent,
            is_valid_syntax=move.is_valid_syntax,
        )

    def to_pgn(self, header: ScoresheetHeader, moves_list: list[str]) -> str:
        return to_pgn(header, moves_list)