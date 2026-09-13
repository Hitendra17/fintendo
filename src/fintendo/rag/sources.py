from abc import ABC, abstractmethod

from fintendo.rag.models import RAGDocument


class RAGDocumentSource(ABC):
    @abstractmethod
    def fetch(
        self,
        ticker: str,
    ) -> list[RAGDocument]:
        """Fetch documents relevant to a ticker."""
        raise NotImplementedError