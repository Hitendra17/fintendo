from functools import lru_cache

from fintendo.agents.research.committee.agent import CommitteeAgent
from fintendo.agents.research.committee.service import (
    CommitteeResearchService,
)
from fintendo.agents.research.fundamental.agent import FundamentalAgent
from fintendo.agents.research.fundamental.service import (
    FundamentalResearchService,
)
from fintendo.agents.research.market_intelligence.event_extractor import (
    MarketEventExtractor,
)
from fintendo.agents.research.market_intelligence.service import (
    MarketIntelligenceService,
)
from fintendo.agents.research.market_intelligence.synthesizer import (
    MarketIntelligenceSynthesizer,
)
from fintendo.agents.research.technical.agent import TechnicalAgent
from fintendo.agents.research.technical.service import (
    TechnicalResearchService,
)
from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.company.search import CompanySearchService
from fintendo.data.market_client import MarketDataClient
from fintendo.llm.gemini import GeminiClient
from fintendo.quant.fundamental_engine import FundamentalEngine
from fintendo.quant.technical_confidence import (
    TechnicalConfidenceCalculator,
)
from fintendo.quant.technical_engine import TechnicalEngine
from fintendo.quant.technical_evidence import TechnicalEvidenceBuilder
from fintendo.rag.in_memory import InMemoryRAGRetriever


@lru_cache(maxsize=1)
def get_gemini_client() -> GeminiClient:
    return GeminiClient()


@lru_cache(maxsize=1)
def get_market_data_client() -> MarketDataClient:
    return MarketDataClient()


@lru_cache(maxsize=1)
def get_profile_resolver() -> CompanyProfileResolver:
    return CompanyProfileResolver(
        get_market_data_client(),
    )


@lru_cache(maxsize=1)
def get_company_search_service() -> CompanySearchService:
    return CompanySearchService()


@lru_cache(maxsize=1)
def get_committee_research_service() -> CommitteeResearchService:
    gemini = get_gemini_client()
    market_data_client = get_market_data_client()

    # Fundamental
    fundamental_engine = FundamentalEngine()

    fundamental_agent = FundamentalAgent(
        llm=gemini,
    )

    fundamental_service = FundamentalResearchService(
        market_data_client=market_data_client,
        fundamental_engine=fundamental_engine,
        fundamental_agent=fundamental_agent,
    )

    # Technical
    technical_engine = TechnicalEngine()
    technical_evidence_builder = TechnicalEvidenceBuilder()
    technical_confidence_calculator = TechnicalConfidenceCalculator()

    technical_agent = TechnicalAgent(
        llm=gemini,
    )

    technical_service = TechnicalResearchService(
        market_data_client=market_data_client,
        technical_engine=technical_engine,
        evidence_builder=technical_evidence_builder,
        confidence_calculator=technical_confidence_calculator,
        technical_agent=technical_agent,
    )

    # Market Intelligence
    profile_resolver = get_profile_resolver()
    rag_retriever = InMemoryRAGRetriever()

    event_extractor = MarketEventExtractor(
        llm=gemini,
    )

    synthesizer = MarketIntelligenceSynthesizer(
        llm=gemini,
    )

    market_intelligence_service = MarketIntelligenceService(
        profile_resolver=profile_resolver,
        rag_retriever=rag_retriever,
        event_extractor=event_extractor,
        synthesizer=synthesizer,
    )

    # Committee
    committee_agent = CommitteeAgent(
        llm=gemini,
    )

    return CommitteeResearchService(
        fundamental_service=fundamental_service,
        technical_service=technical_service,
        market_intelligence_service=market_intelligence_service,
        committee_agent=committee_agent,
    )