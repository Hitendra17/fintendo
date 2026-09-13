from datetime import datetime
from unittest.mock import Mock

from fintendo.agents.research.fundamental.agent import FundamentalAgent
from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.models.research import FundamentalAnalysisOutput


def make_snapshot() -> FundamentalSnapshot:
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


def test_agent_uses_deterministic_evidence_and_confidence():
    llm = Mock()

    llm.generate_structured.return_value = FundamentalAnalysisOutput(
        ticker="TCS",
        score=90,
        summary="Strong fundamentals.",
        strengths=["Strong profitability"],
        weaknesses=["Earnings growth is slower than revenue growth"],
        catalysts=["Improved earnings growth"],
        risks=["Slower earnings growth"],
    )

    agent = FundamentalAgent(llm)

    result = agent.analyze(make_snapshot())

    assert result.evidence
    assert result.confidence == 1.0

    assert result.evidence[0].source == "Fintendo Fundamental Engine"


def test_agent_cannot_accept_llm_generated_evidence_or_confidence():
    llm = Mock()

    llm.generate_structured.return_value = FundamentalAnalysisOutput(
        ticker="TCS",
        score=90,
        summary="Strong fundamentals.",
        strengths=["Strong profitability"],
        weaknesses=[],
        catalysts=[],
        risks=[],
    )

    agent = FundamentalAgent(llm)

    result = agent.analyze(make_snapshot())

    llm_result = llm.generate_structured.return_value

    assert not hasattr(llm_result, "evidence")
    assert not hasattr(llm_result, "confidence")

    assert result.evidence
    assert result.confidence == 1.0


def test_agent_preserves_llm_interpretation():
    llm = Mock()

    expected = FundamentalAnalysisOutput(
        ticker="TCS",
        score=73,
        summary="Mixed fundamental picture.",
        strengths=["Positive cash generation"],
        weaknesses=["Moderate growth"],
        catalysts=["Improving cash flow"],
        risks=["Slower earnings growth"],
    )

    llm.generate_structured.return_value = expected

    agent = FundamentalAgent(llm)

    result = agent.analyze(make_snapshot())

    assert result.score == 73
    assert result.summary == "Mixed fundamental picture."
    assert result.strengths == ["Positive cash generation"]
    assert result.weaknesses == ["Moderate growth"]
    assert result.catalysts == ["Improving cash flow"]
    assert result.risks == ["Slower earnings growth"]
    