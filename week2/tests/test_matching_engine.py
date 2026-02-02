"""
Matching Engine Validation Tests.

Verifies correctness of price-time priority matching logic.
"""

import os
import sys

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook
from week2.orderbook.matching_engine import MatchingEngine


def test_market_buy_clears_ask_book():
    # 1) Initialize a fresh OrderBook
    orderbook = HeapOrderBook()
    engine = MatchingEngine(orderbook)

    # 2) Insert ASK limit orders in this exact order:
    #    Price 101, Qty 10
    #    Price 102, Qty 20
    #    Price 103, Qty 30
    ask_orders = [
        Order(order_id=1, side="SELL", price=101, quantity=10),
        Order(order_id=2, side="SELL", price=102, quantity=20),
        Order(order_id=3, side="SELL", price=103, quantity=30),
    ]
    for order in ask_orders:
        orderbook.add_order(order)

    # Verify initial state
    assert orderbook.best_ask() == 101, "Initial best_ask should be 101"
    assert orderbook.best_bid() is None, "Initial bid book should be empty"

    # 3) Submit a MARKET BUY order for quantity = 60
    market_buy = Order(order_id=999, side="BUY", price=None, quantity=60)
    engine.process_order(market_buy)

    # 4) After matching, assert:

    # - Exactly 3 trades occurred
    assert len(engine.trades) == 3, f"Expected 3 trades, got {len(engine.trades)}"

    # - Trade prices are [101, 102, 103] in that order
    trade_prices = [t.price for t in engine.trades]
    assert trade_prices == [101, 102, 103], f"Expected trade prices [101, 102, 103], got {trade_prices}"

    # - Total traded quantity is 60
    total_qty = sum(t.quantity for t in engine.trades)
    assert total_qty == 60, f"Expected total quantity 60, got {total_qty}"

    # - Individual trade quantities are correct
    trade_quantities = [t.quantity for t in engine.trades]
    assert trade_quantities == [10, 20, 30], f"Expected quantities [10, 20, 30], got {trade_quantities}"

    # - Ask book is now empty
    assert orderbook.best_ask() is None, "Ask book should be empty after market buy"

    # - Bid book is unchanged / empty
    assert orderbook.best_bid() is None, "Bid book should remain empty"

    # 5) Print success message
    print("Matching Engine Validation PASSED")


if __name__ == "__main__":
    test_market_buy_clears_ask_book()
