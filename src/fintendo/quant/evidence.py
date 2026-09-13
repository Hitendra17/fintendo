from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.models.research import FundamentalEvidence


class FundamentalEvidenceBuilder:
    """
    Builds deterministic evidence from a FundamentalSnapshot.

    The builder never invents values. Every evidence item is directly
    derived from a field in the validated snapshot.
    """

    SOURCE = "Fintendo Fundamental Engine"

    def build(
        self,
        snapshot: FundamentalSnapshot,
    ) -> list[FundamentalEvidence]:
        evidence: list[FundamentalEvidence] = []

        self._add_numeric_evidence(
            evidence,
            snapshot,
            "revenue",
            "Revenue",
            "Reported revenue for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "operating_income",
            "Operating income",
            "Reported operating income for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "net_income",
            "Net income",
            "Reported net income for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "total_assets",
            "Total assets",
            "Reported total assets for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "stockholders_equity",
            "Stockholders' equity",
            "Reported stockholders' equity for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "total_debt",
            "Total debt",
            "Reported total debt for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "operating_cash_flow",
            "Operating cash flow",
            "Reported operating cash flow for the latest financial period.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "free_cash_flow",
            "Free cash flow",
            "Derived free cash flow for the latest financial period.",
        )

        self._add_numeric_evidence(
            evidence,
            snapshot,
            "revenue_yoy_growth",
            "Revenue YoY growth",
            "Year-over-year revenue growth.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "net_income_yoy_growth",
            "Net income YoY growth",
            "Year-over-year net income growth.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "revenue_cagr",
            "Revenue CAGR",
            "Historical compound annual revenue growth.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "net_income_cagr",
            "Net income CAGR",
            "Historical compound annual net income growth.",
        )

        self._add_numeric_evidence(
            evidence,
            snapshot,
            "operating_margin",
            "Operating margin",
            "Operating income as a percentage of revenue.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "net_income_margin",
            "Net income margin",
            "Net income as a percentage of revenue.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "return_on_equity",
            "Return on equity",
            "Return generated relative to stockholders' equity.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "return_on_assets",
            "Return on assets",
            "Return generated relative to total assets.",
        )

        self._add_numeric_evidence(
            evidence,
            snapshot,
            "operating_cash_flow_margin",
            "Operating cash flow margin",
            "Operating cash flow as a percentage of revenue.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "free_cash_flow_margin",
            "Free cash flow margin",
            "Free cash flow as a percentage of revenue.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "free_cash_flow_growth",
            "Free cash flow growth",
            "Growth in free cash flow.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "free_cash_flow_conversion",
            "Free cash flow conversion",
            "Free cash flow relative to operating cash flow.",
        )

        self._add_numeric_evidence(
            evidence,
            snapshot,
            "debt_to_equity",
            "Debt to equity",
            "Total debt relative to stockholders' equity.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "current_ratio",
            "Current ratio",
            "Current assets relative to current liabilities.",
        )
        self._add_numeric_evidence(
            evidence,
            snapshot,
            "net_debt_to_operating_income",
            "Net debt to operating income",
            "Net debt relative to operating income.",
        )

        return evidence

    def _add_numeric_evidence(
        self,
        evidence: list[FundamentalEvidence],
        snapshot: FundamentalSnapshot,
        field: str,
        description_name: str,
        description: str,
    ) -> None:
        value = getattr(snapshot, field)

        if value is None:
            return

        evidence.append(
            FundamentalEvidence(
                source=self.SOURCE,
                field=field,
                value=float(value),
                period=snapshot.as_of,
                description=f"{description_name}: {description}",
            )
        )