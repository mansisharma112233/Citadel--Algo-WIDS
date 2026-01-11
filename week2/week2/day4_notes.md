Day 4 implements the analytics pipeline.
Trades are recorded in an append-only tape.
L1 snapshots record best bid, best ask, spread and mid-price.
VWAP is computed from the tape only.
Mid-price volatility is computed from resampled mid-prices.
