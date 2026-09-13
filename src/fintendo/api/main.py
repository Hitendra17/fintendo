from fastapi import FastAPI

from fintendo.api.router import api_router
from fintendo.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Fintendo Research API",
        description=(
            "Backend API for Fintendo's multi-agent financial "
            "research system."
        ),
        version="0.1.0",
    )

    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()