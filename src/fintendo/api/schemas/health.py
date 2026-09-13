from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    gemini_configured: bool
    version: str