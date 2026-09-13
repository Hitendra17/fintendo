import pandas as pd


class FinancialStatementExtractor:
    def extract(self, statements: dict[str, pd.DataFrame]) -> dict:
        income_statement = statements["income_statement"]
        balance_sheet = statements["balance_sheet"]
        cash_flow = statements["cash_flow"]

        return {
            "income_statement": {
                "revenue": income_statement.loc["Total Revenue"].dropna().to_dict(),
                "operating_income": income_statement.loc["Operating Income"].dropna().to_dict(),
                "net_income": income_statement.loc["Net Income"].dropna().to_dict(),
            },
            "balance_sheet": {
                "total_assets": balance_sheet.loc["Total Assets"].dropna().to_dict(),
                "stockholders_equity": balance_sheet.loc["Stockholders Equity"].dropna().to_dict(),
                "total_debt": balance_sheet.loc["Total Debt"].dropna().to_dict(),
                "current_assets": balance_sheet.loc["Current Assets"].dropna().to_dict(),
                "current_liabilities": balance_sheet.loc["Current Liabilities"].dropna().to_dict(),
            },
            "cash_flow": {
                "operating_cash_flow": cash_flow.loc["Operating Cash Flow"].dropna().to_dict(),
                "capital_expenditure": cash_flow.loc["Capital Expenditure"].dropna().to_dict(),
                "free_cash_flow": cash_flow.loc["Free Cash Flow"].dropna().to_dict(),
            },
        } 