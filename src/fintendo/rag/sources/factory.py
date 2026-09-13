from fintendo.data.company.models import CompanyProfile
from fintendo.rag.sources.web_discovery import (
    WebDocumentDiscoverySource,
)


def get_document_discovery_source(
    profile: CompanyProfile,
) -> WebDocumentDiscoverySource:
    return WebDocumentDiscoverySource()
