# Week 2 — Day 5: Full Simulation, Validation, and PDF Report

## Summary

### What run_simulation.py Does
1. Seeds random number generator (seed=42) for deterministic output
2. Initializes all components: OrderBookHeap, MatchingEngine, EventLoop, TradeTape, SnapshotRecorder
3. Generates 1000 random LIMIT and MARKET orders with arrival times between 0–300 seconds
4. Schedules order arrival events and snapshot events (every 1 second) in the EventLoop
5. Runs the discrete-event simulation, processing orders and recording trades/snapshots
6. Computes summary metrics: VWAP, average spread, mid-price volatility
7. Generates 4 plots and exports them to `simulation_report.pdf`

### Validation Checks
- Price >= 0 for all orders
- Quantity >= 0 for all orders
- Trade price >= 0 for all executed trades
- Trade quantity >= 0 for all executed trades
- Best bid >= 0 when present
- Best ask >= 0 when present

If any assertion fails, the simulation crashes immediately.

### PDF Contents
The generated `simulation_report.pdf` contains 4 pages:
1. **Candlestick Chart**: 1-minute OHLC price bars from the trade tape
2. **Volume Bars**: Total volume traded per minute
3. **Spread Over Time**: Bid-ask spread recorded at each snapshot
4. **Rolling Volatility**: 10-period rolling standard deviation of mid-price log returns

### Running the Simulation
```bash
python week2/run_simulation.py
```

This produces `week2/simulation_report.pdf`.

---

This completes Week 2 Day 5.
