import os
import sys
import time
import random
from bisect import bisect_right

# Ensure project root is on path so we can import week2 package modules
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook


def make_buy_orders(n: int, seed: int = 42):
    random.seed(seed)
    orders = []
    for i in range(n):
        price = random.uniform(10.0, 100.0)
        qty = random.randint(1, 100)
        orders.append(Order(order_id=i + 1, side="BUY", price=price, quantity=qty))
    return orders


def benchmark_list_insertion(orders):
    prices = []  # store -price to keep descending order
    orders_list = []
    start = time.time()
    for o in orders:
        key = -o.price
        idx = bisect_right(prices, key)
        prices.insert(idx, key)
        orders_list.insert(idx, o)
    return time.time() - start


def benchmark_heap_insertion(orders):
    book = HeapOrderBook()
    start = time.time()
    for o in orders:
        book.add_order(o)
    return time.time() - start


def main():
    N = 10000
    orders = make_buy_orders(N)

    t_list = benchmark_list_insertion(orders)
    t_heap = benchmark_heap_insertion(orders)

    print(f"Benchmark insertion of {N} BUY limit orders")
    print(f"Plain Python list insertion: {t_list:.4f} seconds")
    print(f"Heap-based order book insertion: {t_heap:.4f} seconds")


if __name__ == "__main__":
    main()
