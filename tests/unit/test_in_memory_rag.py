from fintendo.rag.in_memory import InMemoryRAGRetriever
from fintendo.rag.models import RAGChunk


def make_chunk(
    document_id: str,
    title: str,
    content: str,
    ticker: str = "RELIANCE",
) -> RAGChunk:
    return RAGChunk(
        chunk_id=f"{document_id}-chunk-0",
        document_id=document_id,
        chunk_index=0,
        title=title,
        content=content,
        source="Test Source",
        ticker=ticker,
        document_type="earnings",
    )


def test_retriever_returns_relevant_documents():
    retriever = InMemoryRAGRetriever()

    retriever.add_documents(
        [
            make_chunk(
                "doc-1",
                "Reliance revenue growth",
                "Reliance reported strong revenue growth.",
            ),
            make_chunk(
                "doc-2",
                "Reliance telecom investment",
                "Reliance announced a major telecom investment.",
            ),
            make_chunk(
                "doc-3",
                "Unrelated document",
                "This document discusses something else entirely.",
                ticker="TCS",
            ),
        ]
    )

    results = retriever.search(
        query="reliance revenue growth",
        ticker="RELIANCE",
        top_k=5,
    )

    assert len(results) == 2
    assert results[0].chunk.document_id == "doc-1"
    assert results[0].score == 1.0


def test_retriever_respects_top_k():
    retriever = InMemoryRAGRetriever()

    retriever.add_documents(
        [
            make_chunk(
                f"doc-{i}",
                f"Reliance revenue report {i}",
                "Reliance revenue growth report.",
            )
            for i in range(5)
        ]
    )

    results = retriever.search(
        query="reliance revenue",
        ticker="RELIANCE",
        top_k=2,
    )

    assert len(results) == 2


def test_retriever_returns_empty_for_no_match():
    retriever = InMemoryRAGRetriever()

    retriever.add_documents(
        [
            make_chunk(
                "doc-1",
                "Reliance revenue growth",
                "Reliance reported strong revenue growth.",
            )
        ]
    )

    results = retriever.search(
        query="banking credit losses",
        ticker="RELIANCE",
        top_k=5,
    )

    assert results == []


def test_retriever_rejects_invalid_input():
    retriever = InMemoryRAGRetriever()

    for query, ticker, top_k in [
        ("", "RELIANCE", 5),
        ("revenue", "", 5),
        ("revenue", "RELIANCE", 0),
    ]:
        try:
            retriever.search(
                query=query,
                ticker=ticker,
                top_k=top_k,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError")