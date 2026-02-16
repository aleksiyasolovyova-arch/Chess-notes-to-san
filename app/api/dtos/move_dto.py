from typing import Optional
from pydantic import BaseModel


class MoveDTO(BaseModel):
    raw_input: str
    san_intent: str
    move_type: str
    piece: str
    destination: Optional[str] = None
    disambiguation: Optional[str] = None
    promotion: Optional[str] = None
    check_state: Optional[str] = None
    is_capture: bool = False
    is_valid_syntax: bool