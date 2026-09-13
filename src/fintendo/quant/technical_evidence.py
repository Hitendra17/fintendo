from fintendo.models.technical import TechnicalSnapshot
from fintendo.models.technical_evidence import (
    TechnicalEvidence,
    TechnicalEvidenceType,
)


class TechnicalEvidenceBuilder:
    SOURCE = "TechnicalEngine"

    def build(
        self,
        snapshot: TechnicalSnapshot,
    ) -> list[TechnicalEvidence]:
        evidence: list[TechnicalEvidence] = []

        scalar_fields = [
            (
                "observations",
                "Number of historical price observations used to calculate the technical snapshot.",
                TechnicalEvidenceType.OBSERVED,
            ),
            (
                "close",
                "Closing price.",
                TechnicalEvidenceType.OBSERVED,
            ),
            (
                "sma_20",
                "20-period simple moving average.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "sma_50",
                "50-period simple moving average.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "ema_20",
                "20-period exponential moving average.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "ema_50",
                "50-period exponential moving average.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "rsi_14",
                "14-period relative strength index.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "macd",
                "MACD value.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "macd_signal",
                "MACD signal-line value.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "macd_histogram",
                "MACD histogram value.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "volatility_20d",
                "20-day historical volatility.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "price_vs_sma_20_pct",
                "Percentage difference between closing price and 20-period SMA.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "price_vs_sma_50_pct",
                "Percentage difference between closing price and 50-period SMA.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "price_vs_ema_20_pct",
                "Percentage difference between closing price and 20-period EMA.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "price_vs_ema_50_pct",
                "Percentage difference between closing price and 50-period EMA.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "macd_spread",
                "Difference between MACD and its signal line.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "distance_to_support_pct",
                "Percentage distance from the closing price to the nearest identified support level.",
                TechnicalEvidenceType.DERIVED,
            ),
            (
                "distance_to_resistance_pct",
                "Percentage distance from the closing price to the nearest identified resistance level.",
                TechnicalEvidenceType.DERIVED,
            ),
        ]

        for field_name, description, evidence_type in scalar_fields:
            value = getattr(snapshot, field_name)

            if value is None:
                continue

            evidence.append(
                TechnicalEvidence(
                    source=self.SOURCE,
                    field=field_name,
                    evidence_type=evidence_type,
                    value=value,
                    period=snapshot.as_of,
                    description=description,
                )
            )

        evidence.extend(
            self._build_levels(
                levels=snapshot.support_levels,
                prefix="support",
                description="Identified support level below the current price.",
                period=snapshot.as_of,
            )
        )

        evidence.extend(
            self._build_levels(
                levels=snapshot.resistance_levels,
                prefix="resistance",
                description="Identified resistance level above the current price.",
                period=snapshot.as_of,
            )
        )

        return evidence

    def _build_levels(
        self,
        levels: list[float],
        prefix: str,
        description: str,
        period,
    ) -> list[TechnicalEvidence]:
        return [
            TechnicalEvidence(
                source=self.SOURCE,
                field=f"{prefix}_level_{index}",
                evidence_type=TechnicalEvidenceType.LEVEL,
                value=level,
                period=period,
                description=description,
            )
            for index, level in enumerate(levels, start=1)
        ]