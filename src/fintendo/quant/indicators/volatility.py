import pandas as pd


def historical_volatility(
    prices: pd.Series,
    annualization_factor: int = 252,
) -> pd.Series:
    if annualization_factor <= 0:
        raise ValueError("Annualization factor must be greater than zero.")

    returns = prices.pct_change()

    return returns.rolling(window=20).std() * (annualization_factor**0.5)