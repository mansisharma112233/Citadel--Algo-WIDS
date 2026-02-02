# Integration: called after simulation to compute summary statistics from tape and snapshots.

import pandas as pd
import numpy as np


def compute_vwap(tape_df: pd.DataFrame) -> float:
    """Volume-weighted average price from trade tape.

    VWAP = sum(price * quantity) / sum(quantity)
    """
    return (tape_df["price"] * tape_df["quantity"]).sum() / tape_df["quantity"].sum()


def compute_midprice_volatility(snapshot_df: pd.DataFrame) -> float:
    """Volatility of mid-price as std of log returns.

    Computes log returns of mid_price series and returns standard deviation.
    """
    mid = snapshot_df["mid_price"].dropna()
    log_returns = np.log(mid / mid.shift(1)).dropna()
    return log_returns.std()


# Backward compatibility alias
mid_price_volatility = compute_midprice_volatility


def average_spread(snapshot_df: pd.DataFrame) -> float:
    """Mean of spread column."""
    return snapshot_df["spread"].mean()
