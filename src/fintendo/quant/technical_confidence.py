from fintendo.models.technical import TechnicalSnapshot
from fintendo.models.technical_confidence import TechnicalConfidence


class TechnicalConfidenceCalculator:
    TREND_FIELDS = (
        "sma_20",
        "sma_50",
        "ema_20",
        "ema_50",
    )

    MOMENTUM_FIELDS = (
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_histogram",
    )

    def calculate(
        self,
        snapshot: TechnicalSnapshot,
    ) -> TechnicalConfidence:
        history_score = self._history_score(snapshot.observations)

        trend_score = self._trend_score(snapshot)
        momentum_score = self._momentum_score(snapshot)
        volatility_score = self._volatility_score(snapshot)
        levels_score = self._levels_score(snapshot)

        raw_score = (
            (history_score * 0.15)
            + (trend_score * 0.25)
            + (momentum_score * 0.30)
            + (volatility_score * 0.15)
            + (levels_score * 0.15)
        )

        confidence_ceiling = self._history_confidence_ceiling(
            snapshot.observations
        )

        score = min(raw_score, confidence_ceiling)

        missing_indicators = self._missing_indicators(snapshot)
        limitations = self._build_limitations(
            snapshot,
            missing_indicators,
        )

        return TechnicalConfidence(
            score=score,
            observations=snapshot.observations,
            history_score=history_score,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            levels_score=levels_score,
            missing_indicators=missing_indicators,
            limitations=limitations,
        )

    @staticmethod
    def _history_score(observations: int) -> float:
        if observations < 20:
            return 0.20

        if observations < 50:
            return 0.20 + (
                (observations - 20) / 30
            ) * 0.30

        if observations < 100:
            return 0.50 + (
                (observations - 50) / 50
            ) * 0.25

        if observations < 200:
            return 0.75 + (
                (observations - 100) / 100
            ) * 0.15

        return 1.0

    @staticmethod
    def _history_confidence_ceiling(observations: int) -> float:
        if observations < 20:
            return 0.40

        if observations < 50:
            return 0.65

        if observations < 100:
            return 0.80

        if observations < 200:
            return 0.90

        return 1.0

    @classmethod
    def _trend_score(
        cls,
        snapshot: TechnicalSnapshot,
    ) -> float:
        available = sum(
            getattr(snapshot, field) is not None
            for field in cls.TREND_FIELDS
        )

        return available / len(cls.TREND_FIELDS)

    @classmethod
    def _momentum_score(
        cls,
        snapshot: TechnicalSnapshot,
    ) -> float:
        available = sum(
            getattr(snapshot, field) is not None
            for field in cls.MOMENTUM_FIELDS
        )

        return available / len(cls.MOMENTUM_FIELDS)

    @staticmethod
    def _volatility_score(
        snapshot: TechnicalSnapshot,
    ) -> float:
        return 1.0 if snapshot.volatility_20d is not None else 0.0

    @staticmethod
    def _levels_score(
        snapshot: TechnicalSnapshot,
    ) -> float:
        support_available = len(snapshot.support_levels) > 0
        resistance_available = len(snapshot.resistance_levels) > 0

        available_groups = sum(
            [
                support_available,
                resistance_available,
            ]
        )

        return available_groups / 2

    @classmethod
    def _missing_indicators(
        cls,
        snapshot: TechnicalSnapshot,
    ) -> list[str]:
        fields = (
            cls.TREND_FIELDS
            + cls.MOMENTUM_FIELDS
            + ("volatility_20d",)
        )

        return [
            field
            for field in fields
            if getattr(snapshot, field) is None
        ]

    @staticmethod
    def _build_limitations(
        snapshot: TechnicalSnapshot,
        missing_indicators: list[str],
    ) -> list[str]:
        limitations: list[str] = []

        if snapshot.observations < 20:
            limitations.append(
                "Very limited price history; several technical indicators "
                "may not be meaningful."
            )
        elif snapshot.observations < 50:
            limitations.append(
                "Limited price history; longer-period indicators have "
                "reduced reliability."
            )
        elif snapshot.observations < 100:
            limitations.append(
                "Moderate price history; longer-term technical signals "
                "should be interpreted cautiously."
            )

        if missing_indicators:
            limitations.append(
                "One or more technical indicators are unavailable: "
                + ", ".join(missing_indicators)
                + "."
            )

        if not snapshot.support_levels:
            limitations.append(
                "No support levels were identified."
            )

        if not snapshot.resistance_levels:
            limitations.append(
                "No resistance levels were identified."
            )

        return limitations