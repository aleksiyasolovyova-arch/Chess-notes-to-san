from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import PlainTextResponse

from app.api.dependencies import get_validation_service
from app.api.dtos.scoresheet_dto import PGNRequestDTO
from app.api.dtos.validation_dto import ValidateRequestDTO, ValidateResponseDTO, MoveValidationResultDTO
from app.domain.notation import detect_notation_language, translate_batch
from app.domain.parser.pgn import to_pgn
from app.domain.scoresheet import ScoresheetHeader

from app.services.validation_service import ValidationService

router = APIRouter(prefix="/api/validate", tags=["validation"])

@router.post("", response_model=ValidateResponseDTO)
async def validate_moves(body: ValidateRequestDTO, service: ValidationService = Depends(get_validation_service)):
    try:
        notation_lang = detect_notation_language(body.moves)
        result = service.validate_moves(
            body.moves,
            notation_lang=notation_lang,
            ui_lang=body.ui_lang,
        )
        return ValidateResponseDTO(
            legal=result["all_legal"],
            moves=[MoveValidationResultDTO(**m) for m in result["moves"]],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pgn", response_class=PlainTextResponse)
async def export_pgn(body: PGNRequestDTO):
    if not body.moves:
        raise HTTPException(status_code=400, detail="No moves provided")

    header = ScoresheetHeader(
        white=body.white or "Unknown",
        white_elo=0,
        black=body.black or "Unknown",
        black_elo=0,
        date=body.date or "",
        tournament=body.tournament or "",
        lang="en",
    )

    notation_lang = detect_notation_language(body.moves)
    english_san = translate_batch(body.moves, notation_lang)

    pgn = to_pgn(header, english_san)
    return pgn