import pytest

from fintendo.agents.research.market_intelligence.synthesis_guardrails import (
    MarketIntelligenceSynthesisGuardrail,
)
from fintendo.models.market_intelligence import (
    ImpactDirection,
    Materiality,
    MarketEvent,
    MarketIntelligenceAnalysis,
    Sentiment,
    SentimentStrength,
    TimeHorizon,
)


def build_event(
    ticker: str = "HDFCBANK",
    source_url: str = "https://www.hdfc.bank.in/",
) -> MarketEvent:
    return MarketEvent(
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
        source_url=source_url,
    )


def build_analysis(
    ticker: str = "HDFCBANK",
    key_events: list[MarketEvent] | None = None,
) -> MarketIntelligenceAnalysis:
    return MarketIntelligenceAnalysis(
        ticker=ticker,
        score=75,
        overall_sentiment=Sentiment.POSITIVE,
        sentiment_strength=SentimentStrength.MODERATE,
        summary=(
            "The available information indicates a moderately positive "
            "market-intelligence picture for HDFC Bank."
        ),
        key_events=key_events or [build_event()],
        positive_factors=[
            "Business growth",
            "Digital banking expansion",
        ],
        negative_factors=[],
        catalysts=[
            "Continued business growth",
        ],
        risks=[
            "Execution risk",
        ],
        short_term_outlook=ImpactDirection.POSITIVE,
        medium_term_outlook=ImpactDirection.POSITIVE,
        long_term_outlook=ImpactDirection.UNCERTAIN,
    )


def test_valid_analysis_passes() -> None:
    guardrail = MarketIntelligenceSynthesisGuardrail()

    event = build_event()
    analysis = build_analysis(key_events=[event])

    validated = guardrail.validate(
        ticker="HDFCBANK",
        analysis=analysis,
        events=[event],
    )

    assert validated == analysis


def test_wrong_ticker_fails() -> None:
    guardrail = MarketIntelligenceSynthesisGuardrail()

    event = build_event(ticker="HDFCBANK")
    analysis = build_analysis(
        ticker="RELIANCE",
        key_events=[event],
    )

    with pytest.raises(
        ValueError,
        match="does not match requested ticker",
    ):
        guardrail.validate(
            ticker="HDFCBANK",
            analysis=analysis,
            events=[event],
        )


def test_fabricated_key_event_fails() -> None:
    guardrail = MarketIntelligenceSynthesisGuardrail()

    validated_event = build_event(
        source_url="https://www.hdfc.bank.in/",
    )

    fabricated_event = build_event(
        source_url="https://fabricated.example.com/event",
    )

    analysis = build_analysis(
        key_events=[fabricated_event],
    )

    with pytest.raises(
        ValueError,
        match="source was not present",
    ):
        guardrail.validate(
            ticker="HDFCBANK",
            analysis=analysis,
            events=[validated_event],
        )