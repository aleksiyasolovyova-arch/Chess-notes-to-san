from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_validation_service
from app.api.dtos.validation_dto import ValidateRequestDTO, ValidateResponseDTO, MoveValidationResultDTO

from app.services.validation_service import ValidationService

router = APIRouter(prefix="/api/validate", tags=["validation"])

@router.post("", response_model=ValidateResponseDTO)
async def validate_moves(body: ValidateRequestDTO, service: ValidationService = Depends(get_validation_service)):
    try:
        result = service.validate_moves(body.moves, lang=body.lang)
        return ValidateResponseDTO(
            all_legal=result["all_legal"],
            moves=[
                MoveValidationResultDTO(**m)
                for m in result["moves"]
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
