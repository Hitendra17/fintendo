from fastapi import APIRouter

from fintendo.api.routes.v1.companies import router as companies_router
from fintendo.api.routes.v1.health import router as health_router
from fintendo.api.routes.v1.research import router as research_router


router = APIRouter()

router.include_router(health_router)
router.include_router(research_router)
router.include_router(companies_router)