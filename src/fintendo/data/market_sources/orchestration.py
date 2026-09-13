from pydantic import BaseModel, Field

from fintendo.data.company.models import CompanyProfile
from fintendo.data.company.resolver import CompanyProfileResolver
from fintendo.data.market_client import MarketDataClient
from fintendo.data.market_sources.discovery import MarketSourceDiscovery
from fintendo.data.market_sources.models import MarketSource
from fintendo.data.market_sources.rss_discovery import (
    RSSMarketSourceDiscovery,
)
from fintendo.data.market_sources.web_discovery import (
    WebPageMarketSourceDiscovery,
)


class SourceDiscoveryResult(BaseModel):
    source_name: str = Field(min_length=1)
    urls: list[str] = Field(default_factory=list)
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None


class MarketSourceOrchestrator:
    def __init__(
        self,
        profile_resolver: CompanyProfileResolver | None = None,
        discoveries: dict[str, MarketSourceDiscovery] | None = None,
    ) -> None:
        self.profile_resolver = (
            profile_resolver
            or CompanyProfileResolver(MarketDataClient())
        )

        self.discoveries = discoveries or {
            "web_page": WebPageMarketSourceDiscovery(),
            "rss": RSSMarketSourceDiscovery(),
        }

    def discover(
        self,
        ticker: str,
        sources: list[MarketSource],
    ) -> tuple[CompanyProfile, list[SourceDiscoveryResult]]:
        profile = self.profile_resolver.resolve(ticker)

        results: list[SourceDiscoveryResult] = []

        for source in sources:
            if not source.enabled:
                continue

            discovery = self.discoveries.get(
                source.discovery_method.value
            )

            if discovery is None:
                results.append(
                    SourceDiscoveryResult(
                        source_name=source.name,
                        error=(
                            "No discovery implementation found for "
                            f"method '{source.discovery_method.value}'."
                        ),
                    )
                )
                continue

            try:
                urls = discovery.discover(
                    profile=profile,
                    source=source,
                )

                results.append(
                    SourceDiscoveryResult(
                        source_name=source.name,
                        urls=urls,
                    )
                )

            except (ValueError, RuntimeError, TimeoutError) as exc:
                results.append(
                    SourceDiscoveryResult(
                        source_name=source.name,
                        error=str(exc),
                    )
                )

        return profile, results