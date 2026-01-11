import pandas as pd
import numpy as np

class MarketAnalytics:
    def __init__(self):
        # Append-only logs
        self.trade_tape = []
        self.l1_snapshots = []

    
    def record_trade(self, trade, aggressor=None):
        self.trade_tape.append({
            "timestamp": trade.timestamp,
            "price": trade.price,
            "size": trade.qty,
            "aggressor": aggressor
        })

    def tape_df(self):
        df = pd.DataFrame(self.trade_tape)
        return df.sort_values("timestamp")

   
    def record_l1(self, timestamp, best_bid, best_ask):
        if best_bid is None or best_ask is None:
            return

        self.l1_snapshots.append({
            "timestamp": timestamp,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": best_ask - best_bid,
            "mid_price": (best_bid + best_ask) / 2
        })

    def l1_df(self):
        df = pd.DataFrame(self.l1_snapshots)
        return df.sort_values("timestamp")

   
    def compute_vwap(self):
        df = self.tape_df()
        return (df["price"] * df["size"]).sum() / df["size"].sum()

    def mid_price_volatility(self, freq="1S"):
        df = self.l1_df()
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df.set_index("timestamp", inplace=True)

        mid = df["mid_price"].resample(freq).last().dropna()
        returns = np.log(mid).diff().dropna()
        return returns.std()
