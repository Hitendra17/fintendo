from datetime import datetime, timezone

import pytest

from fintendo.agents.research.market_intelligence.guardrails import (
    MarketEventGuardrail,
)
from fintendo.models.market_intelligence import (
    ImpactDirection,
    MarketEvent,
    Materiality,
    Sentiment,
    SentimentStrength,
    TimeHorizon,
)


def make_event(
    *,
    ticker: str = "RELIANCE",
    title: str = "Reliance announces strategic partnership",
    source_url: str = "https://example.com/event",
) -> MarketEvent:
    return MarketEvent(
        ticker=ticker,
        event_type="Strategic Partnership",
        title=title,
        summary=(
            "Reliance announced a strategic partnership "
            "that could affect future business development."
        ),
        sentiment=Sentiment.POSITIVE,
        sentiment_strength=SentimentStrength.MODERATE,
        materiality=Materiality.HIGH,
        potential_impact=ImpactDirection.POSITIVE,
        affected_areas=["Strategic Partnerships"],
        time_horizon=TimeHorizon.MEDIUM_TERM,
        source="Reliance Investor Relations",
        source_url=source_url,
        published_at=datetime.now(timezone.utc),
    )


def test_valid_events_are_returned():
    guardrail = MarketEventGuardrail()

    event = make_event()

    result = guardrail.validate(
        ticker="RELIANCE",
        events=[event],
    )

    assert result == [event]


def test_wrong_ticker_is_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event(
        ticker="TCS",
    )

    with pytest.raises(ValueError, match="does not match"):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_empty_ticker_is_rejected():
    guardrail = MarketEventGuardrail()

    with pytest.raises(
        ValueError,
        match="ticker must not be empty",
    ):
        guardrail.validate(
            ticker="",
            events=[],
        )


def test_empty_source_is_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event()

    event = event.model_copy(
        update={"source": ""},
    )

    with pytest.raises(
        ValueError,
        match="source must not be empty",
    ):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_empty_title_is_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event()

    event = event.model_copy(
        update={"title": ""},
    )

    with pytest.raises(
        ValueError,
        match="title must not be empty",
    ):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_empty_summary_is_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event()

    event = event.model_copy(
        update={"summary": ""},
    )

    with pytest.raises(
        ValueError,
        match="summary must not be empty",
    ):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_empty_event_type_is_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event()

    event = event.model_copy(
        update={"event_type": ""},
    )

    with pytest.raises(
        ValueError,
        match="event_type must not be empty",
    ):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_empty_affected_areas_are_rejected():
    guardrail = MarketEventGuardrail()

    event = make_event()

    event = event.model_copy(
        update={"affected_areas": []},
    )

    with pytest.raises(
        ValueError,
        match="affected_areas must not be empty",
    ):
        guardrail.validate(
            ticker="RELIANCE",
            events=[event],
        )


def test_duplicate_events_are_removed():
    guardrail = MarketEventGuardrail()

    first_event = make_event()

    duplicate_event = make_event()

    result = guardrail.validate(
        ticker="RELIANCE",
        events=[
            first_event,
            duplicate_event,
        ],
    )

    assert len(result) == 1
    assert result[0] == first_event


def test_different_events_are_preserved():
    guardrail = MarketEventGuardrail()

    first_event = make_event(
        title="Reliance announces strategic partnership",
        source_url="https://example.com/event-1",
    )

    second_event = make_event(
        title="Reliance announces new investment",
        source_url="https://example.com/event-2",
    )

    result = guardrail.validate(
        ticker="RELIANCE",
        events=[
            first_event,
            second_event,
        ],
    )

    assert len(result) == 2