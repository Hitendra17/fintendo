from unittest.mock import Mock

from fintendo.agents.research.technical.agent import TechnicalAgent
from fintendo.models.research import TechnicalAnalysis
from fintendo.models.technical import TechnicalSnapshot
from fintendo.models.technical_confidence import TechnicalConfidence
from fintendo.models.technical_evidence import (
    TechnicalEvidence,
    TechnicalEvidenceType,
)


def test_technical_agent_consumes_evidence_and_confidence():
    llm = Mock()

    expected_analysis = TechnicalAnalysis(
        ticker="TCS",
        score=78.0,
        summary="Bullish trend with positive momentum.",
        trend="bullish",
        momentum="bullish",
        volatility="moderate",
        bullish_signals=[
            "Price is above the major moving averages.",
            "MACD is above its signal line.",
        ],
        bearish_signals=[
            "Price is approaching resistance.",
        ],
        support_levels=[3500.0],
        resistance_levels=[3900.0],
        outlook="Technically constructive with moderate volatility.",
        evidence=[],
        confidence=TechnicalConfidence(
            score=0.9,
            observations=252,
            history_score=1.0,
            trend_score=1.0,
            momentum_score=1.0,
            volatility_score=1.0,
            levels_score=1.0,
            missing_indicators=[],
            limitations=[],
        ),
    )

    llm.generate_structured.return_value = expected_analysis

    agent = TechnicalAgent(llm)

    snapshot = TechnicalSnapshot(
        ticker="TCS",
        as_of="2026-09-04T00:00:00",
        observations=252,
        close=3800.0,
        sma_20=3700.0,
        sma_50=3500.0,
        ema_20=3720.0,
        ema_50=3520.0,
        rsi_14=62.0,
        macd=45.0,
        macd_signal=35.0,
        macd_histogram=10.0,
        support_levels=[3500.0],
        resistance_levels=[3900.0],
        volatility_20d=0.18,
        price_vs_sma_20_pct=2.70,
        price_vs_sma_50_pct=8.57,
        price_vs_ema_20_pct=2.15,
        price_vs_ema_50_pct=7.95,
        macd_spread=10.0,
        distance_to_support_pct=8.57,
        distance_to_resistance_pct=2.56,
    )

    evidence = [
        TechnicalEvidence(
            source="TechnicalEngine",
            field="close",
            evidence_type=TechnicalEvidenceType.OBSERVED,
            value=3800.0,
            period=snapshot.as_of,
            description="Closing price.",
        )
    ]

    confidence = TechnicalConfidence(
        score=0.9,
        observations=252,
        history_score=1.0,
        trend_score=1.0,
        momentum_score=1.0,
        volatility_score=1.0,
        levels_score=1.0,
        missing_indicators=[],
        limitations=[],
    )

    result = agent.analyze(
        snapshot=snapshot,
        evidence=evidence,
        confidence=confidence,
    )

    assert result == expected_analysis
    llm.generate_structured.assert_called_once()

def test_technical_agent_prompt_contains_snapshot_evidence_and_confidence():
    llm = Mock()

    expected_analysis = TechnicalAnalysis(
        ticker="TCS",
        score=75.0,
        summary="Constructive technical setup.",
        trend="bullish",
        momentum="bullish",
        volatility="moderate",
        bullish_signals=["Price is above major moving averages."],
        bearish_signals=["Resistance is relatively close."],
        support_levels=[3500.0],
        resistance_levels=[3900.0],
        outlook="Constructive with moderate volatility.",
        evidence=[],
        confidence=TechnicalConfidence(
            score=0.9,
            observations=252,
            history_score=1.0,
            trend_score=1.0,
            momentum_score=1.0,
            volatility_score=1.0,
            levels_score=1.0,
            missing_indicators=[],
            limitations=[],
        ),
    )

    llm.generate_structured.return_value = expected_analysis

    agent = TechnicalAgent(llm)

    snapshot = TechnicalSnapshot(
        ticker="TCS",
        as_of="2026-09-04T00:00:00",
        observations=252,
        close=3800.0,
        sma_20=3700.0,
        sma_50=3500.0,
        ema_20=3720.0,
        ema_50=3520.0,
        rsi_14=62.0,
        macd=45.0,
        macd_signal=35.0,
        macd_histogram=10.0,
        support_levels=[3500.0],
        resistance_levels=[3900.0],
        volatility_20d=0.18,
        price_vs_sma_20_pct=2.70,
        price_vs_sma_50_pct=8.57,
        price_vs_ema_20_pct=2.15,
        price_vs_ema_50_pct=7.95,
        macd_spread=10.0,
        distance_to_support_pct=8.57,
        distance_to_resistance_pct=2.56,
    )

    evidence = [
        TechnicalEvidence(
            source="TechnicalEngine",
            field="close",
            evidence_type=TechnicalEvidenceType.OBSERVED,
            value=3800.0,
            period=snapshot.as_of,
            description="Closing price.",
        )
    ]

    confidence = TechnicalConfidence(
        score=0.9,
        observations=252,
        history_score=1.0,
        trend_score=1.0,
        momentum_score=1.0,
        volatility_score=1.0,
        levels_score=1.0,
        missing_indicators=[],
        limitations=[],
    )

    agent.analyze(
        snapshot=snapshot,
        evidence=evidence,
        confidence=confidence,
    )

    prompt = llm.generate_structured.call_args.args[0]

    assert "TCS" in prompt
    assert "3800.0" in prompt
    assert "Technical Evidence" in prompt
    assert "Technical Confidence" in prompt
    assert "0.9" in prompt
    assert "252" in prompt
    assert "close" in prompt
    assert "TechnicalEngine" in prompt