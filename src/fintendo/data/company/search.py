from dataclasses import dataclass

import yfinance as yf


@dataclass(frozen=True)
class CompanySearchResult:
    ticker: str
    company_name: str
    exchange: str
    quote_type: str
    score: float | None = None


class CompanySearchService:
    """
    Searches Yahoo Finance for companies and returns Indian NSE equity
    candidates.

    This component performs discovery only. It does not hydrate the
    complete CompanyProfile.
    """

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[CompanySearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query must not be empty.")

        if limit <= 0:
            raise ValueError("limit must be positive.")

        search = yf.Search(normalized_query)

        results: list[CompanySearchResult] = []

        for quote in search.quotes:
            symbol = quote.get("symbol", "")
            exchange = quote.get("exchDisp", "")
            quote_type = quote.get("quoteType", "")

            if exchange != "NSE":
                continue

            if quote_type != "EQUITY":
                continue

            if not symbol.endswith(".NS"):
                continue

            ticker = symbol.removesuffix(".NS").strip().upper()

            if not ticker:
                continue

            company_name = (
                quote.get("longname")
                or quote.get("shortname")
                or ticker
            )

            results.append(
                CompanySearchResult(
                    ticker=ticker,
                    company_name=company_name,
                    exchange=exchange,
                    quote_type=quote_type,
                    score=quote.get("score"),
                )
            )

            if len(results) >= limit:
                break

        return results