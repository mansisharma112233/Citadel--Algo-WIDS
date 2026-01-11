import random
from .base import Agent

class NoiseTrader(Agent):
    def get_action(self, market_snapshot, fair_value):
        side = random.choice(["buy", "sell"])
        qty = random.randint(1, 5)

        if random.random() < 0.7:
            return ("market", side, qty)
        else:
            price = fair_value + random.uniform(-1, 1)
            return ("limit", side, round(price, 2), qty)
