from fintendo.agents.research.technical.agent import TechnicalAgent
from fintendo.data.market_client import MarketDataClient
from fintendo.models.research import TechnicalAnalysis
from fintendo.quant.technical_confidence import TechnicalConfidenceCalculator
from fintendo.quant.technical_engine import TechnicalEngine
from fintendo.quant.technical_evidence import TechnicalEvidenceBuilder


class TechnicalResearchService:
    """
    Orchestrates the complete technical research pipeline.

    The service coordinates deterministic quantitative calculations,
    evidence construction, confidence calculation, and LLM-based
    technical interpretation.
    """

    def __init__(
        self,
        market_data_client: MarketDataClient,
        technical_engine: TechnicalEngine,
        evidence_builder: TechnicalEvidenceBuilder,
        confidence_calculator: TechnicalConfidenceCalculator,
        technical_agent: TechnicalAgent,
    ) -> None:
        self.market_data_client = market_data_client
        self.technical_engine = technical_engine
        self.evidence_builder = evidence_builder
        self.confidence_calculator = confidence_calculator
        self.technical_agent = technical_agent

    def analyze(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> TechnicalAnalysis:
        price_history = self.market_data_client.get_price_history(
            ticker=ticker,
            period=period,
            interval=interval,
        )

        snapshot = self.technical_engine.calculate(
            ticker=ticker,
            price_history=price_history,
        )

        evidence = self.evidence_builder.build(snapshot)

        confidence = self.confidence_calculator.calculate(snapshot)

        return self.technical_agent.analyze(
            snapshot=snapshot,
            evidence=evidence,
            confidence=confidence,
        )