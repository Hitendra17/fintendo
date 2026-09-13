import pandas as pd


def support_levels(
    lows: pd.Series,
    current_price: float,
    window: int = 20,
    num_levels: int = 3,
) -> list[float]:
    if window <= 0:
        raise ValueError("Window must be greater than zero.")

    if num_levels <= 0:
        raise ValueError("Number of levels must be greater than zero.")

    rolling_low = lows.rolling(
        window=window,
        center=True,
    ).min()

    local_lows = lows[
        lows.eq(rolling_low)
    ].dropna()

    valid_levels = local_lows[
        local_lows < current_price
    ]

    if valid_levels.empty:
        return []

    return sorted(
        valid_levels.unique(),
        reverse=True,
    )[:num_levels]


def resistance_levels(
    highs: pd.Series,
    current_price: float,
    window: int = 20,
    num_levels: int = 3,
) -> list[float]:
    if window <= 0:
        raise ValueError("Window must be greater than zero.")

    if num_levels <= 0:
        raise ValueError("Number of levels must be greater than zero.")

    rolling_high = highs.rolling(
        window=window,
        center=True,
    ).max()

    local_highs = highs[
        highs.eq(rolling_high)
    ].dropna()

    valid_levels = local_highs[
        local_highs > current_price
    ]

    if valid_levels.empty:
        return []

    return sorted(
        valid_levels.unique()
    )[:num_levels]