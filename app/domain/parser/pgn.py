from typing import List

from app.domain.scoresheet import ScoresheetHeader


def to_pgn(header: ScoresheetHeader, moves_san: List[str]) -> str:
    result = header.result or "*"
    tags = [
        f'[Event "{header.tournament or "?"}"]',
        f'[Site "?"]',
        f'[Date "{header.date or "????.??.??"}"]',
        f'[Round "?"]',
        f'[White "{header.white or "?"}"]',
        f'[Black "{header.black or "?"}"]',
        f'[WhiteElo "{header.white_elo or "?"}"]',
        f'[BlackElo "{header.black_elo or "?"}"]',
        f'[Result "{result}"]',
    ]

    parts = []
    move_no = 1
    for i in range(0, len(moves_san), 2):
        w = moves_san[i]
        b = moves_san[i + 1] if i + 1 < len(moves_san) else ""
        if not w and not b:
            continue
        if b:
            parts.append(f"{move_no}. {w} {b}")
        else:
            parts.append(f"{move_no}. {w}")
        move_no += 1
    moves_str = " ".join(parts) + " *"
    return "\n".join(tags) + "\n\n" + moves_str
