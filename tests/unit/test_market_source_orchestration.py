from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.models import (
    MarketDiscoveryMethod,
    MarketSource,
    MarketSourceType,
)
from fintendo.data.market_sources.orchestration import (
    MarketSourceOrchestrator,
    SourceDiscoveryResult,
)


class FakeProfileResolver:
    def resolve(self, ticker: str) -> CompanyProfile:
        return CompanyProfile(
            ticker=ticker.upper(),
            company_name="Test Company",
            exchange="NSI",
            official_website="https://example.com",
        )


class SuccessfulDiscovery:
    def discover(
        self,
        profile: CompanyProfile,
        source: MarketSource,
    ) -> list[str]:
        return ["https://example.com/article-1"]


class FailingDiscovery:
    def discover(
        self,
        profile: CompanyProfile,
        source: MarketSource,
    ) -> list[str]:
        raise TimeoutError("source timed out")


def make_source(name: str) -> MarketSource:
    return MarketSource(
        name=name,
        source_type=MarketSourceType.NEWS,
        discovery_method=MarketDiscoveryMethod.WEB_PAGE,
        url="https://example.com",
        description="Test source.",
    )


def test_orchestrator_continues_when_one_source_fails() -> None:
    orchestrator = MarketSourceOrchestrator(
        profile_resolver=FakeProfileResolver(),
        discoveries={
            "web_page": SuccessfulDiscovery(),
        },
    )

    profile, results = orchestrator.discover(
        ticker="TEST",
        sources=[make_source("Working Source")],
    )

    assert profile.ticker == "TEST"
    assert len(results) == 1
    assert results[0].succeeded is True
    assert results[0].urls == ["https://example.com/article-1"]


def test_orchestrator_records_source_failure() -> None:
    orchestrator = MarketSourceOrchestrator(
        profile_resolver=FakeProfileResolver(),
        discoveries={
            "web_page": FailingDiscovery(),
        },
    )

    profile, results = orchestrator.discover(
        ticker="TEST",
        sources=[make_source("Failing Source")],
    )

    assert profile.ticker == "TEST"
    assert len(results) == 1
    assert results[0].succeeded is False
    assert results[0].urls == []
    assert results[0].error == "source timed out"


def test_source_discovery_result_success_property() -> None:
    success = SourceDiscoveryResult(
        source_name="Working Source",
        urls=["https://example.com"],
    )

    failure = SourceDiscoveryResult(
        source_name="Failing Source",
        error="timeout",
    )

    assert success.succeeded is True
    assert failure.succeeded is False