import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from fintendo.rag.embeddings import EmbeddingProvider
from fintendo.rag.models import (
    RAGChunk,
    RAGSearchResult,
)
from fintendo.rag.retriever import RAGRetriever


class QdrantRAGRetriever(RAGRetriever):
    """
    Persistent Qdrant-backed RAG retriever.

    All companies share one collection. Company isolation is enforced
    through the ticker payload field during vector search.
    """

    def __init__(
        self,
        client: QdrantClient,
        embedding_provider: EmbeddingProvider,
        collection_name: str = "fintendo_rag",
    ) -> None:
        self.client = client
        self.embedding_provider = embedding_provider
        self.collection_name = collection_name

    @staticmethod
    def _point_id(chunk_id: str) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                chunk_id,
            )
        )

    def initialize_collection(
        self,
        vector_size: int,
    ) -> None:
        if vector_size <= 0:
            raise ValueError(
                "vector_size must be greater than zero."
            )

        collections = (
            self.client.get_collections()
            .collections
        )

        if any(
            collection.name == self.collection_name
            for collection in collections
        ):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def add_documents(
        self,
        chunks: list[RAGChunk],
    ) -> None:
        if not chunks:
            return

        batch_size = 50

        for start in range(
            0,
            len(chunks),
            batch_size,
        ):
            batch = chunks[
                start : start + batch_size
            ]

            points = []

            for chunk in batch:
                vector = (
                    self.embedding_provider.embed(
                        chunk.content
                    )
                )

                points.append(
                    models.PointStruct(
                        id=self._point_id(
                            chunk.chunk_id
                        ),
                        vector=vector,
                        payload=chunk.model_dump(
                            mode="json"
                        ),
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(
        self,
        query: str,
        ticker: str,
        top_k: int = 5,
    ) -> list:
        if not query.strip():
            raise ValueError(
                "query must not be empty."
            )

        if not ticker.strip():
            raise ValueError(
                "ticker must not be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_vector = (
            self.embedding_provider.embed(query)
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="ticker",
                        match=models.MatchValue(
                            value=ticker.strip().upper()
                        ),
                    )
                ]
            ),
            limit=top_k,
            with_payload=True,
        ).points

        matches = []

        for result in results:
            if not result.payload:
                continue

            chunk = RAGChunk.model_validate(
                result.payload
            )

        matches.append(
        RAGSearchResult(
        chunk=chunk,
        score=max(
            0.0,
            min(
                float(result.score),
                1.0,
            ),
        ),
    )
)
        return matches
