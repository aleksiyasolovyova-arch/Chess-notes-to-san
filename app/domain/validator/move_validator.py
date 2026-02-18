from typing import Dict, Any, List
import chess
from app.domain.validator.explanation import explain_illegal, TRANSLATIONS


class MoveValidator:
    SUPPORTED_LANGUAGES = set(TRANSLATIONS.keys())


    def validate_moves(self, moves: List[str], lang: str = "en") -> Dict[str, Any]:
        if lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{lang}', choose from: {self.SUPPORTED_LANGUAGES}")

        t = TRANSLATIONS[lang]
        board = chess.Board()
        results = []

        for move in moves:
            try:
                board.push_san(move)
                results.append({"move": move, "legal": True})
            except ValueError as e:
                if "invalid" in str(e):
                    reason = t["not_valid_notation"]
                else:
                    reason = explain_illegal(board, move, lang=lang)
                results.append({"move": move, "legal": False, "reason": reason})

        all_legal = all(r["legal"] for r in results)
        return {"all_legal": all_legal, "moves": results}
