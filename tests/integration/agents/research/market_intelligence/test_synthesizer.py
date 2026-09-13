import pytest

from fintendo.agents.research.market_intelligence.synthesizer import (
    MarketIntelligenceSynthesizer,
)
from fintendo.llm.gemini import GeminiClient
from fintendo.models.market_intelligence import (
    ImpactDirection,
    Materiality,
    MarketEvent,
    NewsArticle,
    Sentiment,
    SentimentStrength,
    TimeHorizon,
)


@pytest.mark.integration
def test_market_intelligence_synthesizer_with_real_gemini() -> None:
    ticker = "HDFCBANK"

    article = NewsArticle(
        source="HDFC Bank Official Website",
        title="HDFC Bank corporate update",
        url="https://www.hdfc.bank.in/",
        content=(
            "HDFC Bank continues to focus on growth, digital banking, "
            "customer expansion, and maintaining strong financial performance."
        ),
        ticker=ticker,
    )

    event = MarketEvent(
        ticker=ticker,
        event_type="business_update",
        title="HDFC Bank continues growth and digital banking focus",
        summary=(
            "HDFC Bank continues to focus on business growth, "
            "digital banking, and customer expansion."
        ),
        sentiment=Sentiment.POSITIVE,
        sentiment_strength=SentimentStrength.MODERATE,
        materiality=Materiality.MODERATE,
        potential_impact=ImpactDirection.POSITIVE,
        affected_areas=[
            "business growth",
            "digital banking",
            "customer expansion",
        ],
        time_horizon=TimeHorizon.MEDIUM_TERM,
        source="HDFC Bank Official Website",
        source_url="https://www.hdfc.bank.in/",
    )

    synthesizer = MarketIntelligenceSynthesizer(
        llm=GeminiClient(),
    )

    analysis = synthesizer.synthesize(
        ticker=ticker,
        events=[event],
        articles=[article],
        rag_context=[],
    )

    assert analysis.ticker == ticker
    assert 0 <= analysis.score <= 100
    assert analysis.summary
    assert analysis.overall_sentiment in Sentiment
    assert analysis.sentiment_strength in SentimentStrength
    assert analysis.short_term_outlook in ImpactDirection
    assert analysis.medium_term_outlook in ImpactDirection
    assert analysis.long_term_outlook in ImpactDirection