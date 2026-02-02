# Integration: RandomAgent will be instantiated and registered with EventLoop.
# At each scheduled tick, EventLoop calls agent.get_action(snapshot).
# The returned action dict is converted to an Order and processed by MatchingEngine.

import random
from week2.agents.base_agent import Agent


class RandomAgent(Agent):
    """Random trading agent for stress testing."""

    def __init__(self, agent_id: int, cash: float, inventory: int, seed: int = None):
        super().__init__(agent_id, cash, inventory)
        self._rng = random.Random(seed)

    def get_action(self, snapshot: dict) -> dict:
        # 20% chance to do nothing
        if self._rng.random() < 0.2:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Determine side with inventory bias
        if self.inventory > 10:
            # Too long, bias toward SELL
            side = "SELL" if self._rng.random() < 0.7 else "BUY"
        elif self.inventory < -10:
            # Too short, bias toward BUY
            side = "BUY" if self._rng.random() < 0.7 else "SELL"
        else:
            # 50/50
            side = self._rng.choice(["BUY", "SELL"])

        # Constraints check
        if side == "BUY" and self.cash <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}
        if side == "SELL" and self.inventory <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Random quantity 1-5
        quantity = self._rng.randint(1, 5)

        # Decide LIMIT vs MARKET (80% LIMIT, 20% MARKET)
        is_market = self._rng.random() < 0.2

        if is_market:
            return {
                "type": "MARKET",
                "side": side,
                "price": None,
                "quantity": quantity,
            }
        else:
            # LIMIT order: price near mid_price with small noise
            mid_price = snapshot.get("mid_price")
            if mid_price is None:
                mid_price = 100.0  # fallback default

            noise = self._rng.uniform(-0.5, 0.5)
            price = round(mid_price + noise, 2)
            if price <= 0:
                price = 0.01

            return {
                "type": "LIMIT",
                "side": side,
                "price": price,
                "quantity": quantity,
            }
