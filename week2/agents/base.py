from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, agent_id, balance=0, inventory=0):
        self.id = agent_id
        self.balance = balance
        self.inventory = inventory

    @abstractmethod
    def get_action(self, market_snapshot):
        pass
