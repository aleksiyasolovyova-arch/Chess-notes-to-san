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

    ocr_result = ocr.process_scoresheet(contents)
    parse_result: Dict[str, Any] = parser.parse_scoresheet(
        ocr_result["raw_text"],
        ocr_result["raw_moves"]
    )
    print(parse_result["lang"])
    return ScoresheetDTO(
        filename=file.filename,
        white=parse_result["header"].get("white_player", ""),
        white_elo=parse_result["header"].get("white_elo"),
        black=parse_result["header"].get("black_player", ""),
        black_elo=parse_result["header"].get("black_elo"),
        date=parse_result["header"].get("date"),
        tournament=parse_result["header"].get("tournament"),
        lang=parse_result["lang"],
        moves=parse_result["moves"],
        status="success"
    )
