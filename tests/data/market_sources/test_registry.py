from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSourceType,
)
from fintendo.data.market_sources.registry import (
    GLOBAL_MARKET_SOURCES,
    get_global_market_sources,
)


def test_global_market_sources_are_registered() -> None:
    sources = get_global_market_sources()

    assert len(sources) >= 1
    assert sources == GLOBAL_MARKET_SOURCES


def test_global_market_sources_have_valid_metadata() -> None:
    sources = get_global_market_sources()

    for source in sources:
        assert source.name.strip()
        assert source.description.strip()
        assert source.url
        assert source.enabled is True
        assert source.source_type in MarketSourceType
        assert source.discovery_method in MarketDiscoveryMethod


def test_global_market_source_names_are_unique() -> None:
    sources = get_global_market_sources()

    names = [source.name for source in sources]

    assert len(names) == len(set(names))


def test_global_market_source_urls_are_unique() -> None:
    sources = get_global_market_sources()

    urls = [str(source.url) for source in sources]

    assert len(urls) == len(set(urls))


def test_global_market_sources_use_supported_discovery_methods() -> None:
    sources = get_global_market_sources()

    supported_methods = {
        MarketDiscoveryMethod.WEB_PAGE,
        MarketDiscoveryMethod.RSS,
    }

    for source in sources:
        assert source.discovery_method in supported_methods


def test_get_global_market_sources_returns_a_copy() -> None:
    sources = get_global_market_sources()

    assert sources is not GLOBAL_MARKET_SOURCES

    original_length = len(GLOBAL_MARKET_SOURCES)
    sources.pop()

    assert len(GLOBAL_MARKET_SOURCES) == original_length