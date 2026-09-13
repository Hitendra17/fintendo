from pydantic import BaseModel, Field, HttpUrl


class CompanyProfile(BaseModel):
    ticker: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    official_website: HttpUrl | None = None
    investor_relations_url: HttpUrl | None = None
    sectors: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)