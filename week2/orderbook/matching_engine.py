import time
import itertools
from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook
from week2.orderbook.trade import Trade


class MatchingEngine:
    def __init__(self, orderbook: HeapOrderBook):
        self.orderbook = orderbook
        self.trades: list[Trade] = []
        self._trade_id_counter = itertools.count(1)

    def process_order(self, order: Order) -> None:
        if order.side == "BUY":
            self._match_buy(order)
        else:
            self._match_sell(order)

        # Residual handling
        if order.quantity > 0:
            if order.price is not None:
                # LIMIT order: add remaining to book
                self.orderbook.add_order(order)
            # MARKET order: discard remaining

    def _match_buy(self, order: Order) -> None:
        while order.quantity > 0:
            best_ask = self.orderbook.best_ask()
            if best_ask is None:
                break
            if order.price is not None and order.price < best_ask:
                break

            # Match at best_ask price level
            ask_deque = self.orderbook.asks[best_ask]
            resting = ask_deque[0]

            executed_qty = min(order.quantity, resting.quantity)
            order.quantity -= executed_qty
            resting.quantity -= executed_qty

            trade = Trade(
                trade_id=next(self._trade_id_counter),
                price=resting.price,
                quantity=executed_qty,
                buyer_order_id=order.order_id,
                seller_order_id=resting.order_id,
                timestamp=time.time(),
            )
            self.trades.append(trade)

            # Cleanup resting order if filled
            if resting.quantity == 0:
                ask_deque.popleft()

            # Cleanup price level if empty
            if not ask_deque:
                del self.orderbook.asks[best_ask]
                # Remove from heap (lazy deletion handled by best_ask)

    def _match_sell(self, order: Order) -> None:
        while order.quantity > 0:
            best_bid = self.orderbook.best_bid()
            if best_bid is None:
                break
            if order.price is not None and order.price > best_bid:
                break

            # Match at best_bid price level
            bid_deque = self.orderbook.bids[best_bid]
            resting = bid_deque[0]

            executed_qty = min(order.quantity, resting.quantity)
            order.quantity -= executed_qty
            resting.quantity -= executed_qty

            trade = Trade(
                trade_id=next(self._trade_id_counter),
                price=resting.price,
                quantity=executed_qty,
                buyer_order_id=resting.order_id,
                seller_order_id=order.order_id,
                timestamp=time.time(),
            )
            self.trades.append(trade)

            # Cleanup resting order if filled
            if resting.quantity == 0:
                bid_deque.popleft()

            # Cleanup price level if empty
            if not bid_deque:
                del self.orderbook.bids[best_bid]
                # Remove from heap (lazy deletion handled by best_bid)


def test_market_buy_clears_asks():
    from week2.orderbook.order import Order
    from week2.orderbook.orderbook_heap import HeapOrderBook

    ob = HeapOrderBook()

    asks = [(101, 10), (102, 20), (103, 30)]
    for price, qty in asks:
        ob.add_order(Order(order_id=price, side="SELL", price=price, quantity=qty))

    engine = MatchingEngine(ob)

    market_buy = Order(order_id=999, side="BUY", price=None, quantity=60)
    engine.process_order(market_buy)

    # Assertions
    assert len(engine.trades) == 3
    prices = [t.price for t in engine.trades]
    assert prices == [101, 102, 103]
    assert ob.best_ask() is None
