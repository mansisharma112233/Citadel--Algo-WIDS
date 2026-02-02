# Week 2 — Day 4: Tape, Snapshots, and Metrics

## Summary

### What is a Tape?
A trade tape is an append-only log of executed trades. Each entry records the timestamp, price, and quantity of a trade. It provides a complete history of market activity for post-simulation analysis.

### What is an L1 Snapshot?
An L1 (Level 1) snapshot captures the top-of-book market state at a point in time: best bid, best ask, spread, and mid-price. Recording snapshots at regular intervals (e.g., every second) creates a time series of market conditions.

### Why VWAP Uses Tape Only
Volume-Weighted Average Price (VWAP) measures the average price paid across all trades, weighted by volume. It requires actual executed trades, not quotes, so it's computed from the tape rather than snapshots.

### Why Volatility Uses Mid-Price
Mid-price (average of best bid and ask) represents the "fair value" between buyers and sellers. Using mid-price for volatility avoids noise from bid-ask bounce and provides a cleaner measure of true price movement.

## Files Created
- `tape.py` — TradeTape class for recording trades
- `snapshots.py` — SnapshotRecorder class for L1 market state
- `metrics.py` — VWAP, average spread, and volatility functions

This completes Week 2 Day 4.
