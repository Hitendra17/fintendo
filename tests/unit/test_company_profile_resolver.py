from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.market_client import MarketDataClient


class FakeMarketDataClient:
    def get_company_metadata(self, ticker: str) -> dict:
        return {
            "ticker": ticker,
            "company_name": "Test Company",
            "exchange": "NSI",
            "official_website": "https://example.com",
            "investor_relations_url": None,
            "sector": "Technology",
            "industry": "Software",
        }


def test_resolver_builds_company_profile() -> None:
    resolver = CompanyProfileResolver(
        market_data=FakeMarketDataClient()
    )

    profile = resolver.resolve("test")

    assert profile.ticker == "TEST"
    assert profile.company_name == "Test Company"
    assert profile.exchange == "NSI"
    assert str(profile.official_website) == "https://example.com/"
    assert profile.sectors == ["Technology", "Software"]


def test_resolver_rejects_empty_ticker() -> None:
    resolver = CompanyProfileResolver(
        market_data=FakeMarketDataClient()
    )

    try:
        resolver.resolve("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Ticker must not be empty." in str(exc)