from fintendo.data.company.models import CompanyProfile
from fintendo.data.market_client import MarketDataClient


class CompanyProfileResolver:
    def __init__(
        self,
        market_data: MarketDataClient | None = None,
    ) -> None:
        self.market_data = market_data or MarketDataClient()

    def resolve(self, ticker: str) -> CompanyProfile:
        ticker = ticker.strip().upper()

        if not ticker:
            raise ValueError("Ticker must not be empty.")

        metadata = self.market_data.get_company_metadata(ticker)

        official_website = metadata.get("official_website")

        sectors = []

        if metadata.get("sector"):
            sectors.append(metadata["sector"])

        if metadata.get("industry"):
            sectors.append(metadata["industry"])

        return CompanyProfile(
            ticker=metadata["ticker"],
            company_name=metadata["company_name"],
            exchange=metadata["exchange"],
            official_website=official_website,
            investor_relations_url=metadata.get("investor_relations_url"),
            sectors=sectors,
            aliases=[],
        )