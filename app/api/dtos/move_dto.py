from typing import Optional
from pydantic import BaseModel


class MoveDTO(BaseModel):
    raw_input: str
    san_intent: str
    is_valid_syntax: bool