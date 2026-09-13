from fintendo.rag.sources.discovery import DocumentDiscoverySource
from fintendo.rag.sources.models import DiscoveredDocument, DocumentType


class FakeDocumentDiscoverySource(DocumentDiscoverySource):
    def discover(self, ticker: str) -> list[DiscoveredDocument]:
        return [
            DiscoveredDocument(
                url="https://example.com/reliance-annual-report.pdf",
                title="Reliance Annual Report",
                source="Test Source",
                document_type=DocumentType.ANNUAL_REPORT,
                ticker=ticker,
            )
        ]


def test_document_discovery_source_returns_documents():
    source = FakeDocumentDiscoverySource()

    documents = source.discover("RELIANCE")

    assert len(documents) == 1
    assert documents[0].ticker == "RELIANCE"
    assert documents[0].document_type == DocumentType.ANNUAL_REPORT


def test_document_discovery_source_is_an_abstraction():
    source = FakeDocumentDiscoverySource()

    assert isinstance(source, DocumentDiscoverySource)