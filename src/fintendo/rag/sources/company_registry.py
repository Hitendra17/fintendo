from dataclasses import dataclass


@dataclass(frozen=True)
class CompanySourceConfig:
    ticker: str
    company_name: str
    investor_relations_url: str
    source_name: str


COMPANY_SOURCES: dict[str, CompanySourceConfig] = {
    "RELIANCE": CompanySourceConfig(
        ticker="RELIANCE",
        company_name="Reliance Industries Limited",
        investor_relations_url=(
            "https://www.ril.com/investors/investor-relations"
        ),
        source_name="Reliance Investor Relations",
    ),
}


def get_company_source(ticker: str) -> CompanySourceConfig:
    normalized_ticker = ticker.strip().upper()

    try:
        return COMPANY_SOURCES[normalized_ticker]
    except KeyError as exc:
        raise ValueError(
            f"No source configuration found for ticker "
            f"{normalized_ticker}."
        ) from exc