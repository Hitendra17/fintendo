import uuid

from qdrant_client import QdrantClient

from fintendo.rag.embeddings import EmbeddingProvider
from fintendo.rag.models import RAGChunk
from fintendo.rag.qdrant import QdrantRAGRetriever


class FakeEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3, 0.4]


def test_qdrant_docker_connection():
    client = QdrantClient(
        url="http://localhost:6333"
    )

    collection_name = f"test_{uuid.uuid4().hex}"

    retriever = QdrantRAGRetriever(
        client=client,
        embedding_provider=FakeEmbeddingProvider(),
        collection_name=collection_name,
    )

    retriever.initialize_collection(
        vector_size=4
    )

    chunk = RAGChunk(
        chunk_id=f"chunk-{uuid.uuid4()}",
        document_id=f"doc-{uuid.uuid4()}",
        chunk_index=0,
        title="Reliance revenue growth",
        content="Reliance reported strong revenue growth.",
        source="Test Source",
        ticker="RELIANCE",
        document_type="earnings",
    )

    retriever.add_documents([chunk])

    results = retriever.search(
        query="Reliance revenue growth",
        ticker="RELIANCE",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk.document_id == chunk.document_id