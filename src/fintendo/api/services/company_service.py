from fintendo.api.dependencies import get_company_search_service
from fintendo.api.schemas.company import CompanySearchResult


class CompanyService:
    def __init__(self) -> None:
        self.company_search_service = get_company_search_service()

    def search(self, query: str) -> list[CompanySearchResult]:
        results = self.company_search_service.search(query)

        return [
            CompanySearchResult(
                ticker=result.ticker,
                company_name=result.company_name,
                exchange=result.exchange,
                sector=None,
            )
            for result in results
        ]