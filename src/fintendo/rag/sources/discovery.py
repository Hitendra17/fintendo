from abc import ABC, abstractmethod

from fintendo.data.company.models import CompanyProfile
from fintendo.rag.sources.models import DiscoveredDocument


class DocumentDiscoverySource(ABC):
    @abstractmethod
    def discover(
        self,
        profile: CompanyProfile,
    ) -> list[DiscoveredDocument]:
        """Discover real documents for a company."""
        raise NotImplementedError
