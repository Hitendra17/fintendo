from datetime import datetime

from pydantic import BaseModel, Field


class FundamentalSnapshot(BaseModel):
    ticker: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    as_of: datetime

    # Latest financial values
    revenue: float | None = None
    operating_income: float | None = None
    net_income: float | None = None

    total_assets: float | None = None
    stockholders_equity: float | None = None
    total_debt: float | None = None
    current_assets: float | None = None
    current_liabilities: float | None = None

    operating_cash_flow: float | None = None
    capital_expenditure: float | None = None
    free_cash_flow: float | None = None

    # Growth
    revenue_yoy_growth: float | None = None
    net_income_yoy_growth: float | None = None

    revenue_cagr: float | None = None
    net_income_cagr: float | None = None

    # Profitability
    operating_margin: float | None = None
    net_income_margin: float | None = None
    return_on_equity: float | None = None
    return_on_assets: float | None = None

    # Cash flow quality
    operating_cash_flow_margin: float | None = None
    free_cash_flow_margin: float | None = None
    free_cash_flow_growth: float | None = None
    free_cash_flow_conversion: float | None = None

    # Balance sheet
    debt_to_equity: float | None = None
    current_ratio: float | None = None
    net_debt_to_operating_income: float | None = None