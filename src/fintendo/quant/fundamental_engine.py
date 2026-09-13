import pandas as pd

from fintendo.models.fundamental import FundamentalSnapshot


def _get_series(
    statement: pd.DataFrame,
    field: str,
) -> pd.Series:
    if field not in statement.index:
        return pd.Series(dtype="float64")

    return statement.loc[field].dropna()


class FundamentalEngine:
    def calculate(
        self,
        ticker: str,
        company_name: str,
        statements: dict[str, pd.DataFrame],
    ) -> FundamentalSnapshot:

        income = statements["income_statement"]
        balance = statements["balance_sheet"]
        cash_flow = statements["cash_flow"]

        # Extract financial statement rows safely.
        revenue = _get_series(income, "Total Revenue")
        operating_income = _get_series(income, "Operating Income")
        net_income = _get_series(income, "Net Income")

        total_assets = _get_series(balance, "Total Assets")
        equity = _get_series(balance, "Stockholders Equity")
        total_debt = _get_series(balance, "Total Debt")
        current_assets = _get_series(balance, "Current Assets")
        current_liabilities = _get_series(
            balance,
            "Current Liabilities",
        )

        operating_cash_flow = _get_series(
            cash_flow,
            "Operating Cash Flow",
        )
        capital_expenditure = _get_series(
            cash_flow,
            "Capital Expenditure",
        )
        free_cash_flow = _get_series(
            cash_flow,
            "Free Cash Flow",
        )

        # Revenue is required because it determines
        # the latest reporting period used by the engine.
        if revenue.empty:
            raise ValueError(
                f"Revenue data is unavailable for {ticker}."
            )

        # Latest available period.
        latest_period = revenue.index[0]

        latest_revenue = float(revenue.loc[latest_period])

        latest_operating_income = (
            float(operating_income.loc[latest_period])
            if latest_period in operating_income.index
            else None
        )

        latest_net_income = (
            float(net_income.loc[latest_period])
            if latest_period in net_income.index
            else None
        )

        latest_assets = (
            float(total_assets.loc[latest_period])
            if latest_period in total_assets.index
            else None
        )

        latest_equity = (
            float(equity.loc[latest_period])
            if latest_period in equity.index
            else None
        )

        latest_debt = (
            float(total_debt.loc[latest_period])
            if latest_period in total_debt.index
            else None
        )

        latest_current_assets = (
            float(current_assets.loc[latest_period])
            if latest_period in current_assets.index
            else None
        )

        latest_current_liabilities = (
            float(current_liabilities.loc[latest_period])
            if latest_period in current_liabilities.index
            else None
        )

        latest_ocf = (
            float(operating_cash_flow.loc[latest_period])
            if latest_period in operating_cash_flow.index
            else None
        )

        latest_capex = (
            float(capital_expenditure.loc[latest_period])
            if latest_period in capital_expenditure.index
            else None
        )

        latest_fcf = (
            float(free_cash_flow.loc[latest_period])
            if latest_period in free_cash_flow.index
            else None
        )

        # -------------------------
        # Growth
        # -------------------------

        revenue_yoy_growth = None

        if len(revenue) >= 2:
            previous_revenue = float(revenue.iloc[1])

            if previous_revenue != 0:
                revenue_yoy_growth = (
                    latest_revenue - previous_revenue
                ) / previous_revenue

        net_income_yoy_growth = None

        if len(net_income) >= 2 and latest_net_income is not None:
            previous_net_income = float(net_income.iloc[1])

            if previous_net_income != 0:
                net_income_yoy_growth = (
                    latest_net_income - previous_net_income
                ) / previous_net_income

        revenue_cagr = None

        if len(revenue) >= 2:
            oldest_revenue = float(revenue.iloc[-1])
            periods = len(revenue) - 1

            if oldest_revenue > 0:
                revenue_cagr = (
                    latest_revenue / oldest_revenue
                ) ** (1 / periods) - 1

        net_income_cagr = None

        if (
            len(net_income) >= 2
            and latest_net_income is not None
        ):
            oldest_net_income = float(net_income.iloc[-1])
            periods = len(net_income) - 1

            if oldest_net_income > 0 and latest_net_income > 0:
                net_income_cagr = (
                    latest_net_income / oldest_net_income
                ) ** (1 / periods) - 1

        # -------------------------
        # Profitability
        # -------------------------

        operating_margin = None

        if (
            latest_revenue != 0
            and latest_operating_income is not None
        ):
            operating_margin = (
                latest_operating_income / latest_revenue
            )

        net_income_margin = None

        if (
            latest_revenue != 0
            and latest_net_income is not None
        ):
            net_income_margin = (
                latest_net_income / latest_revenue
            )

        return_on_equity = None

        if (
            latest_equity is not None
            and latest_equity != 0
            and latest_net_income is not None
        ):
            return_on_equity = (
                latest_net_income / latest_equity
            )

        return_on_assets = None

        if (
            latest_assets is not None
            and latest_assets != 0
            and latest_net_income is not None
        ):
            return_on_assets = (
                latest_net_income / latest_assets
            )

        # -------------------------
        # Cash flow quality
        # -------------------------

        operating_cash_flow_margin = None

        if (
            latest_revenue != 0
            and latest_ocf is not None
        ):
            operating_cash_flow_margin = (
                latest_ocf / latest_revenue
            )

        free_cash_flow_margin = None

        if (
            latest_revenue != 0
            and latest_fcf is not None
        ):
            free_cash_flow_margin = (
                latest_fcf / latest_revenue
            )

        free_cash_flow_growth = None

        if len(free_cash_flow) >= 2 and latest_fcf is not None:
            previous_fcf = float(free_cash_flow.iloc[1])

            if previous_fcf != 0:
                free_cash_flow_growth = (
                    latest_fcf - previous_fcf
                ) / abs(previous_fcf)

        free_cash_flow_conversion = None

        if (
            latest_net_income is not None
            and latest_net_income != 0
            and latest_fcf is not None
        ):
            free_cash_flow_conversion = (
                latest_fcf / latest_net_income
            )

        # -------------------------
        # Balance sheet
        # -------------------------

        debt_to_equity = None

        if (
            latest_equity is not None
            and latest_equity != 0
            and latest_debt is not None
        ):
            debt_to_equity = latest_debt / latest_equity

        current_ratio = None

        if (
            latest_current_liabilities is not None
            and latest_current_liabilities != 0
            and latest_current_assets is not None
        ):
            current_ratio = (
                latest_current_assets
                / latest_current_liabilities
            )

        net_debt_to_operating_income = None

        if (
            latest_debt is not None
            and latest_operating_income is not None
            and latest_operating_income != 0
            and "Cash And Cash Equivalents" in balance.index
        ):
            cash = _get_series(
                balance,
                "Cash And Cash Equivalents",
            )

            if latest_period in cash.index:
                latest_cash = float(cash.loc[latest_period])
                latest_net_debt = latest_debt - latest_cash

                net_debt_to_operating_income = (
                    latest_net_debt
                    / latest_operating_income
                )

        return FundamentalSnapshot(
            ticker=ticker.upper(),
            company_name=company_name,
            as_of=latest_period.to_pydatetime(),

            revenue=latest_revenue,
            operating_income=latest_operating_income,
            net_income=latest_net_income,

            total_assets=latest_assets,
            stockholders_equity=latest_equity,
            total_debt=latest_debt,
            current_assets=latest_current_assets,
            current_liabilities=latest_current_liabilities,

            operating_cash_flow=latest_ocf,
            capital_expenditure=latest_capex,
            free_cash_flow=latest_fcf,

            revenue_yoy_growth=revenue_yoy_growth,
            net_income_yoy_growth=net_income_yoy_growth,

            revenue_cagr=revenue_cagr,
            net_income_cagr=net_income_cagr,

            operating_margin=operating_margin,
            net_income_margin=net_income_margin,
            return_on_equity=return_on_equity,
            return_on_assets=return_on_assets,

            operating_cash_flow_margin=operating_cash_flow_margin,
            free_cash_flow_margin=free_cash_flow_margin,
            free_cash_flow_growth=free_cash_flow_growth,
            free_cash_flow_conversion=free_cash_flow_conversion,

            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
            net_debt_to_operating_income=net_debt_to_operating_income,
        )