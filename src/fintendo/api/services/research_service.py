from fintendo.api.dependencies import (
    get_committee_research_service,
    get_profile_resolver,
)
from fintendo.models.research import ResearchReport


class APIResearchService:
    def __init__(self) -> None:
        self.research_service = get_committee_research_service()
        self.profile_resolver = get_profile_resolver()

    def research(
        self,
        ticker: str,
        rag_query: str | None = None,
        rag_top_k: int = 5,
        technical_period: str = "1y",
        technical_interval: str = "1d",
    ) -> ResearchReport:
        normalized_ticker = ticker.strip().upper()

        if not normalized_ticker:
            raise ValueError("ticker must not be empty.")

        profile = self.profile_resolver.resolve(
            normalized_ticker,
        )

        return self.research_service.research_report(
            ticker=profile.ticker,
            company_name=profile.company_name,
            rag_query=rag_query,
            rag_top_k=rag_top_k,
            technical_period=technical_period,
            technical_interval=technical_interval,
        )