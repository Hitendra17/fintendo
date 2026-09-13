from datetime import datetime
import math

from pydantic import BaseModel, Field, field_validator


class TechnicalSnapshot(BaseModel):
    ticker: str = Field(min_length=1)
    as_of: datetime
    observations: int = Field(ge=1)

    close: float = Field(gt=0)

    sma_20: float | None = None
    sma_50: float | None = None

    ema_20: float | None = None
    ema_50: float | None = None

    rsi_14: float | None = Field(default=None, ge=0, le=100)

    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None

    support_levels: list[float]
    resistance_levels: list[float]

    volatility_20d: float | None = Field(default=None, ge=0)

    price_vs_sma_20_pct: float | None = None
    price_vs_sma_50_pct: float | None = None

    price_vs_ema_20_pct: float | None = None
    price_vs_ema_50_pct: float | None = None

    macd_spread: float | None = None

    distance_to_support_pct: float | None = None
    distance_to_resistance_pct: float | None = None

    @field_validator(
        "close",
        "sma_20",
        "sma_50",
        "ema_20",
        "ema_50",
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_histogram",
        "volatility_20d",
        "price_vs_sma_20_pct",
        "price_vs_sma_50_pct",
        "price_vs_ema_20_pct",
        "price_vs_ema_50_pct",
        "macd_spread",
        "distance_to_support_pct",
        "distance_to_resistance_pct",
    )
    @classmethod
    def validate_finite(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("Numeric values must be finite.")
        return value

    @field_validator("support_levels", "resistance_levels")
    @classmethod
    def validate_level_values(cls, values: list[float]) -> list[float]:
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Support and resistance levels must be finite.")
        return values