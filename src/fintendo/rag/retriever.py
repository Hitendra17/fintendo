from abc import ABC, abstractmethod

from fintendo.rag.models import RAGChunk, RAGSearchResult


class RAGRetriever(ABC):
    @abstractmethod
    def add_documents(
        self,
        chunks: list[RAGChunk],
    ) -> None:
        """Add chunks to the knowledge base."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        ticker: str,
        top_k: int = 5,
    ) -> list[RAGSearchResult]:
        """Retrieve relevant chunks for a query."""
        raise NotImplementedError