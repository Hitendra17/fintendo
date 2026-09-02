import logging

from fastapi import FastAPI

from fintendo.core.config import settings
from fintendo.core.logging import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Fintendo",
    description="Agentic quantitative research and trading platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "fintendo",
        "environment": settings.environment,
    }