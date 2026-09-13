from unittest.mock import Mock

from fintendo.agents.research.technical.service import (
    TechnicalResearchService,
)
from fintendo.models.research import TechnicalAnalysis
from fintendo.models.technical import TechnicalSnapshot
from fintendo.models.technical_confidence import TechnicalConfidence
from fintendo.models.technical_evidence import (
    TechnicalEvidence,
    TechnicalEvidenceType,
)


def test_technical_research_service_orchestrates_pipeline():
    market_data_client = Mock()
    technical_engine = Mock()
    evidence_builder = Mock()
    confidence_calculator = Mock()
    technical_agent = Mock()

    price_history = Mock()

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

    expected_analysis = Mock(spec=TechnicalAnalysis)

    market_data_client.get_price_history.return_value = price_history
    technical_engine.calculate.return_value = snapshot
    evidence_builder.build.return_value = evidence
    confidence_calculator.calculate.return_value = confidence
    technical_agent.analyze.return_value = expected_analysis

    service = TechnicalResearchService(
        market_data_client=market_data_client,
        technical_engine=technical_engine,
        evidence_builder=evidence_builder,
        confidence_calculator=confidence_calculator,
        technical_agent=technical_agent,
    )

    result = service.analyze(
        ticker="TCS",
        period="1y",
        interval="1d",
    )

    assert result is expected_analysis

    market_data_client.get_price_history.assert_called_once_with(
        ticker="TCS",
        period="1y",
        interval="1d",
    )

    technical_engine.calculate.assert_called_once_with(
        ticker="TCS",
        price_history=price_history,
    )

    evidence_builder.build.assert_called_once_with(
        snapshot,
    )

    confidence_calculator.calculate.assert_called_once_with(
        snapshot,
    )

    technical_agent.analyze.assert_called_once_with(
        snapshot=snapshot,
        evidence=evidence,
        confidence=confidence,
    )