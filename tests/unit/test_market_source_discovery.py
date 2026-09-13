from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
    MarketSourceType,
)
from fintendo.data.market_sources.web_discovery import (
    WebPageMarketSourceDiscovery,
)


class FakeFetchedPage:
    def __init__(
        self,
        content: str,
        url: str,
    ) -> None:
        self.content = content
        self.url = url


class FakeWebFetcher:
    def fetch(
        self,
        url: str,
    ) -> FakeFetchedPage:
        return FakeFetchedPage(
            content="""
            <html>
                <body>
                    <a href="/announcement-123">
                        HDFC Bank announces quarterly results
                    </a>

                    <a href="/investors">
                        Investors
                    </a>

                    <a href="https://example.com/external">
                        HDFC Bank announcement
                    </a>

                    <a href="/board-of-directors">
                        Board of Directors
                    </a>

                    <a href="/contact">
                        Contact Us
                    </a>
            </body>
            </html>
            """,
            url=url,
        )


def test_web_discovery_finds_relevant_same_domain_links() -> None:
    profile = CompanyProfile(
        ticker="HDFCBANK",
        company_name="HDFC Bank Limited",
        exchange="NSI",
        official_website="https://www.hdfc.bank.in",
    )

    source = MarketSource(
        name="HDFC Bank",
        source_type=MarketSourceType.COMPANY,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.hdfc.bank.in/investor-relations",
        description="Company investor-relations page.",
    )

    discovery = WebPageMarketSourceDiscovery(
        web_fetcher=FakeWebFetcher()
    )

    results = discovery.discover(
        profile,
        source,
    )

    assert results == [
        "https://www.hdfc.bank.in/announcement-123"
    ]


def test_web_discovery_rejects_external_domains() -> None:
    profile = CompanyProfile(
        ticker="HDFCBANK",
        company_name="HDFC Bank Limited",
        exchange="NSI",
        official_website="https://www.hdfc.bank.in",
    )

    source = MarketSource(
        name="HDFC Bank",
        source_type=MarketSourceType.COMPANY,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.hdfc.bank.in/investor-relations",
        description="Company investor-relations page.",
    )

    discovery = WebPageMarketSourceDiscovery(
        web_fetcher=FakeWebFetcher()
    )

    results = discovery.discover(
        profile,
        source,
    )

    assert all(
        "example.com" not in url
        for url in results
    )


def test_web_discovery_rejects_navigation_pages() -> None:
    profile = CompanyProfile(
        ticker="HDFCBANK",
        company_name="HDFC Bank Limited",
        exchange="NSI",
        official_website="https://www.hdfc.bank.in",
    )

    source = MarketSource(
        name="HDFC Bank",
        source_type=MarketSourceType.COMPANY,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.hdfc.bank.in/investor-relations",
        description="Company investor-relations page.",
    )

    discovery = WebPageMarketSourceDiscovery(
        web_fetcher=FakeWebFetcher()
    )

    results = discovery.discover(
        profile,
        source,
    )

    assert "https://www.hdfc.bank.in/investors" not in results
    assert "https://www.hdfc.bank.in/contact" not in results
    assert "https://www.hdfc.bank.in/board-of-directors" not in results