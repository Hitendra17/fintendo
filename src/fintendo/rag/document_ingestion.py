from fintendo.rag.document_fetcher import DocumentFetcher
from fintendo.rag.document_extractor import DocumentTextExtractor
from fintendo.rag.models import RAGDocument
from fintendo.rag.sources.models import DiscoveredDocument


class DiscoveredDocumentIngestionService:
    def __init__(
        self,
        fetcher: DocumentFetcher,
        extractor: DocumentTextExtractor,
    ) -> None:
        self.fetcher = fetcher
        self.extractor = extractor

    def ingest(
        self,
        discovered_document: DiscoveredDocument,
    ) -> RAGDocument:
        fetched = self.fetcher.fetch(
            str(discovered_document.url)
        )

        content, extracted_title = self.extractor.extract(
            fetched
        )

        title = (
            discovered_document.title
            or extracted_title
        )

        return RAGDocument(
            document_id=self._document_id(
                str(discovered_document.url)
            ),
            title=title,
            content=content,
            source=discovered_document.source,
            source_url=discovered_document.url,
            ticker=discovered_document.ticker,
            document_type=(
                discovered_document.document_type.value
            ),
            published_at=(
                discovered_document.published_at
            ),
        )

    @staticmethod
    def _document_id(url: str) -> str:
        import hashlib

        return hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()