from engine import OrderBook, Order

ob = OrderBook()

# Submit ASK ladder
asks = [(101, 10), (102, 20), (103, 30)]
ts = 1

for price, qty in asks:
    ob.add_limit_order(Order("sell", price, qty, ts))
    ts += 1

# Submit massive MARKET BUY
ob.add_market_order("buy", 60, ts)

# Assertions
assert len(ob.trades) == 3
assert sum(t.qty for t in ob.trades) == 60
assert not ob.asks
print("Validation test passed.")
