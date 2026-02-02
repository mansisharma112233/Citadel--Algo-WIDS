# Integration: event_loop calls record_trades() after matching engine returns trades.

import pandas as pd


class TradeTape:
    """Append-only log of every trade execution."""

    def __init__(self):
        self.trades: list[dict] = []

    def record_trade(self, trade) -> None:
        """Record a single trade (backward compatibility)."""
        self.trades.append({
            "timestamp": trade.timestamp,
            "price": trade.price,
            "quantity": trade.quantity,
            "buyer_id": trade.buyer_order_id,
            "seller_id": trade.seller_order_id,
        })

    def record_trades(self, trades, timestamp: float) -> None:
        """Record multiple trades from matching engine.

        Args:
            trades: list of Trade objects returned by matching engine
            timestamp: simulation timestamp when trades occurred
        """
        for trade in trades:
            self.trades.append({
                "timestamp": timestamp,
                "price": trade.price,
                "quantity": trade.quantity,
                "buyer_id": trade.buyer_order_id,
                "seller_id": trade.seller_order_id,
            })

    def to_dataframe(self) -> pd.DataFrame:
        """Return pandas DataFrame with datetime index."""
        df = pd.DataFrame(self.trades)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df.set_index("timestamp")
        return df

    # Backward compatibility alias
    @property
    def records(self):
        return self.trades
