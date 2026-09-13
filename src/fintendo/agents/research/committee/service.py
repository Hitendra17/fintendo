from datetime import datetime, timezone

from fintendo.agents.research.committee.agent import CommitteeAgent
from fintendo.agents.research.fundamental.service import (
    FundamentalResearchService,
)
from fintendo.agents.research.market_intelligence.service import (
    MarketIntelligenceService,
)
from fintendo.agents.research.technical.service import (
    TechnicalResearchService,
)
from fintendo.models.research import CommitteeDecision, ResearchReport


class CommitteeResearchService:
    """
    Orchestrates Fintendo Research's complete research pipeline.

    Flow:

        ticker
          ↓
        Fundamental Research ──┐
                               │
        Technical Research ────┼──> Committee Agent
                               │
        Market Intelligence ───┘
                               ↓
                       CommitteeDecision

    The service coordinates the specialist research layers and passes
    their completed structured outputs to the Committee Agent.

    It does not perform financial calculations or independent research.
    """

    def __init__(
        self,
        fundamental_service: FundamentalResearchService,
        technical_service: TechnicalResearchService,
        market_intelligence_service: MarketIntelligenceService,
        committee_agent: CommitteeAgent,
    ) -> None:
        self.fundamental_service = fundamental_service
        self.technical_service = technical_service
        self.market_intelligence_service = market_intelligence_service
        self.committee_agent = committee_agent

    def research(
        self,
        ticker: str,
        company_name: str,
        rag_query: str | None = None,
        rag_top_k: int = 5,
        technical_period: str = "1y",
        technical_interval: str = "1d",
    ) -> CommitteeDecision:
        """
        Run the complete Fintendo Research workflow and return the
        final committee decision.

        The specialist analyses are executed exactly once.
        """

        return self.research_report(
            ticker=ticker,
            company_name=company_name,
            rag_query=rag_query,
            rag_top_k=rag_top_k,
            technical_period=technical_period,
            technical_interval=technical_interval,
        ).committee

    def research_report(
        self,
        ticker: str,
        company_name: str,
        rag_query: str | None = None,
        rag_top_k: int = 5,
        technical_period: str = "1y",
        technical_interval: str = "1d",
    ) -> ResearchReport:
        """
        Run the complete Fintendo Research workflow and return the
        complete research report.

        The specialist analyses and committee decision are produced
        from a single execution of each research layer.
        """

        normalized_ticker = ticker.strip().upper()

        if not normalized_ticker:
            raise ValueError("ticker must not be empty.")

        if not company_name.strip():
            raise ValueError("company_name must not be empty.")

        if rag_top_k <= 0:
            raise ValueError("rag_top_k must be positive.")

        fundamental = self.fundamental_service.analyze(
            ticker=normalized_ticker,
            company_name=company_name.strip(),
        )

        technical = self.technical_service.analyze(
            ticker=normalized_ticker,
            period=technical_period,
            interval=technical_interval,
        )

        market_intelligence = self.market_intelligence_service.research(
            ticker=normalized_ticker,
            rag_query=rag_query,
            top_k=rag_top_k,
        )

        committee = self.committee_agent.decide(
            fundamental=fundamental,
            technical=technical,
            market_intelligence=market_intelligence,
        )

        return ResearchReport(
            ticker=normalized_ticker,
            generated_at=datetime.now(timezone.utc),
            fundamental=fundamental,
            technical=technical,
            market_intelligence=market_intelligence,
            committee=committee,
        )