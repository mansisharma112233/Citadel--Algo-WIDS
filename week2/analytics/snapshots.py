# Integration: event_loop calls record() every 1 second via snapshot_event.

import pandas as pd


class L1Snapshots:
    """Record best bid/ask every 1 second."""

    def __init__(self):
        self.records: list[dict] = []

    def record(self, timestamp: float, orderbook) -> None:
        """Record L1 snapshot from orderbook.

        Args:
            timestamp: simulation timestamp
            orderbook: HeapOrderBook instance to read best bid/ask from
        """
        best_bid = orderbook.best_bid()
        best_ask = orderbook.best_ask()

        if best_bid is not None and best_ask is not None:
            spread = best_ask - best_bid
            mid_price = (best_ask + best_bid) / 2
        else:
            spread = None
            mid_price = None

        self.records.append({
            "timestamp": timestamp,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
        })

    # Backward compatibility alias
    def record_snapshot(self, timestamp: float, orderbook) -> None:
        self.record(timestamp, orderbook)

    def to_dataframe(self) -> pd.DataFrame:
        """Return pandas DataFrame indexed by time."""
        df = pd.DataFrame(self.records)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df.set_index("timestamp")
        return df

    # Backward compatibility alias
    @property
    def snapshots(self):
        return self.records


# Backward compatibility alias
SnapshotRecorder = L1Snapshots
