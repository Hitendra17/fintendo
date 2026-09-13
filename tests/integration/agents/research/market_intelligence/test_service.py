import pytest

from fintendo.agents.research.market_intelligence.event_extractor import (
    MarketEventExtractor,
)
from fintendo.agents.research.market_intelligence.service import (
    MarketIntelligenceService,
)
from fintendo.agents.research.market_intelligence.synthesis_guardrails import (
    MarketIntelligenceSynthesisGuardrail,
)
from fintendo.agents.research.market_intelligence.synthesizer import (
    MarketIntelligenceSynthesizer,
)
from fintendo.data.article_deduplicator import ArticleDeduplicator
from fintendo.data.article_metadata import ArticleMetadataExtractor
from fintendo.data.article_normalizer import ArticleNormalizer
from fintendo.data.html_parser import HTMLParser
from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
    MarketSourceType,
)
from fintendo.data.market_sources.orchestration import (
    MarketSourceOrchestrator,
)
from fintendo.data.news_ingestion import NewsIngestionService
from fintendo.data.url_normalizer import URLNormalizer
from fintendo.data.web_fetcher import WebFetcher
from fintendo.llm.gemini import GeminiClient
from fintendo.models.market_intelligence import MarketIntelligenceAnalysis
from fintendo.rag.models import RAGSearchResult
from fintendo.rag.retriever import RAGRetriever


class EmptyRAGRetriever(RAGRetriever):
    """
    Test retriever that deliberately returns no historical context.

    This integration test is focused on validating the current-market
    information pipeline, event extraction, synthesis, and final
    synthesis guardrails.
    """

    def add_documents(self, chunks) -> None:
        pass

    def search(
        self,
        query: str,
        ticker: str,
        top_k: int = 5,
    ) -> list[RAGSearchResult]:
        return []


def build_news_ingestion_service() -> NewsIngestionService:
    return NewsIngestionService(
        web_fetcher=WebFetcher(),
        html_parser=HTMLParser(),
        article_normalizer=ArticleNormalizer(),
        url_normalizer=URLNormalizer(),
        article_deduplicator=ArticleDeduplicator(),
        metadata_extractor=ArticleMetadataExtractor(),
    )


@pytest.mark.integration
def test_market_intelligence_service_with_real_news() -> None:
    ticker = "HDFCBANK"

    source = MarketSource(
        name="HDFC Bank Official Website",
        source_type=MarketSourceType.COMPANY,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://www.hdfc.bank.in/",
        description="HDFC Bank official website.",
    )

    service = MarketIntelligenceService(
        source_orchestrator=MarketSourceOrchestrator(),
        news_ingestion=build_news_ingestion_service(),
        rag_retriever=EmptyRAGRetriever(),
        event_extractor=MarketEventExtractor(
            llm=GeminiClient(),
        ),
        synthesizer=MarketIntelligenceSynthesizer(
            llm=GeminiClient(),
        ),
        synthesis_guardrail=MarketIntelligenceSynthesisGuardrail(),
    )

    analysis = service.research(
        ticker=ticker,
        sources=[source],
        top_k=5,
    )

    if analysis is None:
        pytest.skip(
            "Market Intelligence could not ingest current HDFC Bank "
            "articles from the configured external source."
        )

    assert isinstance(analysis, MarketIntelligenceAnalysis)
    assert analysis.ticker == ticker
    assert 0 <= analysis.score <= 100
    assert analysis.summary
    assert analysis.key_events

    assert analysis.positive_factors is not None
    assert analysis.negative_factors is not None
    assert analysis.catalysts is not None
    assert analysis.risks is not None

    assert analysis.short_term_outlook is not None
    assert analysis.medium_term_outlook is not None
    assert analysis.long_term_outlook is not None

    for event in analysis.key_events:
        assert event.ticker == ticker
        assert event.title
        assert event.summary
        assert event.source
        assert event.source_url