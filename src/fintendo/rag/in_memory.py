from fintendo.rag.models import RAGChunk, RAGSearchResult
from fintendo.rag.retriever import RAGRetriever


class InMemoryRAGRetriever(RAGRetriever):
    def __init__(self) -> None:
        self.chunks: list[RAGChunk] = []

    def add_documents(
    self,
    chunks: list[RAGChunk],
    ) -> None:
     self.chunks.extend(chunks)

    def search(
        self,
        query: str,
        ticker: str,
        top_k: int = 5,
    ) -> list[RAGSearchResult]:
        if not query.strip():
            raise ValueError("query must not be empty.")

        if not ticker.strip():
            raise ValueError("ticker must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_terms = set(query.lower().split())
        results: list[RAGSearchResult] = []

        for chunk in self.chunks:
            if chunk.ticker.upper() != ticker.upper():
                continue

            chunk_text = (
                f"{chunk.title} "
                f"{chunk.content} "
                f"{chunk.document_type}"
            ).lower()

            matching_terms = sum(
                1 for term in query_terms if term in chunk_text
            )

            if matching_terms == 0:
                continue

            score = min(
                matching_terms / len(query_terms),
                1.0,
            )

            results.append(
                RAGSearchResult(
                    chunk=chunk,
                    score=score,
                )
            )

        results.sort(key=lambda result: result.score, reverse=True)

        return results[:top_k]