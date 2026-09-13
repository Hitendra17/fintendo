from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    ticker: str = Field(
        min_length=1,
        description="Stock ticker to research.",
        examples=["SIEMENS"],
    )

    rag_query: str | None = Field(
        default=None,
        description="Optional custom RAG query.",
    )

    rag_top_k: int = Field(
        default=5,
        gt=0,
        le=20,
        description="Number of historical RAG results to retrieve.",
    )

    technical_period: str = Field(
        default="1y",
        min_length=1,
    )

    technical_interval: str = Field(
        default="1d",
        min_length=1,
    )