from abc import ABC, abstractmethod

from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_sources.models import MarketSource


class MarketSourceDiscovery(ABC):
    """
    Abstract interface for discovering current market-information URLs.

    Implementations are responsible only for discovery.
    They do not fetch, parse, normalize, or reason about articles.
    """

    @abstractmethod
    def discover(
        self,
        profile: CompanyProfile,
        source: MarketSource,
    ) -> list[str]:
        """Discover article or announcement URLs relevant to a company."""
        raise NotImplementedError