from dataclasses import dataclass


@dataclass
class ScoresheetHeader:
    white: str
    white_elo: int
    black: str
    black_elo: int
    date: str
    tournament: str
    lang: str
