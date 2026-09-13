import pytest

from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.market_client import MarketDataClient
from fintendo.rag.sources.factory import get_document_discovery_source


@pytest.mark.integration
def test_real_reliance_source_discovery():
    ticker = "RELIANCE"

    market_data_client = MarketDataClient()
    profile_resolver = CompanyProfileResolver(market_data_client)

    profile = profile_resolver.resolve(ticker)

    source = get_document_discovery_source(ticker)
    documents = source.discover(profile)

    assert documents

    for document in documents:
        assert document.url
        assert document.title