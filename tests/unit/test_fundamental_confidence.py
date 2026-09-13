from datetime import datetime

from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.quant.confidence import FundamentalConfidenceCalculator


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


def test_complete_snapshot_has_full_confidence():
    snapshot = make_complete_snapshot()

    confidence = FundamentalConfidenceCalculator().calculate(snapshot)

    assert confidence == 1.0


def test_missing_free_cash_flow_reduces_confidence():
    snapshot = make_complete_snapshot()
    snapshot.free_cash_flow = None
    snapshot.free_cash_flow_margin = None
    snapshot.free_cash_flow_growth = None
    snapshot.free_cash_flow_conversion = None

    confidence = FundamentalConfidenceCalculator().calculate(snapshot)

    assert 0 < confidence < 1.0


def test_missing_critical_data_caps_confidence():
    snapshot = make_complete_snapshot()

    snapshot.revenue = None
    snapshot.net_income = None
    snapshot.operating_income = None
    snapshot.operating_cash_flow = None
    snapshot.free_cash_flow = None

    confidence = FundamentalConfidenceCalculator().calculate(snapshot)

    assert confidence < 0.5


def test_confidence_is_bounded():
    snapshot = make_complete_snapshot()

    confidence = FundamentalConfidenceCalculator().calculate(snapshot)

    assert 0.0 <= confidence <= 1.0