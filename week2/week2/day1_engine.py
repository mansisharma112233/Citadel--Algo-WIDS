import heapq
from itertools import count

order_id_counter = count()

class Order:
    def __init__(self, side, price, qty, timestamp, order_type="limit"):
        self.id = next(order_id_counter)
        self.side = side
        self.price = price
        self.qty = qty
        self.timestamp = timestamp
        self.type = order_type
        self.status = "open"

class OrderBook:
    def __init__(self):
        self.bids = []  # (-price, timestamp, Order)
        self.asks = []  # ( price, timestamp, Order)

    def add_order(self, order):
        if order.side == "buy":
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, ( order.price, order.timestamp, order))

    def best_bid(self):
        return self.bids[0][2] if self.bids else None

    def best_ask(self):
        return self.asks[0][2] if self.asks else None
