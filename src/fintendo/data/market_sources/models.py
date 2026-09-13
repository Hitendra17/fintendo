from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class MarketSourceType(StrEnum):
    COMPANY = "company"
    NEWS = "news"
    REGULATORY = "regulatory"


class MarketDiscoveryMethod(StrEnum):
    WEB_PAGE = "web_page"
    RSS = "rss"


class MarketSource(BaseModel):
    name: str = Field(min_length=1)
    source_type: MarketSourceType
    discovery_method: MarketDiscoveryMethod
    url: HttpUrl
    description: str = Field(min_length=1)
    enabled: bool = True


