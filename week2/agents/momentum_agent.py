from collections import deque
from .base import Agent

class MomentumAgent(Agent):
    def __init__(self, agent_id, window=50):
        super().__init__(agent_id)
        self.window = window
        self.prices = deque(maxlen=window)

    def update_price(self, price):
        self.prices.append(price)

    def get_action(self, market_snapshot):
        if len(self.prices) < self.window:
            return None

        price = self.prices[-1]
        sma = sum(self.prices) / len(self.prices)

        if price > sma:
            return ("market", "buy", 1)
        if price < sma:
            return ("market", "sell", 1)

        return None
