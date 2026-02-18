from typing import Dict

class NotationTranslator:
    PIECE_MAP = {
        'en': {'N': 'N', 'B': 'B', 'R': 'R', 'Q': 'Q', 'K': 'K'},
        'nl': {'P': 'N', 'L': 'B', 'T': 'R', 'D': 'Q', 'K': 'K'},
        'fr': {'C': 'N', 'F': 'B', 'T': 'R', 'D': 'Q', 'R': 'K'}
    }

    def translate(self, move: str, lang: str) -> str:
        if lang == "en":
            return move

        if lang not in self.PIECE_MAP:
            raise ValueError(f"Unsupported language '{lang}', choose from: {list(self.PIECE_MAP.keys())}")

        piece_map = self.PIECE_MAP[lang]

        if move in ("O-O", "O-O-O"):
            return move

        if move[0] in piece_map:
            return piece_map[move[0]] + move[1:]

        return move

    def translate_batch(self, moves: list[str], lang: str) -> list[str]:
        return [self.translate(m, lang) for m in moves]