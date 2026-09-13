from datetime import datetime

import pandas as pd

from fintendo.models.technical import TechnicalSnapshot
from fintendo.quant.indicators.levels import (
    resistance_levels,
    support_levels,
)
from fintendo.quant.indicators.momentum import macd, rsi
from fintendo.quant.indicators.trend import ema, sma
from fintendo.quant.indicators.volatility import historical_volatility


class TechnicalEngine:
    """
    Deterministic technical analysis engine.

    Calculates technical indicators and market levels from historical
    price data. This class does not use an LLM and does not perform
    qualitative interpretation.
    """

    REQUIRED_COLUMNS = {"High", "Low", "Close"}

    def calculate(
        self,
        ticker: str,
        price_history: pd.DataFrame,
    ) -> TechnicalSnapshot:
        self._validate_price_history(price_history)

        prices = price_history["Close"]

        sma_20 = sma(prices, 20)
        sma_50 = sma(prices, 50)

        ema_20 = ema(prices, 20)
        ema_50 = ema(prices, 50)

        rsi_14 = rsi(prices, 14)

        macd_data = macd(prices)

        volatility_20d = historical_volatility(prices)

        current_price = float(prices.iloc[-1])

        supports = support_levels(
            price_history["Low"],
            current_price,
        )

        resistances = resistance_levels(
            price_history["High"],
            current_price,
        )

        latest_sma_20 = self._latest_value(sma_20)
        latest_sma_50 = self._latest_value(sma_50)

        latest_ema_20 = self._latest_value(ema_20)
        latest_ema_50 = self._latest_value(ema_50)

        latest_rsi_14 = self._latest_value(rsi_14)

        latest_macd = self._latest_value(
            macd_data["macd"]
        )
        latest_signal = self._latest_value(
            macd_data["signal"]
        )
        latest_histogram = self._latest_value(
            macd_data["histogram"]
        )

        latest_volatility = self._latest_value(
            volatility_20d
        )

        price_vs_sma_20_pct = self._percentage_difference(
            current_price,
            latest_sma_20,
        )

        price_vs_sma_50_pct = self._percentage_difference(
            current_price,
            latest_sma_50,
        )

        price_vs_ema_20_pct = self._percentage_difference(
            current_price,
            latest_ema_20,
        )

        price_vs_ema_50_pct = self._percentage_difference(
            current_price,
            latest_ema_50,
        )

        macd_spread = None

        if (
            latest_macd is not None
            and latest_signal is not None
        ):
            macd_spread = latest_macd - latest_signal

        distance_to_support_pct = self._distance_to_level(
            current_price,
            supports[0] if supports else None,
        )

        distance_to_resistance_pct = self._distance_to_level(
            current_price,
            resistances[0] if resistances else None,
        )

        return TechnicalSnapshot(
            ticker=ticker.upper(),
            as_of=self._latest_timestamp(price_history),
            observations=len(price_history),
            close=current_price,
            sma_20=latest_sma_20,
            sma_50=latest_sma_50,
            ema_20=latest_ema_20,
            ema_50=latest_ema_50,
            rsi_14=latest_rsi_14,
            macd=latest_macd,
            macd_signal=latest_signal,
            macd_histogram=latest_histogram,
            support_levels=supports,
            resistance_levels=resistances,
            volatility_20d=latest_volatility,
            price_vs_sma_20_pct=price_vs_sma_20_pct,
            price_vs_sma_50_pct=price_vs_sma_50_pct,
            price_vs_ema_20_pct=price_vs_ema_20_pct,
            price_vs_ema_50_pct=price_vs_ema_50_pct,
            macd_spread=macd_spread,
            distance_to_support_pct=distance_to_support_pct,
            distance_to_resistance_pct=distance_to_resistance_pct,
        )

    @classmethod
    def _validate_price_history(
        cls,
        price_history: pd.DataFrame,
    ) -> None:
        if price_history.empty:
            raise ValueError("Price history is empty.")

        missing_columns = (
            cls.REQUIRED_COLUMNS
            - set(price_history.columns)
        )

        if missing_columns:
            raise ValueError(
                "Price history is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        required_data = price_history[
            list(cls.REQUIRED_COLUMNS)
        ]

        if required_data.isna().any().any():
            raise ValueError(
                "Price history contains missing values."
            )

        if not required_data.map(
            pd.api.types.is_number
        ).all().all():
            raise ValueError(
                "Price history contains non-numeric values."
            )

        if (price_history["Close"] <= 0).any():
            raise ValueError(
                "Close prices must be greater than zero."
            )

        if (price_history["High"] <= 0).any():
            raise ValueError(
                "High prices must be greater than zero."
            )

        if (price_history["Low"] <= 0).any():
            raise ValueError(
                "Low prices must be greater than zero."
            )

    @staticmethod
    def _latest_value(
        series: pd.Series,
    ) -> float | None:
        value = series.iloc[-1]

        if pd.isna(value):
            return None

        value = float(value)

        if not pd.api.types.is_number(value):
            raise ValueError(
                "Technical indicator contains a non-numeric value."
            )

        return value

    @staticmethod
    def _percentage_difference(
        current_price: float,
        reference_price: float | None,
    ) -> float | None:
        if reference_price is None or reference_price == 0:
            return None

        return (
            (current_price - reference_price)
            / reference_price
        ) * 100

    @staticmethod
    def _distance_to_level(
        current_price: float,
        level: float | None,
    ) -> float | None:
        if level is None or current_price == 0:
            return None

        return abs(
            (current_price - level)
            / current_price
        ) * 100

    @staticmethod
    def _latest_timestamp(
        price_history: pd.DataFrame,
    ) -> datetime:
        timestamp = price_history.index[-1]

        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

        if not isinstance(timestamp, datetime):
            raise ValueError(
                "Price history index must contain datetime values."
            )

        return timestamp