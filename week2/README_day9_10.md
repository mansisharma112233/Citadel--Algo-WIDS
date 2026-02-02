# Week 2 — Day 9 & 10: Multi-Agent Integration and Final Report

## Summary

### Market Making Logic (MarketMakerAgent)
Market makers provide liquidity by continuously quoting both sides of the book:
- **Bid price** = mid_price - half_spread
- **Ask price** = mid_price + half_spread

**Inventory Skew**: When the market maker accumulates inventory, it adjusts quotes to reduce risk:
- If **long** (positive inventory): Lower both bid and ask to encourage selling
- If **short** (negative inventory): Raise both bid and ask to encourage buying

This creates mean-reversion in inventory while still providing liquidity.

### Scenario Differences

| Scenario | Composition | Expected Behavior |
|----------|-------------|-------------------|
| A | 100 NoiseAgents | Baseline random dynamics, wide spreads |
| B | 80 Noise + 20 MarketMaker | Tighter spreads, more stable prices |
| C | 80 Noise + 20 Momentum | Higher volatility, trending behavior |

### Emergent Behavior

**Scenario A (Pure Noise):**
- Random walk price dynamics from Brownian fair values
- Spreads fluctuate without systematic tightening
- Volume depends on random order flow

**Scenario B (With Market Makers):**
- Market makers absorb one-sided flow
- Spreads tighten as MMs quote competitively
- Prices stabilize around fair value
- Inventory limits create natural mean-reversion

**Scenario C (With Momentum Traders):**
- Trend-following amplifies price movements
- Positive feedback creates larger swings
- Higher volatility compared to pure noise
- Momentum traders profit from persistent trends, lose during reversals

### Validation Assertions
The simulation includes runtime checks:
- `price >= 0` for all orders and trades
- `quantity >= 0` for all orders and trades
- `spread >= 0` at snapshot times
- Determinism: same seed produces identical results

### PDF Report Contents
1. **Page 1**: Setup and configuration
2. **Page 2**: Scenario A plots (mid-price, spread, candlestick)
3. **Page 3**: Scenario B plots
4. **Page 4**: Scenario C plots
5. **Page 5**: Comparison table (trades, volume, VWAP, spread, volatility)
6. **Page 6**: Interpretation and conclusions

### Running the Simulation
```bash
python week2/run_simulation.py
```

This produces `week2/simulation_report.pdf`.

---

This completes Week 2: Limit Order Book Simulator with Multi-Agent System.
