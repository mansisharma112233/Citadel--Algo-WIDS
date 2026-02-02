# Week 2 — Day 7 & 8: NoiseAgent and MomentumAgent

## Summary

### Brownian Fair Value (NoiseAgent)
NoiseAgent maintains an internal "fair value" estimate that evolves via Brownian motion:
```
fair_value += normal(0, volatility)
```
This creates a random walk that the agent uses to bias its limit order prices. The agent acts as a zero-intelligence liquidity consumer, placing mostly market orders (60%) with some aggressive limit orders near the touch (40%).

### Poisson-like Randomness
While not explicitly Poisson, the random arrival of NoiseAgent actions combined with random quantities (1–5) creates bursty, unpredictable order flow similar to Poisson processes observed in real markets. This helps stress-test the matching engine and generates realistic volume patterns.

### SMA Crossover Logic (MomentumAgent)
MomentumAgent implements a simple trend-following strategy:
1. Maintains a 50-period price history
2. Computes Simple Moving Average (SMA) of mid-prices
3. **BUY MARKET** when price > SMA (uptrend)
4. **SELL MARKET** when price < SMA (downtrend)
5. **NONE** when price == SMA or insufficient history

This is a classic momentum strategy that profits when trends persist.

### Why These Create Volume and Trends
- **NoiseAgent**: Generates continuous random order flow, providing baseline liquidity and volume. Its Brownian fair value can create micro-trends.
- **MomentumAgent**: Amplifies existing trends by buying into strength and selling into weakness. When multiple momentum agents act together, they can create positive feedback loops.

Together, these agents produce realistic market dynamics with volume, volatility, and occasional trending behavior.

### Files Created
- `noise_agent.py` — NoiseAgent with Brownian fair value
- `momentum_agent.py` — MomentumAgent with SMA crossover

---

This completes Week 2 Day 7 & Day 8.
