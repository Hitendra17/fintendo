from fintendo.rag.chunker import TextChunker
from fintendo.rag.document_processor import RAGDocumentProcessor
from fintendo.rag.ingestion import RAGIngestionService
from fintendo.rag.in_memory import InMemoryRAGRetriever
from fintendo.rag.models import RAGDocument


def test_rag_ingestion_processes_and_stores_document():
    document = RAGDocument(
        document_id="doc-001",
        title="Reliance Earnings",
        content="Reliance reported strong revenue growth. " * 20,
        source="Test Source",
        ticker="RELIANCE",
        document_type="earnings",
    )

    processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=100,
            overlap=20,
        )
    )

    retriever = InMemoryRAGRetriever()

    service = RAGIngestionService(
        document_processor=processor,
        retriever=retriever,
    )

    service.ingest(document)

    results = retriever.search(
        query="Reliance revenue growth",
        ticker="RELIANCE",
        top_k=5,
    )

    assert results
    assert all(
        result.chunk.document_id == "doc-001"
        for result in results
    )


def test_rag_ingestion_handles_document_with_multiple_chunks():
    document = RAGDocument(
        document_id="doc-002",
        title="Reliance Annual Report",
        content="Financial performance information. " * 100,
        source="Test Source",
        ticker="RELIANCE",
        document_type="annual_report",
    )

    processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=100,
            overlap=20,
        )
    )

    retriever = InMemoryRAGRetriever()

    service = RAGIngestionService(
        document_processor=processor,
        retriever=retriever,
    )

    service.ingest(document)

    assert len(retriever.chunks) > 1
    assert all(
        chunk.document_id == "doc-002"
        for chunk in retriever.chunks
    )