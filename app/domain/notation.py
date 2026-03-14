from typing import Dict, List
import re

NOTATION_CONFIG: Dict[str, Dict[str, str]] = {
    "en": {"K": "K", "Q": "Q", "R": "R", "B": "B", "N": "N"},
    "nl": {"K": "K", "D": "Q", "T": "R", "L": "B", "P": "N"},
    "fr": {"R": "K", "D": "Q", "T": "R", "F": "B", "C": "N"}
}


def detect_notation_language(raw_moves: List[str]) -> str:
    pieces = set()
    for move in raw_moves[:10]:
        match = re.match(r'^([KQRBNDTLFPC])', move)
        if match:
            pieces.add(match.group(1))


    if pieces & {'L', 'P'}: return 'nl'
    if pieces & {'F', 'C'}: return 'fr'

    for lang, mapping in NOTATION_CONFIG.items():
        if set(mapping.keys()) & pieces:
            return lang

    return "en"


def translate_notation(move: str, lang: str) -> str:
    if lang == "en":
        return move
    mapping = NOTATION_CONFIG.get(lang)
    if not mapping:
        raise ValueError(f"Unsupported language: '{lang}'")

    if move in ("O-O", "O-O-O"):
        return move
    for native, english in mapping.items():
        if move.startswith(native):
            return english + move[1:]
    return move  # Pawns unchanged


def translate_batch(moves: List[str], lang: str) -> List[str]:
    return [translate_notation(m, lang) for m in moves]
