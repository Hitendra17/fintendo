from pprint import pprint

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
from fintendo.core.config import settings
from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.market_client import MarketDataClient
from fintendo.llm.gemini import GeminiClient
from fintendo.quant.fundamental_engine import FundamentalEngine
from fintendo.quant.technical_confidence import (
    TechnicalConfidenceCalculator,
)
from fintendo.quant.technical_engine import TechnicalEngine
from fintendo.quant.technical_evidence import TechnicalEvidenceBuilder
from fintendo.rag.in_memory import InMemoryRAGRetriever


def build_market_intelligence_service(
    gemini: GeminiClient,
) -> MarketIntelligenceService:
    """Build the real Market Intelligence pipeline."""

    market_data_client = MarketDataClient()

    profile_resolver = CompanyProfileResolver(
        market_data_client,
    )

    rag_retriever = InMemoryRAGRetriever()

    event_extractor = MarketEventExtractor(
        llm=gemini,
    )

    synthesizer = MarketIntelligenceSynthesizer(
        llm=gemini,
    )

    return MarketIntelligenceService(
        profile_resolver=profile_resolver,
        rag_retriever=rag_retriever,
        event_extractor=event_extractor,
        synthesizer=synthesizer,
    )


def build_committee_service() -> CommitteeResearchService:
    """Build the complete real research pipeline."""

    gemini = GeminiClient()
    market_data_client = MarketDataClient()

    # -------------------------
    # Fundamental
    # -------------------------

    fundamental_engine = FundamentalEngine()

    fundamental_agent = FundamentalAgent(
        llm=gemini,
    )

    fundamental_service = FundamentalResearchService(
        market_data_client=market_data_client,
        fundamental_engine=fundamental_engine,
        fundamental_agent=fundamental_agent,
    )

    # -------------------------
    # Technical
    # -------------------------

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

    # -------------------------
    # Market Intelligence
    # -------------------------

    market_intelligence_service = build_market_intelligence_service(
        gemini=gemini,
    )

    # -------------------------
    # Committee
    # -------------------------

    committee_agent = CommitteeAgent(
        llm=gemini,
    )

    return CommitteeResearchService(
        fundamental_service=fundamental_service,
        technical_service=technical_service,
        market_intelligence_service=market_intelligence_service,
        committee_agent=committee_agent,
    )


def main() -> None:
    ticker = "EMBASSY"

    print("=" * 80)
    print("FINTENDO RESEARCH")
    print("=" * 80)
    print(f"Environment : {settings.environment}")
    print(f"Model       : {settings.gemini_model}")
    print(f"Ticker      : {ticker}")
    print("=" * 80)

    # Resolve company metadata through Yahoo Finance.
    market_data_client = MarketDataClient()
    profile_resolver = CompanyProfileResolver(
        market_data_client,
    )

    print("\nResolving company profile...")

    profile = profile_resolver.resolve(ticker)

    print(f"Company     : {profile.company_name}")
    print(f"Ticker      : {profile.ticker}")
    print(f"Exchange    : {profile.exchange}")
    print(f"Website     : {profile.official_website}")

    # Build the complete research pipeline.
    service = build_committee_service()

    print("\nRunning complete research pipeline...")
    print()
    print("Fundamental → Technical → Market Intelligence → Committee")
    print()

    report = service.research_report(
        ticker=profile.ticker,
        company_name=profile.company_name,
        rag_query=(
            f"{profile.company_name} business fundamentals "
            f"financial performance competitive position"
        ),
        rag_top_k=5,
        technical_period="1y",
        technical_interval="1d",
    )

    print("\n" + "=" * 80)
    print("FUNDAMENTAL ANALYSIS")
    print("=" * 80)
    pprint(
        report.fundamental.model_dump(mode="json"),
        sort_dicts=False,
    )

    print("\n" + "=" * 80)
    print("TECHNICAL ANALYSIS")
    print("=" * 80)
    pprint(
        report.technical.model_dump(mode="json"),
        sort_dicts=False,
    )

    print("\n" + "=" * 80)
    print("MARKET INTELLIGENCE")
    print("=" * 80)

    if report.market_intelligence is None:
        print(
            "Market Intelligence unavailable: "
            "no current grounded market evidence was found."
        )
    else:
        pprint(
            report.market_intelligence.model_dump(mode="json"),
            sort_dicts=False,
        )

    print("\n" + "=" * 80)
    print("FINAL COMMITTEE DECISION")
    print("=" * 80)
    pprint(
        report.committee.model_dump(mode="json"),
        sort_dicts=False,
    )

    print("\n" + "=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()