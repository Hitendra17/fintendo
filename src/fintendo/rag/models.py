from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class RAGDocument(BaseModel):
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    ticker: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    published_at: datetime | None = None




class RAGChunk(BaseModel):
    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    content: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_url: HttpUrl | None = None
    ticker: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    published_at: datetime | None = None

class RAGSearchResult(BaseModel):
    chunk: RAGChunk
    score: float = Field(ge=0, le=1)