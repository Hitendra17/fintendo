from datetime import datetime, timezone

from fintendo.rag.models import RAGChunk, RAGDocument, RAGSearchResult


def make_document() -> RAGDocument:
    return RAGDocument(
        document_id="doc-1",
        title="Reliance Annual Report",
        content="Reliance reported strong financial performance.",
        source="Test Source",
        source_url="https://example.com/report",
        ticker="RELIANCE",
        document_type="annual_report",
        published_at=datetime.now(timezone.utc),
    )


def make_chunk() -> RAGChunk:
    document = make_document()

    return RAGChunk(
        chunk_id="doc-1-chunk-0",
        document_id=document.document_id,
        chunk_index=0,
        content=document.content,
        title=document.title,
        source=document.source,
        source_url=document.source_url,
        ticker=document.ticker,
        document_type=document.document_type,
        published_at=document.published_at,
    )


def test_rag_document_creation():
    document = make_document()

    assert document.document_id == "doc-1"
    assert document.ticker == "RELIANCE"
    assert document.document_type == "annual_report"


def test_rag_chunk_creation():
    chunk = make_chunk()

    assert chunk.chunk_id == "doc-1-chunk-0"
    assert chunk.document_id == "doc-1"
    assert chunk.chunk_index == 0
    assert chunk.ticker == "RELIANCE"


def test_rag_search_result_creation():
    chunk = make_chunk()

    result = RAGSearchResult(
        chunk=chunk,
        score=0.92,
    )

    assert result.chunk.chunk_id == "doc-1-chunk-0"
    assert result.score == 0.92