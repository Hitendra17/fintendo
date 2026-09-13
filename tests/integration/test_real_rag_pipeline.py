import uuid

import pytest
from qdrant_client import QdrantClient

from fintendo.rag.chunker import TextChunker
from fintendo.rag.document_extractor import DocumentTextExtractor
from fintendo.rag.document_fetcher import DocumentFetcher
from fintendo.rag.document_ingestion import (
    DiscoveredDocumentIngestionService,
)
from fintendo.rag.document_processor import RAGDocumentProcessor
from fintendo.rag.embedding_factory import get_embedding_provider
from fintendo.rag.ingestion import RAGIngestionService
from fintendo.rag.pdf_extractor import PDFTextExtractor
from fintendo.rag.qdrant import QdrantRAGRetriever
from fintendo.rag.pipeline import RAGPipeline


@pytest.mark.integration
def test_real_hdfcbank_rag_pipeline():
    ticker = "HDFCBANK"
    collection_name = f"test_fintendo_real_{uuid.uuid4().hex}"

    print("\n[1] Creating Qdrant client...")
    client = QdrantClient(
        url="http://localhost:6333"
    )

    print("[2] Loading embedding provider...")
    embedding_provider = get_embedding_provider()

    print("[3] Testing embedding...")
    vector_size = len(
        embedding_provider.embed(
            "financial report"
        )
    )
    print(f"[4] Embedding works. Vector size: {vector_size}")

    retriever = QdrantRAGRetriever(
        client=client,
        embedding_provider=embedding_provider,
        collection_name=collection_name,
    )

    retriever.initialize_collection(
        vector_size=vector_size
    )
    print("[5] Qdrant collection initialized.")

    document_processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=1000,
            overlap=200,
        )
    )

    rag_ingestion = RAGIngestionService(
        document_processor=document_processor,
        retriever=retriever,
    )

    document_ingestion = DiscoveredDocumentIngestionService(
        fetcher=DocumentFetcher(),
        extractor=DocumentTextExtractor(
            pdf_extractor=PDFTextExtractor()
        ),
    )

    pipeline = RAGPipeline(
        document_ingestion=document_ingestion,
        rag_ingestion=rag_ingestion,
    )

    try:
        print("[6] Starting RAG pipeline...")

        count = pipeline.ingest_ticker(
            ticker,
            max_documents=1,
        )

        print(
            f"[7] Ingested {count} documents for {ticker}."
        )

        assert count > 0

        print("[8] Starting Qdrant retrieval...")

        results = retriever.search(
            query=(
                "HDFC Bank financial performance "
                "profitability revenue business outlook"
            ),
            ticker=ticker,
            top_k=3,
        )

        print(
            f"[9] Retrieved {len(results)} results."
        )

        assert results

        assert all(
            result.chunk.ticker == ticker
            for result in results
        )

        assert all(
            result.chunk.content.strip()
            for result in results
        )

        print("[10] RAG pipeline test completed successfully.")

    finally:
        client.delete_collection(
            collection_name=collection_name
        )