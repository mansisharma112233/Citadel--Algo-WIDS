# Integration: Agents will be called by EventLoop at scheduled intervals.
# The returned action dict will be converted to an Order and sent to MatchingEngine.

from abc import ABC, abstractmethod


class Agent(ABC):
    """Abstract base class for all trading agents."""

    def __init__(self, agent_id: int, cash: float, inventory: int):
        self.agent_id = agent_id
        self.cash = cash
        self.inventory = inventory

    @abstractmethod
    def get_action(self, snapshot: dict) -> dict:
        """Return an action dict based on market snapshot.

        Args:
            snapshot: Read-only market data dict with keys like:
                - best_bid
                - best_ask
                - mid_price
                - spread

        Returns:
            Action dict with keys:
                - type: "LIMIT" | "MARKET" | "CANCEL" | "NONE"
                - side: "BUY" | "SELL"
                - price: float | None
                - quantity: int
        """
        pass
