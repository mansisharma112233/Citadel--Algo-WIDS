import numpy as np

class FairValueProcess:
    def __init__(self, price=100, sigma=1, seed=42):
        self.price = price
        self.rng = np.random.default_rng(seed)
        self.sigma = sigma

    def step(self):
        self.price += self.rng.normal(0, self.sigma)
        return max(self.price, 0)
