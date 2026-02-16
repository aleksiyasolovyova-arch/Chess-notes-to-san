from functools import lru_cache

from app.services.ocr_service import OCRService
from app.services.parsing_service import ParsingService
from app.services.validation_service import ValidationService

@lru_cache
def get_ocr_service() -> OCRService:
    return OCRService()


@lru_cache
def get_parsing_service() -> ParsingService:
    return ParsingService()


@lru_cache
def get_validation_service() -> ValidationService:
    return ValidationService()