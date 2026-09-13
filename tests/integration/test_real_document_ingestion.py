import pytest

from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.market_client import MarketDataClient
from fintendo.rag.document_extractor import DocumentTextExtractor
from fintendo.rag.document_fetcher import DocumentFetcher
from fintendo.rag.pdf_extractor import PDFTextExtractor
from fintendo.rag.sources.factory import get_document_discovery_source


@pytest.mark.integration
def test_real_reliance_document_ingestion():
    ticker = "RELIANCE"

    market_data_client = MarketDataClient()
    profile_resolver = CompanyProfileResolver(market_data_client)

    profile = profile_resolver.resolve(ticker)

    discovery_source = get_document_discovery_source(ticker)
    documents = discovery_source.discover(profile)

    assert documents

    document = documents[0]

    print("\nTesting document:")
    print(f"Title: {document.title}")
    print(f"URL: {document.url}")

    fetcher = DocumentFetcher()
    extractor = DocumentTextExtractor(
        pdf_extractor=PDFTextExtractor()
    )

    fetched = fetcher.fetch(str(document.url))

    print(f"Content type: {fetched.content_type}")
    print(f"Downloaded bytes: {len(fetched.content):,}")

    text, title = extractor.extract(fetched)

    print(f"Extracted title: {title}")
    print(f"Extracted characters: {len(text):,}")

    assert fetched.content
    assert fetched.content_type == "application/pdf"
    assert text.strip()
    assert len(text) > 1000