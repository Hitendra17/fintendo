from fastapi import FastAPI

from fintendo.core.config import settings


app = FastAPI(
    title="Fintendo",
    description="Agentic quantitative research and trading platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "fintendo",
        "environment": settings.environment,
    }