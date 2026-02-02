# Integration: MomentumAgent will be instantiated and registered with EventLoop.
# At each scheduled tick, EventLoop calls agent.get_action(snapshot).
# The returned action dict is converted to an Order and processed by MatchingEngine.

from collections import deque
from week2.agents.base_agent import Agent


class MomentumAgent(Agent):
    """Trend-following agent using SMA crossover strategy.

    Buys when price > SMA(50), sells when price < SMA(50).
    """

    def __init__(self, agent_id: int, cash: float, inventory: int,
                 lookback: int = 50):
        super().__init__(agent_id, cash, inventory)
        self._lookback = lookback
        self._price_history: deque[float] = deque(maxlen=lookback)

    def get_action(self, snapshot: dict) -> dict:
        mid_price = snapshot.get("mid_price")

        # Need valid mid_price to proceed
        if mid_price is None:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Append to history
        self._price_history.append(mid_price)

        # Need full history to compute SMA
        if len(self._price_history) < self._lookback:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Compute SMA
        sma = sum(self._price_history) / len(self._price_history)

        # Fixed quantity
        quantity = 2

        # Decision logic
        if mid_price > sma:
            side = "BUY"
        elif mid_price < sma:
            side = "SELL"
        else:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        # Constraints check
        if side == "BUY" and self.cash <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}
        if side == "SELL" and self.inventory <= 0:
            return {"type": "NONE", "side": None, "price": None, "quantity": 0}

        return {
            "type": "MARKET",
            "side": side,
            "price": None,
            "quantity": quantity,
        }
