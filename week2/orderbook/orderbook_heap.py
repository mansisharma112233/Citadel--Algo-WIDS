from collections import deque
import heapq
from typing import Dict, Deque, Optional
from week2.orderbook.order import Order


class HeapOrderBook:
    """Heap-based order book (no matching or cancellations).

    bids: dict[price -> deque[Order]] (price -> FIFO queue)
    asks: dict[price -> deque[Order]]
    bid_heap: max-heap via storing -price
    ask_heap: min-heap storing price
    """

    def __init__(self) -> None:
        self.bids: Dict[float, Deque[Order]] = {}
        self.asks: Dict[float, Deque[Order]] = {}
        self.bid_heap: list[float] = []
        self.ask_heap: list[float] = []

    def add_order(self, order: Order) -> None:
        assert order.price is not None, "limit orders must have a price"
        price = order.price
        if order.side == "BUY":
            if price not in self.bids:
                self.bids[price] = deque()
                heapq.heappush(self.bid_heap, -price)
            self.bids[price].append(order)
        else:
            if price not in self.asks:
                self.asks[price] = deque()
                heapq.heappush(self.ask_heap, price)
            self.asks[price].append(order)

    def best_bid(self) -> Optional[float]:
        while self.bid_heap:
            price = -self.bid_heap[0]
            if price in self.bids and self.bids[price]:
                return price
            heapq.heappop(self.bid_heap)
        return None

    def best_ask(self) -> Optional[float]:
        while self.ask_heap:
            price = self.ask_heap[0]
            if price in self.asks and self.asks[price]:
                return price
            heapq.heappop(self.ask_heap)
        return None
