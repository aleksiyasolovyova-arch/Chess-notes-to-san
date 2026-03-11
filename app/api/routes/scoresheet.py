from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.api.dependencies import get_ocr_service, get_parsing_service
from app.api.dtos.scoresheet_dto import ScoresheetDTO
from app.services.ocr_service import OCRService
from app.services.parsing_service import ParsingService

router = APIRouter(prefix="/api/scoresheets", tags=["scoresheets"])

MAX_SIZE = 10 * 1024 * 1024
ACCEPTED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


@router.post("", response_model=ScoresheetDTO)
async def upload_scoresheet(
    file: UploadFile = File(...),
    file2: Optional[UploadFile] = File(None),
    ocr: OCRService = Depends(get_ocr_service),
    parser: ParsingService = Depends(get_parsing_service),
):
    if file.content_type not in ACCEPTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    header, raw_moves = ocr.process_scoresheet(contents)

    if file2 is not None:
        if file2.content_type not in ACCEPTED_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type for page 2: {file2.content_type}")
        contents2 = await file2.read()
        if len(contents2) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="Page 2 too large. Maximum size is 10 MB.")

        moves_page2 = ocr.process_second_page(contents2)
        raw_moves = _merge_pages(raw_moves, moves_page2)

    moves_dto = parser.parse_scoresheet(header, raw_moves)

    return ScoresheetDTO(
        filename=file.filename,
        white=moves_dto["header"].white,
        white_elo=moves_dto["header"].white_elo,
        black=moves_dto["header"].black,
        black_elo=moves_dto["header"].black_elo,
        date=moves_dto["header"].date,
        tournament=moves_dto["header"].tournament,
        lang=moves_dto["ui_lang"],
        moves=moves_dto["moves"],
        status="success",
    )


def _merge_pages(page1_moves: list[str], page2_moves: list[str]) -> list[str]:
    """Concatenate moves from both pages; _sort_and_strip_move_numbers will order them."""
    from app.services.ocr_service import sort_and_strip_move_numbers
    return sort_and_strip_move_numbers(page1_moves + page2_moves)
