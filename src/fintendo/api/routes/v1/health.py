from fastapi import APIRouter

from fintendo.api.schemas.health import HealthResponse
from fintendo.core.config import settings


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        gemini_configured=bool(
            settings.gemini_api_key.strip()
        ),
        version="0.1.0",
    )