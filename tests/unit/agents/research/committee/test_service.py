from datetime import  timezone
from unittest.mock import Mock

import pytest

from fintendo.agents.research.committee.service import CommitteeResearchService
from fintendo.models.market_intelligence import (
    ImpactDirection,
    MarketIntelligenceAnalysis,
    Sentiment,
    SentimentStrength,
)
from fintendo.models.research import (
    CommitteeDecision,
    FundamentalAnalysis,
    TechnicalAnalysis,
)
from fintendo.models.technical_confidence import TechnicalConfidence


def make_service() -> tuple[
    CommitteeResearchService,
    Mock,
    Mock,
    Mock,
    Mock,
]:
    fundamental_service = Mock()
    technical_service = Mock()
    market_intelligence_service = Mock()
    committee_agent = Mock()

    service = CommitteeResearchService(
        fundamental_service=fundamental_service,
        technical_service=technical_service,
        market_intelligence_service=market_intelligence_service,
        committee_agent=committee_agent,
    )

    return (
        service,
        fundamental_service,
        technical_service,
        market_intelligence_service,
        committee_agent,
    )


def make_fundamental_analysis(ticker: str) -> FundamentalAnalysis:
    return FundamentalAnalysis(
        ticker=ticker,
        score=80,
        summary="Fundamentals are strong.",
        strengths=["Strong profitability"],
        weaknesses=["Moderate growth"],
        catalysts=["Business expansion"],
        risks=["Market slowdown"],
        evidence=[],
        confidence=0.9,
    )


def make_technical_analysis(ticker: str) -> TechnicalAnalysis:
    confidence = TechnicalConfidence(
        score=0.9,
        observations=100,
        history_score=0.9,
        trend_score=0.9,
        momentum_score=0.9,
        volatility_score=0.9,
        levels_score=0.9,
        missing_indicators=[],
        limitations=[],
    )

    return TechnicalAnalysis(
        ticker=ticker,
        score=60,
        summary="Technical signals are mixed.",
        trend="neutral",
        momentum="neutral",
        volatility="moderate",
        bullish_signals=["Price above support"],
        bearish_signals=["Weak momentum"],
        support_levels=[1500.0],
        resistance_levels=[1700.0],
        outlook="Mixed near-term technical outlook.",
        evidence=[],
        confidence=confidence,
    )


def make_market_intelligence_analysis(
    ticker: str,
) -> MarketIntelligenceAnalysis:
    return MarketIntelligenceAnalysis(
        ticker=ticker,
        score=75,
        overall_sentiment=Sentiment.POSITIVE,
        sentiment_strength=SentimentStrength.MODERATE,
        summary="Market intelligence is broadly positive.",
        key_events=[],
        positive_factors=["Positive business developments"],
        negative_factors=["Market uncertainty"],
        catalysts=["New growth opportunities"],
        risks=["Competitive pressure"],
        short_term_outlook=ImpactDirection.POSITIVE,
        medium_term_outlook=ImpactDirection.POSITIVE,
        long_term_outlook=ImpactDirection.POSITIVE,
    )


def test_committee_service_orchestrates_full_research_pipeline() -> None:
    (
        service,
        fundamental_service,
        technical_service,
        market_intelligence_service,
        committee_agent,
    ) = make_service()

    fundamental = make_fundamental_analysis("HDFCBANK")
    technical = make_technical_analysis("HDFCBANK")
    market_intelligence = make_market_intelligence_analysis("HDFCBANK")

    expected = CommitteeDecision(
        ticker="HDFCBANK",
        recommendation="Positive",
        conviction=80,
        rationale="Research layers are broadly constructive.",
        bull_case=[
            "Strong fundamentals",
        ],
        bear_case=[
            "Mixed technical setup",
        ],
        key_risks=[
            "Market uncertainty",
        ],
        confidence=0.9,
    )

    fundamental_service.analyze.return_value = fundamental
    technical_service.analyze.return_value = technical
    market_intelligence_service.research.return_value = market_intelligence
    committee_agent.decide.return_value = expected

    market_sources = [Mock()]

    result = service.research(
        ticker=" hdfcbank ",
        company_name=" HDFC Bank ",
        market_sources=market_sources,
        rag_query="HDFC Bank growth outlook",
        rag_top_k=7,
        technical_period="2y",
        technical_interval="1wk",
    )

    assert result == expected

    fundamental_service.analyze.assert_called_once_with(
        ticker="HDFCBANK",
        company_name="HDFC Bank",
    )

    technical_service.analyze.assert_called_once_with(
        ticker="HDFCBANK",
        period="2y",
        interval="1wk",
    )

    market_intelligence_service.research.assert_called_once_with(
        ticker="HDFCBANK",
        sources=market_sources,
        rag_query="HDFC Bank growth outlook",
        top_k=7,
    )

    committee_agent.decide.assert_called_once_with(
        fundamental=fundamental,
        technical=technical,
        market_intelligence=market_intelligence,
    )


def test_committee_service_uses_default_optional_parameters() -> None:
    (
        service,
        fundamental_service,
        technical_service,
        market_intelligence_service,
        committee_agent,
    ) = make_service()

    fundamental = make_fundamental_analysis("TCS")
    technical = make_technical_analysis("TCS")
    market_intelligence = make_market_intelligence_analysis("TCS")

    expected = CommitteeDecision(
        ticker="TCS",
        recommendation="Neutral",
        conviction=60,
        rationale="Research signals are mixed.",
        bull_case=[
            "Strong business fundamentals",
        ],
        bear_case=[
            "Mixed technical signals",
        ],
        key_risks=[
            "Market volatility",
        ],
        confidence=0.8,
    )

    fundamental_service.analyze.return_value = fundamental
    technical_service.analyze.return_value = technical
    market_intelligence_service.research.return_value = market_intelligence
    committee_agent.decide.return_value = expected

    market_sources = [Mock()]

    result = service.research(
        ticker="TCS",
        company_name="Tata Consultancy Services",
        market_sources=market_sources,
    )

    assert result == expected

    fundamental_service.analyze.assert_called_once_with(
        ticker="TCS",
        company_name="Tata Consultancy Services",
    )

    technical_service.analyze.assert_called_once_with(
        ticker="TCS",
        period="1y",
        interval="1d",
    )

    market_intelligence_service.research.assert_called_once_with(
        ticker="TCS",
        sources=market_sources,
        rag_query=None,
        top_k=5,
    )

    committee_agent.decide.assert_called_once_with(
        fundamental=fundamental,
        technical=technical,
        market_intelligence=market_intelligence,
    )


def test_committee_service_research_report_preserves_all_research_layers() -> None:
    (
        service,
        fundamental_service,
        technical_service,
        market_intelligence_service,
        committee_agent,
    ) = make_service()

    fundamental = make_fundamental_analysis("INFY")
    technical = make_technical_analysis("INFY")
    market_intelligence = make_market_intelligence_analysis("INFY")

    expected_committee = CommitteeDecision(
        ticker="INFY",
        recommendation="Neutral",
        conviction=65,
        rationale="Fundamental and market signals are positive while technical signals are bearish.",
        bull_case=["Strong fundamentals"],
        bear_case=["Bearish technical trend"],
        key_risks=["Market uncertainty"],
        confidence=0.7,
    )

    fundamental_service.analyze.return_value = fundamental
    technical_service.analyze.return_value = technical
    market_intelligence_service.research.return_value = market_intelligence
    committee_agent.decide.return_value = expected_committee

    report = service.research_report(
        ticker="INFY",
        company_name="Infosys Limited",
        market_sources=[Mock()],
    )

    assert report.ticker == "INFY"
    assert report.fundamental is fundamental
    assert report.technical is technical
    assert report.market_intelligence is market_intelligence
    assert report.committee is expected_committee
    assert report.generated_at.tzinfo == timezone.utc

    fundamental_service.analyze.assert_called_once()
    technical_service.analyze.assert_called_once()
    market_intelligence_service.research.assert_called_once()
    committee_agent.decide.assert_called_once_with(
        fundamental=fundamental,
        technical=technical,
        market_intelligence=market_intelligence,
    )


@pytest.mark.parametrize(
    ("ticker", "company_name", "market_sources", "rag_top_k", "error"),
    [
        (
            "   ",
            "HDFC Bank",
            [Mock()],
            5,
            "ticker must not be empty",
        ),
        (
            "HDFCBANK",
            "   ",
            [Mock()],
            5,
            "company_name must not be empty",
        ),
        (
            "HDFCBANK",
            "HDFC Bank",
            [],
            5,
            "market_sources must not be empty",
        ),
        (
            "HDFCBANK",
            "HDFC Bank",
            [Mock()],
            0,
            "rag_top_k must be positive",
        ),
    ],
)
def test_committee_service_validates_input(
    ticker: str,
    company_name: str,
    market_sources: list[Mock],
    rag_top_k: int,
    error: str,
) -> None:
    (
        service,
        fundamental_service,
        technical_service,
        market_intelligence_service,
        committee_agent,
    ) = make_service()

    with pytest.raises(ValueError, match=error):
        service.research(
            ticker=ticker,
            company_name=company_name,
            market_sources=market_sources,
            rag_top_k=rag_top_k,
        )

    fundamental_service.analyze.assert_not_called()
    technical_service.analyze.assert_not_called()
    market_intelligence_service.research.assert_not_called()
    committee_agent.decide.assert_not_called()