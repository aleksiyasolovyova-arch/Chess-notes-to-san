from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.api.dependencies import get_ocr_service, get_parsing_service
from app.api.dtos.scoresheet_dto import ScoresheetDTO
from app.services.ocr_service import OCRService
from app.services.parsing_service import ParsingService

router = APIRouter(prefix="/api/scoresheets", tags=["scoresheets"])

MAX_SIZE = 10 * 1024 * 1024
ACCEPTED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

@router.post("", response_model=ScoresheetDTO)
async def upload_scoresheet( file: UploadFile = File(...), ocr: OCRService = Depends(get_ocr_service), parser: ParsingService = Depends(get_parsing_service)):
    if file.content_type not in ACCEPTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    header, raw_moves = ocr.process_scoresheet(contents)
    moves_dto = parser.parse_moves(raw_moves, header.lang)

    return ScoresheetDTO(
        filename=file.filename,
        white=header.white,
        white_elo=header.white_elo,
        black=header.black,
        black_elo=header.black_elo,
        date=header.date,
        tournament=header.tournament,
        lang=header.lang,
        moves=moves_dto,
        status="success",
    )
