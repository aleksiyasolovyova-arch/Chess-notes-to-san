from typing import List, Optional
from pydantic import BaseModel, Field

from .move_dto import MoveDTO


class ScoresheetDTO(BaseModel):
    filename: Optional[str] = None
    white: str = Field(default="")
    white_elo: Optional[int] = Field(None)
    black: str = Field(default="")
    black_elo: Optional[int] = Field(None)
    date: Optional[str] = None
    tournament: Optional[str] = None
    lang: str
    moves: List[MoveDTO]
    status: str