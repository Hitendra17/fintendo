import pandas as pd


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    if period <= 0:
        raise ValueError("Period must be greater than zero.")

    delta = prices.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    average_gain = gains.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = losses.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    relative_strength = average_gain / average_loss

    return 100 - (100 / (1 + relative_strength))



def macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    if not (0 < fast_period < slow_period):
        raise ValueError("Fast period must be positive and less than slow period.")

    if signal_period <= 0:
        raise ValueError("Signal period must be greater than zero.")

    fast_ema = prices.ewm(
        span=fast_period,
        adjust=False,
    ).mean()

    slow_ema = prices.ewm(
        span=slow_period,
        adjust=False,
    ).mean()

    macd_line = fast_ema - slow_ema

    signal_line = macd_line.ewm(
        span=signal_period,
        adjust=False,
    ).mean()

    histogram = macd_line - signal_line

    return pd.DataFrame(
        {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }
    )