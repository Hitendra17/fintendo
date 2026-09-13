import numpy as np
import pandas as pd
import pytest
from fintendo.models.technical import TechnicalSnapshot
from fintendo.quant.technical_engine import TechnicalEngine


def make_price_history(rows: int = 60) -> pd.DataFrame:
    dates = pd.date_range(
        "2026-01-01",
        periods=rows,
        freq="D",
    )

    close = pd.Series(
        [100 + i for i in range(rows)],
        index=dates,
        dtype=float,
    )

    return pd.DataFrame(
        {
            "Open": close - 1,
            "High": close + 2,
            "Low": close - 2,
            "Close": close,
            "Volume": 100000,
        },
        index=dates,
    )


def test_engine_uses_latest_market_data_timestamp():
    price_history = make_price_history()

    snapshot = TechnicalEngine().calculate(
        "TCS",
        price_history,
    )

    assert snapshot.as_of == price_history.index[-1].to_pydatetime()


def test_engine_requires_close_column():
    price_history = make_price_history().drop(columns=["Close"])

    with pytest.raises(ValueError, match="Close"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_requires_high_and_low_columns():
    price_history = make_price_history().drop(columns=["High"])

    with pytest.raises(ValueError, match="High"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_rejects_empty_price_history():
    price_history = make_price_history().iloc[0:0]

    with pytest.raises(ValueError, match="empty"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_rejects_missing_price_values():
    price_history = make_price_history()

    price_history.loc[
        price_history.index[-1],
        "Close",
    ] = np.nan

    with pytest.raises(ValueError, match="missing"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_rejects_non_positive_prices():
    price_history = make_price_history()

    price_history.loc[
        price_history.index[-1],
        "Close",
    ] = 0

    with pytest.raises(ValueError, match="greater than zero"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_rejects_non_numeric_prices():
    price_history = make_price_history()

    price_history["Close"] = price_history["Close"].astype(object)
    price_history.loc[
        price_history.index[-1],
        "Close",
    ] = "invalid"

    with pytest.raises(ValueError, match="non-numeric"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )


def test_engine_calculates_snapshot_with_sufficient_history():
    price_history = make_price_history()

    snapshot = TechnicalEngine().calculate(
        "TCS",
        price_history,
    )

    assert snapshot.ticker == "TCS"
    assert snapshot.close == pytest.approx(159.0)

    assert snapshot.sma_20 is not None
    assert snapshot.sma_50 is not None
    assert snapshot.ema_20 is not None
    assert snapshot.ema_50 is not None
    assert snapshot.rsi_14 is not None
    assert snapshot.macd is not None
    assert snapshot.macd_signal is not None
    assert snapshot.macd_histogram is not None
    assert snapshot.volatility_20d is not None


def test_engine_handles_insufficient_history_without_crashing():
    price_history = make_price_history(rows=10)

    snapshot = TechnicalEngine().calculate(
        "TCS",
        price_history,
    )

    assert snapshot.close == pytest.approx(109.0)

    assert snapshot.sma_20 is None
    assert snapshot.sma_50 is None
    assert snapshot.rsi_14 is None
    assert snapshot.volatility_20d is None

    assert snapshot.ema_20 is not None
    assert snapshot.ema_50 is not None
    assert snapshot.macd is not None
    assert snapshot.macd_signal is not None
    assert snapshot.macd_histogram is not None


def test_engine_rejects_invalid_timestamp_index():
    price_history = make_price_history()

    price_history.index = range(len(price_history))

    with pytest.raises(ValueError, match="datetime"):
        TechnicalEngine().calculate(
            "TCS",
            price_history,
        )

def test_snapshot_rejects_nan_indicator():
    snapshot_data = {
        "ticker": "TCS",
        "as_of": pd.Timestamp("2026-03-01"),
        "close": 100.0,
        "sma_20": np.nan,
        "support_levels": [],
        "resistance_levels": [],
    }

    with pytest.raises(ValueError, match="finite"):
        TechnicalSnapshot(**snapshot_data)


def test_snapshot_rejects_infinite_indicator():
    snapshot_data = {
        "ticker": "TCS",
        "as_of": pd.Timestamp("2026-03-01"),
        "close": 100.0,
        "macd": np.inf,
        "support_levels": [],
        "resistance_levels": [],
    }

    with pytest.raises(ValueError, match="finite"):
        TechnicalSnapshot(**snapshot_data)


def test_snapshot_rejects_non_finite_levels():
    snapshot_data = {
        "ticker": "TCS",
        "as_of": pd.Timestamp("2026-03-01"),
        "close": 100.0,
        "support_levels": [95.0, np.inf],
        "resistance_levels": [110.0],
    }

    with pytest.raises(ValueError, match="finite"):
        TechnicalSnapshot(**snapshot_data)