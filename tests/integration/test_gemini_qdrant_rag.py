import uuid

import pytest
from qdrant_client import QdrantClient

from fintendo.core.config import settings
from fintendo.rag.chunker import TextChunker
from fintendo.rag.document_processor import RAGDocumentProcessor
from fintendo.rag.gemini_embeddings import GeminiEmbeddingProvider
from fintendo.rag.ingestion import RAGIngestionService
from fintendo.rag.models import RAGDocument
from fintendo.rag.qdrant import QdrantRAGRetriever


@pytest.mark.integration
def test_real_gemini_qdrant_rag():
    if not settings.gemini_api_key:
        pytest.skip("Gemini API key is not configured.")

    client = QdrantClient(
        url="http://localhost:6333"
    )

    collection_name = (
        f"test_fintendo_rag_{uuid.uuid4().hex}"
    )

    embedding_provider = GeminiEmbeddingProvider()

    retriever = QdrantRAGRetriever(
        client=client,
        embedding_provider=embedding_provider,
        collection_name=collection_name,
    )

    retriever.initialize_collection(
        vector_size=GeminiEmbeddingProvider.OUTPUT_DIMENSIONALITY
    )

    processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=1000,
            overlap=200,
        )
    )

    ingestion_service = RAGIngestionService(
        document_processor=processor,
        retriever=retriever,
    )

    document = RAGDocument(
        document_id="reliance-test-001",
        title="Reliance Financial Performance",
        content=(
            "Reliance Industries reported strong revenue growth "
            "during the period. The company continued to invest "
            "in its digital services business and telecommunications "
            "infrastructure. Strong operating performance and "
            "continued investment were important factors in the "
            "company's financial outlook. "
        )
        * 10,
        source="Test Financial Document",
        ticker="RELIANCE",
        document_type="financial_report",
    )

    try:
        ingestion_service.ingest(document)

        results = retriever.search(
            query="Reliance revenue growth and financial performance",
            ticker="RELIANCE",
            top_k=3,
        )

        assert results
        assert results[0].chunk.document_id == "reliance-test-001"
        assert results[0].chunk.ticker == "RELIANCE"
        assert results[0].chunk.content
        assert results[0].score > 0

    finally:
        client.delete_collection(
            collection_name=collection_name
        )