from datetime import datetime

from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.quant.evidence import FundamentalEvidenceBuilder


def make_complete_snapshot() -> FundamentalSnapshot:
    return FundamentalSnapshot(
        ticker="TCS",
        company_name="Tata Consultancy Services Limited",
        as_of=datetime(2026, 3, 31),
        revenue=1000,
        operating_income=200,
        net_income=150,
        total_assets=2000,
        stockholders_equity=1200,
        total_debt=100,
        current_assets=800,
        current_liabilities=400,
        operating_cash_flow=180,
        capital_expenditure=-30,
        free_cash_flow=150,
        revenue_yoy_growth=0.08,
        net_income_yoy_growth=0.06,
        revenue_cagr=0.07,
        net_income_cagr=0.06,
        operating_margin=0.20,
        net_income_margin=0.15,
        return_on_equity=0.125,
        return_on_assets=0.075,
        operating_cash_flow_margin=0.18,
        free_cash_flow_margin=0.15,
        free_cash_flow_growth=0.10,
        free_cash_flow_conversion=1.0,
        debt_to_equity=0.083,
        current_ratio=2.0,
        net_debt_to_operating_income=0.25,
    )


def test_complete_snapshot_generates_evidence_for_every_available_metric():
    snapshot = make_complete_snapshot()

    evidence = FundamentalEvidenceBuilder().build(snapshot)

    assert len(evidence) == 23


def test_evidence_values_match_snapshot():
    snapshot = make_complete_snapshot()

    evidence = FundamentalEvidenceBuilder().build(snapshot)

    evidence_by_field = {item.field: item for item in evidence}

    assert evidence_by_field["revenue"].value == snapshot.revenue
    assert evidence_by_field["net_income"].value == snapshot.net_income
    assert evidence_by_field["free_cash_flow"].value == snapshot.free_cash_flow
    assert evidence_by_field["debt_to_equity"].value == snapshot.debt_to_equity


def test_evidence_period_matches_snapshot():
    snapshot = make_complete_snapshot()

    evidence = FundamentalEvidenceBuilder().build(snapshot)

    assert all(item.period == snapshot.as_of for item in evidence)


def test_missing_metric_produces_no_evidence_for_that_metric():
    snapshot = make_complete_snapshot()
    snapshot.free_cash_flow = None

    evidence = FundamentalEvidenceBuilder().build(snapshot)

    fields = {item.field for item in evidence}

    assert "free_cash_flow" not in fields