from typing import List, Optional
from pydantic import BaseModel

# TODO: discuss with eva about these thingies, have to align better with frontend maybe

class ValidateRequestDTO(BaseModel):
    moves: List[str]
    lang: str = "en"


class MoveValidationResultDTO(BaseModel):
    move: str
    legal: bool
    reason: Optional[str] = None


class ValidateResponseDTO(BaseModel):
    legal: bool
    moves: List[MoveValidationResultDTO]