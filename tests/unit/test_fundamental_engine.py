import pandas as pd
import pytest

from fintendo.quant.fundamental_engine import FundamentalEngine


def make_statements() -> dict[str, pd.DataFrame]:
    period_1 = pd.Timestamp("2026-03-31")
    period_2 = pd.Timestamp("2025-03-31")

    income = pd.DataFrame(
        {
            period_1: [1000, 200, 150],
            period_2: [900, 180, 140],
        },
        index=[
            "Total Revenue",
            "Operating Income",
            "Net Income",
        ],
    )

    balance = pd.DataFrame(
        {
            period_1: [2000, 1200, 100, 800, 400, 300],
            period_2: [1900, 1100, 120, 750, 380, 250],
        },
        index=[
            "Total Assets",
            "Stockholders Equity",
            "Total Debt",
            "Current Assets",
            "Current Liabilities",
            "Cash And Cash Equivalents",
        ],
    )

    cash_flow = pd.DataFrame(
        {
            period_1: [180, -30, 150],
            period_2: [160, -25, 135],
        },
        index=[
            "Operating Cash Flow",
            "Capital Expenditure",
            "Free Cash Flow",
        ],
    )

    return {
        "income_statement": income,
        "balance_sheet": balance,
        "cash_flow": cash_flow,
    }


def test_engine_calculates_expected_metrics():
    statements = make_statements()

    snapshot = FundamentalEngine().calculate(
        "TCS",
        "Tata Consultancy Services Limited",
        statements,
    )

    assert snapshot.revenue == 1000
    assert snapshot.operating_income == 200
    assert snapshot.net_income == 150

    assert snapshot.revenue_yoy_growth == pytest.approx(100 / 900)
    assert snapshot.net_income_yoy_growth == pytest.approx(10 / 140)

    assert snapshot.operating_margin == pytest.approx(0.20)
    assert snapshot.net_income_margin == pytest.approx(0.15)

    assert snapshot.free_cash_flow == 150
    assert snapshot.free_cash_flow_conversion == pytest.approx(1.0)

    assert snapshot.debt_to_equity == pytest.approx(100 / 1200)
    assert snapshot.current_ratio == pytest.approx(2.0)


def test_missing_revenue_raises_error():
    statements = make_statements()

    statements["income_statement"] = statements["income_statement"].drop(
        index="Total Revenue"
    )

    with pytest.raises(ValueError, match="Revenue data is unavailable"):
        FundamentalEngine().calculate(
            "TCS",
            "Tata Consultancy Services Limited",
            statements,
        )


def test_missing_optional_metric_does_not_crash():
    statements = make_statements()

    statements["cash_flow"] = statements["cash_flow"].drop(
        index="Free Cash Flow"
    )

    snapshot = FundamentalEngine().calculate(
        "TCS",
        "Tata Consultancy Services Limited",
        statements,
    )

    assert snapshot.free_cash_flow is None
    assert snapshot.free_cash_flow_margin is None
    assert snapshot.free_cash_flow_conversion is None


def test_zero_equity_does_not_create_invalid_debt_to_equity():
    statements = make_statements()

    statements["balance_sheet"].loc[
        "Stockholders Equity"
    ] = [0, 0]

    snapshot = FundamentalEngine().calculate(
        "TCS",
        "Tata Consultancy Services Limited",
        statements,
    )

    assert snapshot.debt_to_equity is None


def test_zero_current_liabilities_does_not_create_invalid_current_ratio():
    statements = make_statements()

    statements["balance_sheet"].loc[
        "Current Liabilities"
    ] = [0, 0]

    snapshot = FundamentalEngine().calculate(
        "TCS",
        "Tata Consultancy Services Limited",
        statements,
    )

    assert snapshot.current_ratio is None


def test_missing_cash_does_not_create_net_debt_ratio():
    statements = make_statements()

    statements["balance_sheet"] = statements["balance_sheet"].drop(
        index="Cash And Cash Equivalents"
    )

    snapshot = FundamentalEngine().calculate(
        "TCS",
        "Tata Consultancy Services Limited",
        statements,
    )

    assert snapshot.net_debt_to_operating_income is None