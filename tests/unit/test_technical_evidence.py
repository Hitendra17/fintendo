from datetime import datetime, timezone

from fintendo.models.technical import TechnicalSnapshot
from fintendo.models.technical_evidence import TechnicalEvidenceType
from fintendo.quant.technical_evidence import TechnicalEvidenceBuilder


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


def test_builder_creates_scalar_evidence():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    fields = {item.field for item in evidence}

    assert "close" in fields
    assert "sma_20" in fields
    assert "sma_50" in fields
    assert "rsi_14" in fields
    assert "macd" in fields
    assert "volatility_20d" in fields


def test_builder_creates_support_and_resistance_evidence():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    fields = {item.field for item in evidence}

    assert "support_level_1" in fields
    assert "support_level_2" in fields
    assert "resistance_level_1" in fields
    assert "resistance_level_2" in fields


def test_level_evidence_preserves_values():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    evidence_by_field = {item.field: item for item in evidence}

    assert evidence_by_field["support_level_1"].value == 3400.0
    assert evidence_by_field["support_level_2"].value == 3300.0
    assert evidence_by_field["resistance_level_1"].value == 3600.0
    assert evidence_by_field["resistance_level_2"].value == 3700.0


def test_builder_skips_unavailable_indicators():
    snapshot = make_snapshot(
        sma_50=None,
        rsi_14=None,
        volatility_20d=None,
    )

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    fields = {item.field for item in evidence}

    assert "sma_50" not in fields
    assert "rsi_14" not in fields
    assert "volatility_20d" not in fields


def test_builder_classifies_evidence_types():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    evidence_by_field = {item.field: item for item in evidence}

    assert (
        evidence_by_field["close"].evidence_type
        == TechnicalEvidenceType.OBSERVED
    )

    assert (
        evidence_by_field["rsi_14"].evidence_type
        == TechnicalEvidenceType.DERIVED
    )

    assert (
        evidence_by_field["support_level_1"].evidence_type
        == TechnicalEvidenceType.LEVEL
    )


def test_builder_preserves_snapshot_timestamp():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    assert all(item.period == snapshot.as_of for item in evidence)


def test_builder_uses_technical_engine_as_source():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    assert all(item.source == "TechnicalEngine" for item in evidence)


def test_builder_does_not_create_interpretation():
    snapshot = make_snapshot()

    evidence = TechnicalEvidenceBuilder().build(snapshot)

    descriptions = [item.description.lower() for item in evidence]

    assert not any("bullish" in description for description in descriptions)
    assert not any("bearish" in description for description in descriptions)
    assert not any("buy" in description for description in descriptions)
    assert not any("sell" in description for description in descriptions)