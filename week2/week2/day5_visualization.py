import matplotlib.pyplot as plt
import mplfinance as mpf

def plot_candles(tape_df, filename):
    df = tape_df.copy()
    df.index = df.index.to_series().astype("datetime64[s]")
    ohlc = df["price"].resample("1min").ohlc()
    volume = df["size"].resample("1min").sum()

    mpf.plot(
        ohlc,
        type="candle",
        volume=volume,
        style="classic",
        savefig=filename
    )
