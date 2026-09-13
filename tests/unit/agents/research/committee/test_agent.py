from unittest.mock import Mock

import pytest

from fintendo.agents.research.committee.agent import CommitteeAgent
from fintendo.models.research import CommitteeDecision


def make_fundamental() -> Mock:
    fundamental = Mock()
    fundamental.ticker = "HDFCBANK"
    fundamental.model_dump.return_value = {
        "ticker": "HDFCBANK",
        "score": 90,
        "summary": "Strong fundamental profile with healthy growth and profitability.",
        "strengths": [
            "Strong revenue growth",
            "Healthy profitability",
        ],
        "weaknesses": [
            "Valuation remains elevated",
        ],
        "catalysts": [
            "Continued loan growth",
        ],
        "risks": [
            "Asset quality deterioration",
        ],
        "evidence": [
            {
                "source": "Yahoo Finance",
                "field": "revenue_growth",
                "evidence_type": "derived",
                "value": 15.0,
                "description": "Revenue growth remains healthy.",
            }
        ],
        "confidence": {
            "score": 0.9,
            "level": "high",
            "reasons": [
                "Sufficient financial statement history",
            ],
        },
    }
    return fundamental


def make_technical() -> Mock:
    technical = Mock()
    technical.ticker = "HDFCBANK"
    technical.model_dump.return_value = {
        "ticker": "HDFCBANK",
        "score": 55,
        "summary": "Mixed technical setup with moderate momentum.",
        "trend": "mixed",
        "momentum": "neutral",
        "volatility": "moderate",
        "bullish_signals": [
            "Price remains above long-term support",
        ],
        "bearish_signals": [
            "Short-term momentum is weak",
        ],
        "support_levels": [
            1600.0,
        ],
        "resistance_levels": [
            1800.0,
        ],
        "outlook": "Mixed near-term technical outlook.",
        "evidence": [
            {
                "source": "Yahoo Finance",
                "field": "SMA20",
                "evidence_type": "derived",
                "value": 1700.0,
                "description": "Price is near the short-term moving average.",
            }
        ],
        "confidence": {
            "score": 0.9,
            "level": "high",
            "reasons": [
                "Sufficient historical price data",
            ],
        },
    }
    return technical


def make_market_intelligence() -> Mock:
    market_intelligence = Mock()
    market_intelligence.ticker = "HDFCBANK"
    market_intelligence.model_dump.return_value = {
        "ticker": "HDFCBANK",
        "score": 75,
        "overall_sentiment": "positive",
        "sentiment_strength": "moderate",
        "summary": "Recent market developments are broadly constructive.",
        "key_events": [
            {
                "ticker": "HDFCBANK",
                "event_type": "business_update",
                "title": "HDFC Bank reports positive business developments",
                "summary": (
                    "Recent developments support the company's "
                    "medium-term outlook."
                ),
                "sentiment": "positive",
                "sentiment_strength": "moderate",
                "materiality": "moderate",
                "potential_impact": "positive",
                "affected_areas": [
                    "growth",
                ],
                "time_horizon": "medium_term",
                "source": "Mint",
                "source_url": "https://www.livemint.com/",
                "published_at": "2026-09-01T00:00:00Z",
            }
        ],
        "positive_factors": [
            "Positive business developments",
        ],
        "negative_factors": [
            "Broader market uncertainty",
        ],
        "catalysts": [
            "Continued business growth",
        ],
        "risks": [
            "Macroeconomic uncertainty",
        ],
        "short_term_outlook": "positive",
        "medium_term_outlook": "positive",
        "long_term_outlook": "positive",
    }
    return market_intelligence


def test_committee_agent_returns_structured_decision() -> None:
    expected = CommitteeDecision(
        ticker="HDFCBANK",
        recommendation="Positive",
        conviction=78,
        rationale=(
            "Fundamentals and market intelligence are constructive, "
            "while technical signals remain mixed."
        ),
        bull_case=[
            "Strong fundamental profile",
            "Positive market developments",
        ],
        bear_case=[
            "Mixed technical setup",
        ],
        key_risks=[
            "Near-term technical weakness",
        ],
        confidence=0.9,
    )

    llm = Mock()
    llm.generate_structured.return_value = expected

    agent = CommitteeAgent(llm=llm)

    result = agent.decide(
        fundamental=make_fundamental(),
        technical=make_technical(),
        market_intelligence=make_market_intelligence(),
    )

    assert result == expected
    llm.generate_structured.assert_called_once()


def test_committee_agent_prompt_contains_all_three_analyses() -> None:
    llm = Mock()
    llm.generate_structured.return_value = CommitteeDecision(
        ticker="HDFCBANK",
        recommendation="Positive",
        conviction=70,
        rationale="Combined research is constructive.",
        bull_case=[
            "Strong fundamentals",
        ],
        bear_case=[
            "Mixed technicals",
        ],
        key_risks=[
            "Market uncertainty",
        ],
        confidence=0.8,
    )

    agent = CommitteeAgent(llm=llm)

    agent.decide(
        fundamental=make_fundamental(),
        technical=make_technical(),
        market_intelligence=make_market_intelligence(),
    )

    prompt = llm.generate_structured.call_args.args[0]

    assert "HDFCBANK" in prompt
    assert "Strong fundamental profile" in prompt
    assert "Mixed technical setup" in prompt
    assert "Recent market developments are broadly constructive" in prompt


def test_committee_agent_rejects_mismatched_ticker() -> None:
    llm = Mock()
    agent = CommitteeAgent(llm=llm)

    technical = make_technical()
    technical.ticker = "RELIANCE"

    with pytest.raises(
        ValueError,
        match="technical ticker does not match",
    ):
        agent.decide(
            fundamental=make_fundamental(),
            technical=technical,
            market_intelligence=make_market_intelligence(),
        )

    llm.generate_structured.assert_not_called()


def test_committee_agent_rejects_mismatched_market_intelligence_ticker() -> None:
    llm = Mock()
    agent = CommitteeAgent(llm=llm)

    market_intelligence = make_market_intelligence()
    market_intelligence.ticker = "RELIANCE"

    with pytest.raises(
        ValueError,
        match="market intelligence ticker does not match",
    ):
        agent.decide(
            fundamental=make_fundamental(),
            technical=make_technical(),
            market_intelligence=market_intelligence,
        )

    llm.generate_structured.assert_not_called()