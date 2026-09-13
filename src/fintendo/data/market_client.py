from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

from fintendo.models.market import FinancialSnapshot


class MarketDataClient:
    def get_financial_snapshot(self, ticker: str) -> FinancialSnapshot:
        yahoo_ticker = yf.Ticker(f"{ticker}.NS")
        info = yahoo_ticker.info

        return FinancialSnapshot(
            ticker=ticker.upper(),
            company_name=info.get("longName", ticker.upper()),
            market_cap=info.get("marketCap"),
            revenue=info.get("totalRevenue"),
            net_income=info.get("netIncomeToCommon"),
            operating_cash_flow=info.get("operatingCashflow"),
            free_cash_flow=info.get("freeCashflow"),
            revenue_growth=info.get("revenueGrowth"),
            earnings_growth=info.get("earningsGrowth"),
            profit_margin=info.get("profitMargins"),
            operating_margin=info.get("operatingMargins"),
            return_on_equity=info.get("returnOnEquity"),
            return_on_assets=info.get("returnOnAssets"),
            debt_to_equity=info.get("debtToEquity"),
            current_ratio=info.get("currentRatio"),
            trailing_pe=info.get("trailingPE"),
            price_to_book=info.get("priceToBook"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            as_of=datetime.now(timezone.utc),
        )

    def get_company_metadata(self, ticker: str) -> dict:
        ticker = ticker.strip().upper()

        if not ticker:
            raise ValueError("Ticker must not be empty.")

        yahoo_ticker = yf.Ticker(f"{ticker}.NS")
        info = yahoo_ticker.info

        if not info:
            raise ValueError(f"No company metadata found for {ticker}.")

        return {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "exchange": info.get("exchange", ""),
            "official_website": info.get("website"),
            "investor_relations_url": info.get("irWebsite"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        }

    def get_price_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        yahoo_ticker = yf.Ticker(f"{ticker}.NS")

        data = yahoo_ticker.history(
            period=period,
            interval=interval,
            auto_adjust=True,
        )

        if data.empty:
            raise ValueError(f"No price history found for {ticker}.")

        required_columns = ["Open", "High", "Low", "Close", "Volume"]

        missing_columns = [
            column for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing price columns for {ticker}: {missing_columns}"
            )

        return data[required_columns].dropna()

    def get_financial_statements(self, ticker: str) -> dict[str, pd.DataFrame]:
        yahoo_ticker = yf.Ticker(f"{ticker}.NS")

        return {
            "income_statement": yahoo_ticker.income_stmt,
            "balance_sheet": yahoo_ticker.balance_sheet,
            "cash_flow": yahoo_ticker.cashflow,
        }