from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
    MarketSourceType,
)


GLOBAL_MARKET_SOURCES: list[MarketSource] = [
    MarketSource(
        name="SEBI Corporate Filings",
        source_type=MarketSourceType.REGULATORY,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.sebi.gov.in/curation/corporate_filings.html",
        description="SEBI corporate filing and regulatory disclosure information.",
    ),
    MarketSource(
        name="Economic Times",
        source_type=MarketSourceType.NEWS,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://economictimes.indiatimes.com/",
        description=(
            "Indian business and financial news covering companies, "
            "markets, industries, and the economy."
        ),
    ),
    
    MarketSource(
        name="Mint",
        source_type=MarketSourceType.NEWS,
        discovery_method=MarketDiscoveryMethod.RSS,
        url="https://www.livemint.com/rss/markets",
        description=(
            "Financial and business news covering Indian markets, "
            "companies, industries, and economic developments."
        ),
    ),
    MarketSource(
        name="CNBC TV18",
        source_type=MarketSourceType.NEWS,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.cnbctv18.com/",
        description=(
            "Indian business and financial news covering markets, "
            "companies, and economic developments."
        ),
    ),
    MarketSource(
        name="Google News",
        source_type=MarketSourceType.NEWS,
        discovery_method=MarketDiscoveryMethod.RSS,
        url="https://news.google.com/",
        description=(
            "News discovery source used to identify potentially relevant "
            "current articles from external publishers."
        ),
    ),
]


def get_global_market_sources() -> list[MarketSource]:
    return GLOBAL_MARKET_SOURCES.copy()