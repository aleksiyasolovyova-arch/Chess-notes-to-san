from typing import Dict, Any, List
import chess
from app.domain.validator.explanation import explain_illegal, TRANSLATIONS
from app.domain.validator.correction import _find_correction


class MoveValidator:
    SUPPORTED_LANGUAGES = set(TRANSLATIONS.keys())

    def validate_moves(self, moves: List[str], lang: str = "en") -> Dict[str, Any]:
        if lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{lang}', choose from: {self.SUPPORTED_LANGUAGES}")

        t = TRANSLATIONS[lang]
        board = chess.Board()
        results = []

        for i, move in enumerate(moves):
            try:
                board.push_san(move)
                results.append({"move": move, "legal": True})
            except ValueError:
                reason = explain_illegal(board, move, lang=lang)

                suggestion, _ = _find_correction(board, moves, i)
                entry = {"move": move, "legal": False, "reason": reason}
                if suggestion:
                    entry["suggestion"] = suggestion
                    board.push_san(suggestion)
                else:
                    board.push(chess.Move.null())

                results.append(entry)

        all_legal = all(r["legal"] for r in results)
        return {"all_legal": all_legal, "moves": results}
