import random
import pandas as pd
from day2_matching_engine import OrderBook, Order
from day4_analytics import MarketAnalytics
from day5_validation import validate_orderbook, validate_tape
from day5_visualization import plot_candles

random.seed(42)

ob = OrderBook()
analytics = MarketAnalytics()

t = 0

for _ in range(1000):
    side = random.choice(["buy", "sell"])
    price = random.randint(95, 105)
    qty = random.randint(1, 10)

    ob.add_limit(Order(side, price, qty, t))

    for trade in ob.trades:
        analytics.record_trade(trade)

    t += 1

# Build tape
df = analytics.tape_df()
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df.set_index("timestamp", inplace=True)

validate_orderbook(ob)
validate_tape(df)

plot_candles(df, "simulation_report.pdf")

print("Simulation complete.")
