from fintendo.rag.chunker import TextChunker
from fintendo.rag.models import RAGChunk, RAGDocument


class RAGDocumentProcessor:
    def __init__(self, chunker: TextChunker) -> None:
        self.chunker = chunker

    def process(self, document: RAGDocument) -> list[RAGChunk]:
        text_chunks = self.chunker.split(document.content)

        return [
            RAGChunk(
                chunk_id=f"{document.document_id}-chunk-{chunk.chunk_index}",
                document_id=document.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                title=document.title,
                source=document.source,
                source_url=document.source_url,
                ticker=document.ticker,
                document_type=document.document_type,
                published_at=document.published_at,
            )
            for chunk in text_chunks
        ]