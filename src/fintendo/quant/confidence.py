from statistics import median

from fintendo.models.fundamental import FundamentalSnapshot


class FundamentalConfidenceCalculator:
    """
    Deterministic confidence calculator for fundamental analysis.

    Confidence measures the quality and completeness of the evidence
    available to the analysis. It does not measure whether the
    investment conclusion itself is correct.
    """

    CRITICAL_WEIGHTS = {
        "revenue": 1.00,
        "net_income": 1.00,
        "operating_income": 0.90,
        "operating_cash_flow": 0.90,
        "free_cash_flow": 0.90,
        "total_assets": 0.70,
        "stockholders_equity": 0.80,
        "total_debt": 0.80,
    }

    def calculate(
        self,
        snapshot: FundamentalSnapshot,
    ) -> float:
        critical_confidence = self._critical_confidence(snapshot)

        optional_confidences = [
            self._growth_confidence(snapshot),
            self._profitability_confidence(snapshot),
            self._cash_flow_confidence(snapshot),
            self._balance_sheet_confidence(snapshot),
            self._historical_confidence(snapshot),
        ]

        optional_confidence = median(optional_confidences)

        return round(
            min(critical_confidence, optional_confidence),
            4,
        )

    def _critical_confidence(
        self,
        snapshot: FundamentalSnapshot,
    ) -> float:
        weighted_available = 0.0
        total_weight = 0.0

        for field, weight in self.CRITICAL_WEIGHTS.items():
            total_weight += weight

            if getattr(snapshot, field) is not None:
                weighted_available += weight

        return weighted_available / total_weight

    @staticmethod
    def _growth_confidence(
        snapshot: FundamentalSnapshot,
    ) -> float:
        fields = (
            snapshot.revenue_yoy_growth,
            snapshot.net_income_yoy_growth,
        )

        return sum(
            value is not None for value in fields
        ) / len(fields)

    @staticmethod
    def _profitability_confidence(
        snapshot: FundamentalSnapshot,
    ) -> float:
        fields = (
            snapshot.operating_margin,
            snapshot.net_income_margin,
            snapshot.return_on_equity,
            snapshot.return_on_assets,
        )

        return sum(
            value is not None for value in fields
        ) / len(fields)

    @staticmethod
    def _cash_flow_confidence(
        snapshot: FundamentalSnapshot,
    ) -> float:
        fields = (
            snapshot.operating_cash_flow,
            snapshot.operating_cash_flow_margin,
            snapshot.free_cash_flow,
            snapshot.free_cash_flow_margin,
            snapshot.free_cash_flow_growth,
            snapshot.free_cash_flow_conversion,
        )

        return sum(
            value is not None for value in fields
        ) / len(fields)

    @staticmethod
    def _balance_sheet_confidence(
        snapshot: FundamentalSnapshot,
    ) -> float:
        fields = (
            snapshot.total_assets,
            snapshot.stockholders_equity,
            snapshot.total_debt,
            snapshot.current_assets,
            snapshot.current_liabilities,
            snapshot.debt_to_equity,
            snapshot.current_ratio,
            snapshot.net_debt_to_operating_income,
        )

        return sum(
            value is not None for value in fields
        ) / len(fields)

    @staticmethod
    def _historical_confidence(
        snapshot: FundamentalSnapshot,
    ) -> float:
        fields = (
            snapshot.revenue_cagr,
            snapshot.net_income_cagr,
        )

        return sum(
            value is not None for value in fields
        ) / len(fields)