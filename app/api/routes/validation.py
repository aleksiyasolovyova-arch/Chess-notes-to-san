from fastapi import APIRouter, Depends

from app.api.dependencies import get_validation_service
from app.api.dtos.validation_dto import ValidateRequestDTO, ValidateResponseDTO, MoveValidationResultDTO

from app.services.validation_service import ValidationService

router = APIRouter(prefix="/api/validate", tags=["validation"])

#TODO: some kind of exception handling, idk if here
@router.post("", response_model=ValidateResponseDTO)
async def validate_moves(body: ValidateRequestDTO, service: ValidationService = Depends(get_validation_service)):
    result = service.validate_moves(body.moves, lang=body.lang)
    return ValidateResponseDTO(
        all_legal=result["all_legal"],
        moves=[
            MoveValidationResultDTO(**m)
            for m in result["moves"]
        ],
    )
