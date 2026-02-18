from typing import List, Optional
from pydantic import BaseModel

from .move_dto import MoveDTO


class ScoresheetDTO(BaseModel):
    filename: str
    white: str
    white_elo: int
    black: str
    black_elo: int
    date: str
    tournament: str
    lang: str
    moves: List[MoveDTO]
    status: str