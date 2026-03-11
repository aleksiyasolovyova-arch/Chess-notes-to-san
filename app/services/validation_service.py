from typing import List, Dict, Any
from app.domain.notation import translate_batch
from app.domain.validator.move_validator import MoveValidator


class ValidationService:
    def __init__(self):
        self._validator = MoveValidator()

    def validate_moves(
            self,
            moves: List[str],
            notation_lang: str = "en",
            ui_lang: str = "en",
    ) -> Dict[str, Any]:
        original_moves = moves.copy()

        english_moves = translate_batch(moves, notation_lang) if notation_lang != "en" else moves

        results = self._validator.validate_moves(english_moves, ui_lang)

        for i, result in enumerate(results["moves"]):
            result["move"] = original_moves[i]

        return results

