from datetime import datetime, timezone

from fintendo.models.technical import TechnicalSnapshot
from fintendo.quant.technical_confidence import (
    TechnicalConfidenceCalculator,
)


def make_snapshot(**overrides) -> TechnicalSnapshot:
    data = {
        "ticker": "TCS",
        "as_of": datetime(2026, 9, 1, tzinfo=timezone.utc),
        "observations": 252,
        "close": 3500.0,
        "sma_20": 3400.0,
        "sma_50": 3200.0,
        "ema_20": 3450.0,
        "ema_50": 3250.0,
        "rsi_14": 64.0,
        "macd": 45.0,
        "macd_signal": 38.0,
        "macd_histogram": 7.0,
        "support_levels": [3400.0, 3300.0],
        "resistance_levels": [3600.0, 3700.0],
        "volatility_20d": 0.18,
        "price_vs_sma_20_pct": 2.94,
        "price_vs_sma_50_pct": 9.38,
        "price_vs_ema_20_pct": 1.45,
        "price_vs_ema_50_pct": 7.69,
        "macd_spread": 7.0,
        "distance_to_support_pct": 2.94,
        "distance_to_resistance_pct": -2.78,
    }

    data.update(overrides)

    return TechnicalSnapshot(**data)


def test_complete_long_history_produces_full_confidence():
    snapshot = make_snapshot()

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert result.score == 1.0
    assert result.history_score == 1.0
    assert result.trend_score == 1.0
    assert result.momentum_score == 1.0
    assert result.volatility_score == 1.0
    assert result.levels_score == 1.0


def test_short_history_caps_confidence():
    snapshot = make_snapshot(observations=10)

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert result.score <= 0.40
    assert result.observations == 10


def test_missing_indicators_reduce_confidence():
    snapshot = make_snapshot(
        sma_50=None,
        ema_50=None,
        rsi_14=None,
        volatility_20d=None,
    )

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert result.score < 1.0
    assert result.trend_score == 0.5
    assert result.momentum_score == 0.75
    assert result.volatility_score == 0.0


def test_missing_indicators_are_reported():
    snapshot = make_snapshot(
        sma_50=None,
        rsi_14=None,
        volatility_20d=None,
    )

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert "sma_50" in result.missing_indicators
    assert "rsi_14" in result.missing_indicators
    assert "volatility_20d" in result.missing_indicators


def test_short_history_creates_limitation():
    snapshot = make_snapshot(observations=10)

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert any(
        "limited price history" in limitation.lower()
        or "very limited price history" in limitation.lower()
        for limitation in result.limitations
    )


def test_missing_indicators_create_limitation():
    snapshot = make_snapshot(
        sma_50=None,
        volatility_20d=None,
    )

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert any(
        "unavailable" in limitation.lower()
        for limitation in result.limitations
    )


def test_confidence_is_always_bounded():
    snapshot = make_snapshot(
        observations=1,
        sma_20=None,
        sma_50=None,
        ema_20=None,
        ema_50=None,
        rsi_14=None,
        macd=None,
        macd_signal=None,
        macd_histogram=None,
        volatility_20d=None,
        support_levels=[],
        resistance_levels=[],
    )

    result = TechnicalConfidenceCalculator().calculate(snapshot)

    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.history_score <= 1.0
    assert 0.0 <= result.trend_score <= 1.0
    assert 0.0 <= result.momentum_score <= 1.0
    assert 0.0 <= result.volatility_score <= 1.0
    assert 0.0 <= result.levels_score <= 1.0