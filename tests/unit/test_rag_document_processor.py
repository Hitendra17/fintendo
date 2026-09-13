from fintendo.rag.chunker import TextChunker
from fintendo.rag.document_processor import RAGDocumentProcessor
from fintendo.rag.models import RAGDocument


def test_document_processor_creates_chunks():
    document = RAGDocument(
        document_id="doc-001",
        title="Reliance Earnings",
        content="a" * 250,
        source="Reliance Investor Relations",
        ticker="RELIANCE",
        document_type="earnings",
    )

    processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=100,
            overlap=20,
        )
    )

    chunks = processor.process(document)

    assert len(chunks) == 3
    assert chunks[0].chunk_id == "doc-001-chunk-0"
    assert chunks[1].chunk_id == "doc-001-chunk-1"
    assert chunks[1].document_id == "doc-001"
    assert chunks[1].ticker == "RELIANCE"


def test_document_processor_preserves_metadata():
    document = RAGDocument(
        document_id="doc-002",
        title="Reliance Annual Report",
        content="This is some financial information " * 20,
        source="Reliance Investor Relations",
        source_url="https://example.com/report",
        ticker="RELIANCE",
        document_type="annual_report",
    )

    processor = RAGDocumentProcessor(
        TextChunker(
            chunk_size=100,
            overlap=20,
        )
    )

    chunks = processor.process(document)

    assert chunks
    assert all(
        chunk.title == "Reliance Annual Report"
        for chunk in chunks
    )
    assert all(
        chunk.document_type == "annual_report"
        for chunk in chunks
    )
    assert all(
        chunk.source == "Reliance Investor Relations"
        for chunk in chunks
    )