import heapq
from itertools import count

order_id_counter = count()

class Order:
    def __init__(self, side, price, qty, timestamp, order_type="limit"):
        self.id = next(order_id_counter)
        self.side = side            # "buy" or "sell"
        self.price = price
        self.qty = qty
        self.timestamp = timestamp
        self.type = order_type     # "limit" or "market"
        self.status = "open"

class Trade:
    def __init__(self, price, qty, buyer_id, seller_id, timestamp):
        self.price = price
        self.qty = qty
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.timestamp = timestamp

class OrderBook:
    def __init__(self):
        self.bids = []   # (-price, timestamp, Order)
        self.asks = []   # ( price, timestamp, Order)
        self.trades = []

    def add_limit_order(self, order):
        if order.side == "buy":
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, ( order.price, order.timestamp, order))
        self.match()

    def add_market_order(self, side, qty, timestamp):
        price = float("inf") if side == "buy" else 0
        order = Order(side, price, qty, timestamp, order_type="market")
        self.match(incoming=order)

    def match(self, incoming=None):
        """
        Core matching loop:
        - Enforces price-time priority
        - Handles partial fills
        - Walks the book
        """

        while True:
            if not self.bids or not self.asks:
                break

            best_bid = self.bids[0][2]
            best_ask = self.asks[0][2]

            if best_bid.price < best_ask.price:
                break

            trade_qty = min(best_bid.qty, best_ask.qty)
            trade_price = best_ask.price

            self.trades.append(
                Trade(
                    price=trade_price,
                    qty=trade_qty,
                    buyer_id=best_bid.id,
                    seller_id=best_ask.id,
                    timestamp=max(best_bid.timestamp, best_ask.timestamp)
                )
            )

            best_bid.qty -= trade_qty
            best_ask.qty -= trade_qty

            if best_bid.qty == 0:
                best_bid.status = "filled"
                heapq.heappop(self.bids)

            if best_ask.qty == 0:
                best_ask.status = "filled"
                heapq.heappop(self.asks)

        if incoming:
            self._execute_market(incoming)

    def _execute_market(self, order):
        book = self.asks if order.side == "buy" else self.bids

        while order.qty > 0 and book:
            best = book[0][2]

            trade_qty = min(order.qty, best.qty)

            self.trades.append(
                Trade(
                    price=best.price,
                    qty=trade_qty,
                    buyer_id=order.id if order.side == "buy" else best.id,
                    seller_id=best.id if order.side == "buy" else order.id,
                    timestamp=order.timestamp
                )
            )

            order.qty -= trade_qty
            best.qty -= trade_qty

            if best.qty == 0:
                best.status = "filled"
                heapq.heappop(book)

        order.status = "filled" if order.qty == 0 else "partial"
