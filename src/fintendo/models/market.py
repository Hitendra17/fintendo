from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class MarketBar(BaseModel):
    ticker: str = Field(min_length=1)
    timestamp: datetime

    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float

    @model_validator(mode="after")
    def validate_ohlcv(self):
        if self.high < max(self.open, self.close):
            raise ValueError("High must be greater than or equal to open and close.")

        if self.low > min(self.open, self.close):
            raise ValueError("Low must be less than or equal to open and close.")

        if self.volume < 0:
            raise ValueError("Volume cannot be negative.")

        return self

class FinancialSnapshot(BaseModel):
    ticker: str = Field(min_length=1)
    company_name: str = Field(min_length=1)

    market_cap: float | None = None
    revenue: float | None = None
    net_income: float | None = None
    operating_cash_flow: float | None = None
    free_cash_flow: float | None = None

    revenue_growth: float | None = None
    earnings_growth: float | None = None

    profit_margin: float | None = None
    operating_margin: float | None = None
    return_on_equity: float | None = None
    return_on_assets: float | None = None

    debt_to_equity: float | None = None
    current_ratio: float | None = None

    trailing_pe: float | None = None
    price_to_book: float | None = None

    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None

    as_of: datetime