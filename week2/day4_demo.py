from day2_matching_engine import OrderBook, Order
from day4_analytics import MarketAnalytics

ob = OrderBook()
analytics = MarketAnalytics()

t = 1

# Add sell orders
for price, qty in [(101, 10), (102, 20), (103, 30)]:
    ob.add_limit(Order("sell", price, qty, t))
    t += 1

# Market buy
ob.add_market("buy", 60, t)

# Record trades
for trade in ob.trades:
    analytics.record_trade(trade, aggressor="buy")

# Record L1 snapshot
best_bid = ob.bids[0][2].price if ob.bids else None
best_ask = ob.asks[0][2].price if ob.asks else None
analytics.record_l1(t, best_bid, best_ask)

print("VWAP:", analytics.compute_vwap())
print("Mid-price volatility:", analytics.mid_price_volatility())
