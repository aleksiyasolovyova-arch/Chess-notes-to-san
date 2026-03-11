from typing import List, Optional
from pydantic import BaseModel


class ValidateRequestDTO(BaseModel):
    moves: List[str]
    ui_lang: str = "en"


class MoveValidationResultDTO(BaseModel):
    move: str
    legal: bool
    reason: Optional[str] = None


class ValidateResponseDTO(BaseModel):
    legal: bool
    moves: List[MoveValidationResultDTO]