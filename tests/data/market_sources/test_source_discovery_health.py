import pytest

from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.models import MarketDiscoveryMethod
from fintendo.data.market_sources.registry import get_global_market_sources
from fintendo.data.market_sources.rss_discovery import (
    RSSMarketSourceDiscovery,
)
from fintendo.data.market_sources.web_discovery import (
    WebPageMarketSourceDiscovery,
)


TEST_PROFILE = CompanyProfile(
    ticker="INFY",
    company_name="Infosys",
    exchange="NSE",
    official_website="https://www.infosys.com",
)


@pytest.mark.integration
def test_registered_market_sources_are_discoverable() -> None:
    sources = get_global_market_sources()

    web_discovery = WebPageMarketSourceDiscovery()
    rss_discovery = RSSMarketSourceDiscovery()

    failures: list[str] = []

    for source in sources:
        try:
            if source.discovery_method == MarketDiscoveryMethod.WEB_PAGE:
                urls = web_discovery.discover(
                    profile=TEST_PROFILE,
                    source=source,
                )

            elif source.discovery_method == MarketDiscoveryMethod.RSS:
                urls = rss_discovery.discover(
                    profile=TEST_PROFILE,
                    source=source,
                )

            else:
                failures.append(
                    f"{source.name}: unsupported discovery method "
                    f"{source.discovery_method}"
                )
                continue

            print(
                f"\n{source.name}"
                f"\n  method: {source.discovery_method.value}"
                f"\n  discovered URLs: {len(urls)}"
            )

            for url in urls[:5]:
                print(f"  - {url}")

        except Exception as exc:
            failures.append(
                f"{source.name}: "
                f"{type(exc).__name__}: {exc}"
            )

    if failures:
        pytest.fail(
            "Market source discovery failures:\n"
            + "\n".join(f"- {failure}" for failure in failures)
        )