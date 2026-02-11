from dataclasses import dataclass
from typing import Optional
# Represents the result of parsing a raw OCR string
@dataclass
class ParsedMove:
    raw_input: str
    san_intent: str
    move_type: str

    piece: str
    destination: Optional[str] = None
    disambiguation: Optional[str] = None
    promotion: Optional[str] = None
    check_state: Optional[str] = None #"+" or "#"
    is_capture: bool = False

    @property
    def is_valid_syntax(self) -> bool:
        if self.move_type == "castling":
            return True
        return self.destination is not None