from pydantic import BaseModel, Field


class CompanySearchResult(BaseModel):
    ticker: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    sector: str | None = None