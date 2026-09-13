from unittest.mock import Mock, patch
import pytest

from fintendo.data.company.search import (
    CompanySearchResult,
    CompanySearchService,
)


def test_search_returns_only_nse_equities() -> None:
    yahoo_search = Mock()
    yahoo_search.quotes = [
        {
            "symbol": "INFY",
            "longname": "Infosys Limited",
            "shortname": "Infosys Limited",
            "exchDisp": "NYSE",
            "quoteType": "EQUITY",
            "score": 22572.0,
        },
        {
            "symbol": "INFY.NS",
            "longname": "Infosys Limited",
            "shortname": "INFOSYS LIMITED",
            "exchDisp": "NSE",
            "quoteType": "EQUITY",
            "score": 20586.0,
        },
        {
            "symbol": "INFY.BO",
            "longname": "Infosys Limited",
            "shortname": "INFOSYS LTD.",
            "exchDisp": "Bombay",
            "quoteType": "EQUITY",
            "score": 20040.0,
        },
        {
            "symbol": "0P00012KBN.BO",
            "longname": "HDFC Banking & PSU Debt",
            "shortname": "HDFC Banking",
            "exchDisp": "Bombay",
            "quoteType": "MUTUALFUND",
            "score": 19000.0,
        },
    ]

    with patch(
        "fintendo.data.company.search.yf.Search",
        return_value=yahoo_search,
    ):
        service = CompanySearchService()
        results = service.search("Infosys")

    assert results == [
        CompanySearchResult(
            ticker="INFY",
            company_name="Infosys Limited",
            exchange="NSE",
            quote_type="EQUITY",
            score=20586.0,
        )
    ]


def test_search_respects_limit() -> None:
    yahoo_search = Mock()
    yahoo_search.quotes = [
        {
            "symbol": "ABC.NS",
            "longname": "ABC Limited",
            "shortname": "ABC",
            "exchDisp": "NSE",
            "quoteType": "EQUITY",
            "score": 100.0,
        },
        {
            "symbol": "XYZ.NS",
            "longname": "XYZ Limited",
            "shortname": "XYZ",
            "exchDisp": "NSE",
            "quoteType": "EQUITY",
            "score": 90.0,
        },
        {
            "symbol": "DEF.NS",
            "longname": "DEF Limited",
            "shortname": "DEF",
            "exchDisp": "NSE",
            "quoteType": "EQUITY",
            "score": 80.0,
        },
    ]

    with patch(
        "fintendo.data.company.search.yf.Search",
        return_value=yahoo_search,
    ):
        service = CompanySearchService()
        results = service.search("company", limit=2)

    assert len(results) == 2
    assert [result.ticker for result in results] == ["ABC", "XYZ"]


@pytest.mark.parametrize(
    ("query", "limit", "error"),
    [
        ("   ", 5, "query must not be empty"),
        ("Infosys", 0, "limit must be positive"),
        ("Infosys", -1, "limit must be positive"),
    ],
)
def test_search_validates_input(
    query: str,
    limit: int,
    error: str,
) -> None:
    service = CompanySearchService()

    with pytest.raises(ValueError, match=error):
        service.search(query, limit=limit)


def test_search_uses_normalized_query() -> None:
    yahoo_search = Mock()
    yahoo_search.quotes = []

    with patch(
        "fintendo.data.company.search.yf.Search",
        return_value=yahoo_search,
    ) as search_mock:
        service = CompanySearchService()
        service.search("  Infosys  ")

    search_mock.assert_called_once_with("Infosys")