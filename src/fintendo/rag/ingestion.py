from fintendo.rag.document_processor import RAGDocumentProcessor
from fintendo.rag.models import RAGDocument
from fintendo.rag.retriever import RAGRetriever


class RAGIngestionService:
    def __init__(
        self,
        document_processor: RAGDocumentProcessor,
        retriever: RAGRetriever,
    ) -> None:
        self.document_processor = document_processor
        self.retriever = retriever

    def ingest(self, document: RAGDocument) -> None:
        chunks = self.document_processor.process(document)

        self.retriever.add_documents(chunks)