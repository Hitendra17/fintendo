from unittest.mock import Mock

from fintendo.agents.research.fundamental.agent import FundamentalAgent
from fintendo.models.fundamental import FundamentalSnapshot


def make_snapshot() -> FundamentalSnapshot:
    return FundamentalSnapshot(
        ticker="TCS",
        company_name="Tata Consultancy Services Limited",
        as_of="2026-03-31T00:00:00",
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


def test_fundamental_prompt_contains_core_guardrails():
    llm = Mock()
    agent = FundamentalAgent(llm)

    llm.generate_structured.return_value = Mock()

    try:
        agent.analyze(make_snapshot())
    except Exception:
        pass

    prompt = llm.generate_structured.call_args.args[0]

    required_rules = [
        "Use ONLY the supplied FundamentalSnapshot.",
        "Do not invent financial values.",
        "Do not invent company information.",
        "Do not use external knowledge.",
        "Do not assume industry benchmarks",
        "Treat null values as unavailable.",
        "Never infer a missing metric.",
        "Do not make guaranteed predictions.",
        "Do not provide evidence objects.",
        "Do not provide a confidence value.",
    ]

    for rule in required_rules:
        assert rule in prompt


def test_fundamental_prompt_requires_structured_output():
    llm = Mock()
    agent = FundamentalAgent(llm)

    llm.generate_structured.return_value = Mock()

    try:
        agent.analyze(make_snapshot())
    except Exception:
        pass

    prompt = llm.generate_structured.call_args.args[0]

    assert "Return the analysis using the provided structured schema." in prompt