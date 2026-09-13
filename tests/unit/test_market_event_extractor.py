from datetime import datetime, timezone

from fintendo.agents.research.market_intelligence.event_extractor import (
    MarketEventExtractor,
    MarketEventList,
)
from fintendo.models.market_intelligence import NewsArticle
from fintendo.rag.models import RAGChunk, RAGSearchResult


class FakeGeminiClient:
    def __init__(self, response):
        self.response = response
        self.last_prompt = None
        self.last_model = None

    def generate_structured(self, prompt, response_model):
        self.last_prompt = prompt
        self.last_model = response_model
        return self.response


def make_article() -> NewsArticle:
    return NewsArticle(
        source="Reuters",
        title="Reliance announces major new investment",
        url="https://example.com/reliance-investment",
        published_at=datetime.now(timezone.utc),
        author="Test Author",
        content=(
            "Reliance Industries announced a major investment "
            "that could materially affect its business outlook. "
            "The company expects the investment to support growth "
            "over the medium term."
        ),
        ticker="RELIANCE",
    )


def make_rag_result() -> RAGSearchResult:
    chunk = RAGChunk(
        chunk_id="doc-1-chunk-0",
        document_id="doc-1",
        chunk_index=0,
        content=(
            "Reliance has historically invested heavily in new "
            "business segments and infrastructure."
        ),
        title="Reliance Annual Report",
        source="Reliance Investor Relations",
        source_url="https://example.com/report",
        ticker="RELIANCE",
        document_type="annual_report",
        published_at=datetime.now(timezone.utc),
    )

    return RAGSearchResult(
        chunk=chunk,
        score=0.92,
    )


def test_extract_returns_gemini_events():
    response = MarketEventList(events=[])

    llm = FakeGeminiClient(response)

    extractor = MarketEventExtractor(llm)

    result = extractor.extract(
        ticker="RELIANCE",
        articles=[make_article()],
        rag_context=[make_rag_result()],
    )

    assert result == []
    assert llm.last_model is MarketEventList


def test_prompt_contains_current_and_rag_information():
    llm = FakeGeminiClient(
        MarketEventList(events=[])
    )

    extractor = MarketEventExtractor(llm)

    extractor.extract(
        ticker="RELIANCE",
        articles=[make_article()],
        rag_context=[make_rag_result()],
    )

    prompt = llm.last_prompt

    assert "RELIANCE" in prompt
    assert "Reliance announces major new investment" in prompt
    assert "Reliance Annual Report" in prompt
    assert "UNTRUSTED DATA" in prompt

    assert (
        "recommend buying or selling the stock"
        in prompt.lower()
    )


def test_empty_ticker_is_rejected():
    llm = FakeGeminiClient(
        MarketEventList(events=[])
    )

    extractor = MarketEventExtractor(llm)

    try:
        extractor.extract(
            ticker="",
            articles=[make_article()],
            rag_context=[],
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "ticker" in str(exc)


def test_empty_articles_are_rejected():
    llm = FakeGeminiClient(
        MarketEventList(events=[])
    )

    extractor = MarketEventExtractor(llm)

    try:
        extractor.extract(
            ticker="RELIANCE",
            articles=[],
            rag_context=[],
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "articles" in str(exc)