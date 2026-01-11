import random
from .base import Agent

class RandomAgent(Agent):
    def get_action(self, market_snapshot):
        side = random.choice(["buy", "sell"])
        return ("market", side, 1)
