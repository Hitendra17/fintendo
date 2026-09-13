from fintendo.agents.research.fundamental.agent import FundamentalAgent
from fintendo.data.market_client import MarketDataClient
from fintendo.models.fundamental import FundamentalSnapshot
from fintendo.models.research import FundamentalAnalysis
from fintendo.quant.fundamental_engine import FundamentalEngine


class FundamentalResearchService:
    """
    Orchestrates the complete fundamental research pipeline.

    The service coordinates financial data retrieval, deterministic
    fundamental calculations, and LLM-based fundamental interpretation.
    """

    def __init__(
        self,
        market_data_client: MarketDataClient,
        fundamental_engine: FundamentalEngine,
        fundamental_agent: FundamentalAgent,
    ) -> None:
        self.market_data_client = market_data_client
        self.fundamental_engine = fundamental_engine
        self.fundamental_agent = fundamental_agent

    def analyze(
        self,
        ticker: str,
        company_name: str,
    ) -> FundamentalAnalysis:
        statements = self.market_data_client.get_financial_statements(
            ticker=ticker,
        )

        snapshot: FundamentalSnapshot = (
            self.fundamental_engine.calculate(
                ticker=ticker,
                company_name=company_name,
                statements=statements,
            )
        )

        return self.fundamental_agent.analyze(
            snapshot=snapshot,
        )