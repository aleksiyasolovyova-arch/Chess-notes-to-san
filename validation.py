import chess
from explanation import explain_illegal, TRANSLATIONS

SUPPORTED_LANGUAGES = set(TRANSLATIONS.keys())


def validate_moves(moves, lang="en"):
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language '{lang}', choose from: {SUPPORTED_LANGUAGES}")

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

    return results


if __name__ == "__main__":
    moves = ["e4", "e5", "Nf3", "Ra3", "Nc6", "Bb5", "Qe7", "Ba4",
             "Zz9", "Nf6", "O-O", "Ke5", "b5", "Qg4", "Bb4+",
             "Nd2", "Nbd2", "Bxb5"]

    for lang in ["en", "fr", "nl"]:
        print(f"\n=== {lang.upper()} ===")
        for i, result in enumerate(validate_moves(moves, lang=lang), 1):
            if result["legal"]:
                print(f"Move {i}: {result['move']} - LEGAL")
            else:
                print(f"Move {i}: {result['move']} - ILLEGAL ({result['reason']})")
