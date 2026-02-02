# Week 2 — Day 2: Price-Time Priority Matching Engine

## Summary

### Price-Time Priority
Orders are matched first by price (best price first), then by time (earliest order at that price level first). BUY orders match against the lowest ASK prices; SELL orders match against the highest BID prices.

### FIFO at Price Level
At each price level, orders are stored in a deque (double-ended queue). The oldest order (front of the deque) is always matched first, ensuring fair execution order.

### Book Walking
The matching engine "walks" through the order book price level by price level. For a BUY order, it starts at the best (lowest) ask and moves up; for a SELL order, it starts at the best (highest) bid and moves down.

### Partial Fills
If the incoming order quantity exceeds the resting order quantity, the resting order is fully filled and removed. The incoming order continues matching with the next resting order until fully filled or no more matches exist.

### Market Order Behavior
Market orders (price=None) match immediately against available liquidity at any price. If the book is exhausted before the market order is filled, the remaining quantity is discarded (no resting).

## Validation Test
A test function `test_market_buy_clears_asks()` is included in `matching_engine.py`. It verifies that a market BUY order correctly sweeps through multiple ASK price levels in order.

Run via:
```
python -c "from week2.orderbook.matching_engine import test_market_buy_clears_asks; test_market_buy_clears_asks()"
```

This completes Week 2 Day 2.
