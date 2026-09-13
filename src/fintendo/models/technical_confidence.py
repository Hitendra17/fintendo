from pydantic import BaseModel, Field


class TechnicalConfidence(BaseModel):
    score: float = Field(ge=0, le=1)

    observations: int = Field(ge=1)

    history_score: float = Field(ge=0, le=1)
    trend_score: float = Field(ge=0, le=1)
    momentum_score: float = Field(ge=0, le=1)
    volatility_score: float = Field(ge=0, le=1)
    levels_score: float = Field(ge=0, le=1)

    missing_indicators: list[str]
    limitations: list[str]