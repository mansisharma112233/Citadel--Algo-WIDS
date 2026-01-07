import heapq
from itertools import count
from day2_matching_engine import OrderBook, Order

_event_id = count()

class Event:
    def __init__(self, time, handler, payload=None):
        self.time = time
        self.handler = handler
        self.payload = payload
        self.id = next(_event_id)

    def __lt__(self, other):
        return (self.time, self.id) < (other.time, other.id)


class MarketEngine:
    def __init__(self):
        self.time = 0
        self.event_queue = []
        self.orderbook = OrderBook()
        self.running = True

    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)

    def run(self):
        while self.event_queue and self.running:
            event = heapq.heappop(self.event_queue)
            self.time = event.time
            event.handler(self, event.payload)
