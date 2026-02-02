# Integration: MarketMakerAgent will be instantiated and registered with EventLoop.
# At each scheduled tick, EventLoop calls agent.get_action(snapshot).
# The returned action dicts are converted to Orders and processed by MatchingEngine.

from week2.agents.base_agent import Agent


class MarketMakerAgent(Agent):
    """Market maker that quotes both sides of the book.

    Provides liquidity by placing BUY and SELL limit orders around mid-price.
    Adjusts quotes based on inventory to manage risk.
    """

    def __init__(self, agent_id: int, cash: float, inventory: int,
                 base_spread: float = 2.0, inventory_skew_factor: float = 0.1,
                 quantity: int = 5):
        super().__init__(agent_id, cash, inventory)
        self.base_spread = base_spread
        self.inventory_skew_factor = inventory_skew_factor
        self.quantity = quantity

    def get_action(self, snapshot: dict) -> list[dict]:
        """Return two limit orders: one BUY (bid) and one SELL (ask)."""
        mid_price = snapshot.get("mid_price")

        if mid_price is None:
            return [{"type": "NONE", "side": None, "price": None, "quantity": 0}]

        # Base bid and ask
        half_spread = self.base_spread / 2
        bid_price = mid_price - half_spread
        ask_price = mid_price + half_spread

        # Inventory skew: if long, lower ask to sell more; if short, raise bid to buy more
        skew = self.inventory * self.inventory_skew_factor
        bid_price -= skew  # Lower bid if long (less eager to buy)
        ask_price -= skew  # Lower ask if long (more eager to sell)

        # Ensure positive prices
        bid_price = max(0.01, round(bid_price, 2))
        ask_price = max(0.01, round(ask_price, 2))

        actions = []

        # BUY order at bid (only if we have cash)
        if self.cash > 0:
            actions.append({
                "type": "LIMIT",
                "side": "BUY",
                "price": bid_price,
                "quantity": self.quantity,
            })

        # SELL order at ask (only if we have inventory)
        if self.inventory > 0:
            actions.append({
                "type": "LIMIT",
                "side": "SELL",
                "price": ask_price,
                "quantity": min(self.quantity, self.inventory),
            })

        if not actions:
            return [{"type": "NONE", "side": None, "price": None, "quantity": 0}]

        return actions
