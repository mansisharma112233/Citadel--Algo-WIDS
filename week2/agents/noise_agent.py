# Integration: NoiseAgent will be instantiated and registered with EventLoop.
# At each scheduled tick, EventLoop calls agent.get_action(snapshot).
# The returned action dict is converted to an Order and processed by MatchingEngine.

import numpy as np
from week2.agents.base_agent import Agent


class NoiseAgent(Agent):
    """Zero-Intelligence trader acting as liquidity consumer.

    Uses Brownian motion to update internal fair value estimate.
    """

    def __init__(self, agent_id: int, cash: float, inventory: int,
                 initial_fair_value: float = 100.0, volatility: float = 0.1,
                 seed: int = None):
        super().__init__(agent_id, cash, inventory)
        self._rng = np.random.default_rng(seed)
        self._fair_value = initial_fair_value
        self._volatility = volatility

    def _update_fair_value(self) -> None:
        """Update fair value using Brownian motion."""
        drift = self._rng.normal(0, self._volatility)
        self._fair_value += drift
        if self._fair_value <= 0:
            self._fair_value = 0.01

    def get_action(self, snapshot: dict) -> dict:
        # Update internal fair value estimate
        self._update_fair_value()

        # 50/50 BUY/SELL
        side = "BUY" if self._rng.random() < 0.5 else "SELL"

        # Constraints check
        if side == "BUY" and self.cash <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}
        if side == "SELL" and self.inventory <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Random quantity 1-5
        quantity = int(self._rng.integers(1, 6))

        # 60% MARKET, 40% aggressive LIMIT near touch
        is_market = self._rng.random() < 0.6

        if is_market:
            return {
                "type": "MARKET",
                "side": side,
                "price": None,
                "quantity": quantity,
            }
        else:
            # Aggressive LIMIT near touch, biased by fair_value
            mid_price = snapshot.get("mid_price")
            if mid_price is None:
                mid_price = self._fair_value

            # Small noise around mid_price, biased toward fair_value
            noise = self._rng.normal(0, 0.2)
            fair_bias = (self._fair_value - mid_price) * 0.1
            price = round(mid_price + noise + fair_bias, 2)

            if price <= 0:
                price = 0.01

            return {
                "type": "LIMIT",
                "side": side,
                "price": price,
                "quantity": quantity,
            }
