from unittest.mock import Mock

from fintendo.agents.research.fundamental.service import (
    FundamentalResearchService,
)
from fintendo.models.research import FundamentalAnalysis


def test_fundamental_research_service_orchestrates_pipeline():
    financial_data_client = Mock()
    fundamental_engine = Mock()
    fundamental_agent = Mock()

    statements = {
        "income_statement": Mock(),
        "balance_sheet": Mock(),
        "cash_flow": Mock(),
    }

    snapshot = Mock()

    expected_analysis = Mock(spec=FundamentalAnalysis)

    financial_data_client.get_financial_statements.return_value = statements
    fundamental_engine.calculate.return_value = snapshot
    fundamental_agent.analyze.return_value = expected_analysis

    service = FundamentalResearchService(
        market_data_client=financial_data_client,
        fundamental_engine=fundamental_engine,
        fundamental_agent=fundamental_agent,
    )

    result = service.analyze(
        ticker="TCS",
        company_name="Tata Consultancy Services",
    )

    assert result is expected_analysis

    financial_data_client.get_financial_statements.assert_called_once_with(
        ticker="TCS",
    )

    fundamental_engine.calculate.assert_called_once_with(
        ticker="TCS",
        company_name="Tata Consultancy Services",
        statements=statements,
    )

    fundamental_agent.analyze.assert_called_once_with(
        snapshot=snapshot,
    )