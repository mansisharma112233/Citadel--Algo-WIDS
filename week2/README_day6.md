# Week 2 — Day 6: Agent Architecture and RandomAgent

## Summary

### Why Polymorphism is Required
Using an abstract base class (`Agent`) with an abstract `get_action()` method ensures all agent implementations share a common interface. This allows the simulation engine to treat all agents uniformly—whether RandomAgent, MomentumAgent, or any future strategy—without knowing their internal logic. New strategies can be added by simply inheriting from `Agent`.

### Why Agents Must Not Touch the Orderbook
Agents receive only a read-only snapshot of market data (best bid, best ask, mid-price, spread). This enforces a clean separation:
- **Agents** decide *what* to do based on observable market state
- **MatchingEngine** executes orders and updates the book

This prevents agents from cheating (e.g., peeking at hidden orders) and mirrors real exchange APIs where traders only see public market data.

### Role of RandomAgent for Stress Testing
RandomAgent generates unpredictable order flow with random sides, quantities, and prices. This is useful for:
- Stress testing the matching engine under chaotic conditions
- Providing baseline liquidity in simulations
- Verifying system robustness against pathological inputs

### Files Created
- `base_agent.py` — Abstract `Agent` base class
- `random_agent.py` — `RandomAgent` implementation

---

This completes Week 2 Day 6.
