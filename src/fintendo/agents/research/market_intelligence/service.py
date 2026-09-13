from fintendo.agents.research.market_intelligence.article_relevance import (
    MarketArticleRelevanceAgent,
)
from fintendo.agents.research.market_intelligence.event_extractor import (
    MarketEventExtractor,
)
from fintendo.agents.research.market_intelligence.synthesis_guardrails import (
    MarketIntelligenceSynthesisGuardrail,
)
from fintendo.agents.research.market_intelligence.synthesizer import (
    MarketIntelligenceSynthesizer,
)
from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.models.market_intelligence import (
    GroundedMarketEvidence,
    MarketIntelligenceAnalysis,
)
from fintendo.rag.retriever import RAGRetriever


class MarketIntelligenceService:
    """
    Orchestrates Fintendo Research's Market Intelligence pipeline.

    Flow:

        ticker
          ↓
        company profile resolution
          ↓
        Gemini + Google Search
          ↓
        grounded market evidence
          ↓
        RAG retrieval
          ↓
        event extraction
          ↓
        synthesis
          ↓
        synthesis guardrails
          ↓
        MarketIntelligenceAnalysis
    """

    def __init__(
        self,
        profile_resolver: CompanyProfileResolver,
        rag_retriever: RAGRetriever,
        event_extractor: MarketEventExtractor,
        synthesizer: MarketIntelligenceSynthesizer,
        synthesis_guardrail: (
            MarketIntelligenceSynthesisGuardrail | None
        ) = None,
        article_search_agent: MarketArticleRelevanceAgent | None = None,
    ) -> None:
        self.profile_resolver = profile_resolver
        self.rag_retriever = rag_retriever
        self.event_extractor = event_extractor
        self.synthesizer = synthesizer

        self.synthesis_guardrail = (
            synthesis_guardrail
            or MarketIntelligenceSynthesisGuardrail()
        )

        self.article_search_agent = (
            article_search_agent
            or MarketArticleRelevanceAgent()
        )

    def research(
        self,
        ticker: str,
        rag_query: str | None = None,
        top_k: int = 5,
    ) -> MarketIntelligenceAnalysis | None:
        """
        Run the complete Market Intelligence workflow.
        """
        normalized_ticker = ticker.strip().upper()

        if not normalized_ticker:
            raise ValueError("ticker must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        profile = self.profile_resolver.resolve(
            normalized_ticker,
        )

        web_search_result = self.article_search_agent.search(
            ticker=normalized_ticker,
            company_name=profile.company_name,
        )

        if not web_search_result.articles:
            return None

        evidence = [
        GroundedMarketEvidence(
        ticker=normalized_ticker,
        title=article.title,
        source=article.source,
        url=article.url,
        published_at=article.published_at,
        summary=article.summary,
        reason=article.reason,
        entity_scope=article.entity_scope,
    )
        for article in web_search_result.articles
]

        query = rag_query or self._build_rag_query(
            profile.company_name,
        )

        rag_context = self.rag_retriever.search(
            query=query,
            ticker=normalized_ticker,
            top_k=top_k,
        )

        events = self.event_extractor.extract(
            ticker=normalized_ticker,
            evidence=evidence,
            rag_context=rag_context,
        )

        if not events:
            raise RuntimeError(
                f"No market events were extracted for "
                f"{normalized_ticker}."
            )

        analysis = self.synthesizer.synthesize(
            ticker=normalized_ticker,
            events=events,
            evidence=evidence,
            rag_context=rag_context,
        )

        return self.synthesis_guardrail.validate(
            ticker=normalized_ticker,
            analysis=analysis,
            events=events,
        )

    @staticmethod
    def _build_rag_query(company_name: str) -> str:
        return (
            f"{company_name} financial performance business outlook "
            "earnings growth profitability risks strategy "
            "major developments"
        )