from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.rag.document_ingestion import (
    DiscoveredDocumentIngestionService,
)
from fintendo.rag.ingestion import RAGIngestionService
from fintendo.rag.sources.discovery import DocumentDiscoverySource
from fintendo.rag.sources.factory import get_document_discovery_source


class RAGPipeline:
    """
    End-to-end company-agnostic RAG ingestion pipeline.
    """

    def __init__(
        self,
        document_ingestion: DiscoveredDocumentIngestionService,
        rag_ingestion: RAGIngestionService,
        profile_resolver: CompanyProfileResolver | None = None,
        discovery_source: DocumentDiscoverySource | None = None,
    ) -> None:
        self.document_ingestion = document_ingestion
        self.rag_ingestion = rag_ingestion
        self.profile_resolver = (
            profile_resolver or CompanyProfileResolver()
        )
        self.discovery_source = discovery_source

    def ingest_ticker(
        self,
        ticker: str,
        max_documents: int | None = None,
    ) -> int:
        if not ticker.strip():
            raise ValueError("Ticker cannot be empty.")

        if max_documents is not None and max_documents <= 0:
            raise ValueError(
                "max_documents must be positive when provided."
            )

        profile = self.profile_resolver.resolve(ticker)

        discovery_source = (
            self.discovery_source
            or get_document_discovery_source(profile)
        )

        discovered_documents = discovery_source.discover(profile)

        if max_documents is not None:
            discovered_documents = discovered_documents[:max_documents]

        ingested_count = 0

        for discovered_document in discovered_documents:
            try:
                rag_document = self.document_ingestion.ingest(
                    discovered_document
                )
                self.rag_ingestion.ingest(rag_document)
                ingested_count += 1
            except (ValueError, RuntimeError):
                continue

        return ingested_count