import heapq
from collections import deque
from itertools import count

order_counter = count()

class Order:
    def __init__(self, side, price, qty, timestamp):
        self.id = next(order_counter)
        self.side = side      # 'buy' or 'sell'
        self.price = price
        self.qty = qty
        self.timestamp = timestamp

class OrderBook:
    def __init__(self):
        self.bids = []   # max-heap: (-price, timestamp, order)
        self.asks = []   # min-heap: (price, timestamp, order)
        self.trades = []

    def add_limit_order(self, order):
        if order.side == 'buy':
            heapq.heappush(self.bids, (-order.price, order.timestamp, order))
        else:
            heapq.heappush(self.asks, (order.price, order.timestamp, order))
        self.match()

    def add_market_order(self, side, qty, timestamp):
        price = float('inf') if side == 'buy' else 0
        order = Order(side, price, qty, timestamp)
        self.execute_market(order)

    def match(self):
        while self.bids and self.asks:
            best_bid = self.bids[0][2]
            best_ask = self.asks[0][2]

            if best_bid.price >= best_ask.price:
                traded_qty = min(best_bid.qty, best_ask.qty)
                trade_price = best_ask.price

                self.trades.append({
                    'price': trade_price,
                    'qty': traded_qty,
                    'buy_id': best_bid.id,
                    'sell_id': best_ask.id
                })

                best_bid.qty -= traded_qty
                best_ask.qty -= traded_qty

                if best_bid.qty == 0:
                    heapq.heappop(self.bids)
                if best_ask.qty == 0:
                    heapq.heappop(self.asks)
            else:
                break

    def execute_market(self, order):
        book = self.asks if order.side == 'buy' else self.bids
        while book and order.qty > 0:
            best = book[0][2]
            traded_qty = min(order.qty, best.qty)
            trade_price = best.price

            self.trades.append({
                'price': trade_price,
                'qty': traded_qty,
                'aggressor': order.side
            })

            order.qty -= traded_qty
            best.qty -= traded_qty

            if best.qty == 0:
                heapq.heappop(book)

    def top_of_book(self):
        best_bid = -self.bids[0][0] if self.bids else None
        best_ask = self.asks[0][0] if self.asks else None
        return best_bid, best_ask
        if __name__ == "__main__":
    stream = [
        ("limit","buy",100,5,1),
        ("limit","buy",99,4,2),
        ("limit","sell",102,5,3),
        ("limit","sell",101,3,4),
        ("market","buy",None,4,5),
        ("market","sell",None,2,6),
    ]

    def run():
        ob = OrderBook()
        for typ, side, price, qty, ts in stream:
            if typ == "limit":
                ob.add_limit(Order(side, price, qty, ts))
            else:
                ob.add_market(side, qty, ts)
        return ob

    ob1 = run()
    ob2 = run()

    print("Trades:")
    for t in ob1.trades:
        print(t)

    print("\nTop 5 Depth:")
    print(ob1.top_5_levels())

    print("\nDeterministic replay:", ob1.trades == ob2.trades)


