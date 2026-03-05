from fastapi import APIRouter

from .health import router as health_router
from .scoresheet import router as scoresheet_router
from .validation import router as validation_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(scoresheet_router)
api_router.include_router(validation_router)