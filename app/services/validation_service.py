from typing import List, Dict, Any

from app.domain.validator.move_validator import MoveValidator
from app.domain.parser.notation_translator import NotationTranslator

class ValidationService:
    def __init__(self) -> None:
        self._validator = MoveValidator()
        self._translator = NotationTranslator()

    def validate_moves(self, moves: List[str], lang: str = "en") -> Dict[str, Any]:
        original_moves = moves.copy()

        if lang == "en":
            english_moves = moves
        else:
            english_moves = []
            for move in moves:
                translated = self._translator.translate(move, lang)
                english_moves.append(translated)

        validation_results = self._validator.validate_moves(english_moves, lang)

        for i, result in enumerate(validation_results["moves"]):
            result["move"] = original_moves[i]

        return validation_results