from qdrant_client import QdrantClient

from fintendo.rag.embeddings import EmbeddingProvider
from fintendo.rag.models import RAGChunk
from fintendo.rag.qdrant import QdrantRAGRetriever


class FakeEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        if "revenue" in text.lower():
            return [1.0, 0.0, 0.0, 0.0]

        return [0.0, 1.0, 0.0, 0.0]


def make_chunk() -> RAGChunk:
    return RAGChunk(
        chunk_id="doc-1-chunk-0",
        document_id="doc-1",
        chunk_index=0,
        title="Reliance revenue growth",
        content="Reliance reported strong revenue growth.",
        source="Test Source",
        ticker="RELIANCE",
        document_type="earnings",
    )


def test_qdrant_retriever_adds_and_searches_chunks():
    client = QdrantClient(":memory:")
    embedding_provider = FakeEmbeddingProvider()

    retriever = QdrantRAGRetriever(
        client=client,
        embedding_provider=embedding_provider,
        collection_name="test_collection",
    )

    retriever.initialize_collection(vector_size=4)

    chunk = make_chunk()

    retriever.add_documents([chunk])

    results = retriever.search(
        query="Reliance revenue growth",
        ticker="RELIANCE",
    )

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "doc-1-chunk-0"
    assert results[0].chunk.document_id == "doc-1"
    assert results[0].chunk.ticker == "RELIANCE"
    assert results[0].score > 0


def test_qdrant_retriever_rejects_invalid_input():
    client = QdrantClient(":memory:")
    embedding_provider = FakeEmbeddingProvider()

    retriever = QdrantRAGRetriever(
        client=client,
        embedding_provider=embedding_provider,
        collection_name="test_collection",
    )

    retriever.initialize_collection(vector_size=4)

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