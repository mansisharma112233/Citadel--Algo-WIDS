"""
Visualization and Report Generation for Week 2 Simulation.

Provides plotting functions for market data and PDF export.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for PDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# mplfinance is optional - use manual candlestick if not available
try:
    import mplfinance as mpf
    HAS_MPLFINANCE = True
except ImportError:
    HAS_MPLFINANCE = False


def plot_midprice_and_spread(snapshot_df: pd.DataFrame, title: str = "") -> plt.Figure:
    """
    Create figure with two subplots: mid-price and spread over time.

    Args:
        snapshot_df: DataFrame with mid_price and spread columns (datetime index)
        title: Title for the figure

    Returns:
        matplotlib Figure with two subplots
    """
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold")

    # Subplot 1: Mid-price line
    ax1 = axes[0]
    if not snapshot_df.empty and "mid_price" in snapshot_df.columns:
        mid = snapshot_df["mid_price"].dropna()
        if not mid.empty:
            x = range(len(mid))
            ax1.plot(x, mid.values, color="blue", linewidth=0.8)
            ax1.set_ylabel("Mid-Price")
            ax1.set_title("Mid-Price Over Time")
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "No mid-price data", ha="center", va="center",
                     transform=ax1.transAxes)
    else:
        ax1.text(0.5, 0.5, "No snapshot data", ha="center", va="center",
                 transform=ax1.transAxes)

    # Subplot 2: Spread line
    ax2 = axes[1]
    if not snapshot_df.empty and "spread" in snapshot_df.columns:
        spread = snapshot_df["spread"].dropna()
        if not spread.empty:
            x = range(len(spread))
            ax2.plot(x, spread.values, color="green", linewidth=0.8)
            ax2.set_xlabel("Time (seconds)")
            ax2.set_ylabel("Spread")
            ax2.set_title("Bid-Ask Spread Over Time")
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No spread data", ha="center", va="center",
                     transform=ax2.transAxes)
    else:
        ax2.text(0.5, 0.5, "No snapshot data", ha="center", va="center",
                 transform=ax2.transAxes)

    fig.tight_layout(rect=[0, 0, 1, 0.96] if title else [0, 0, 1, 1])
    return fig


def plot_candlestick(tape_df: pd.DataFrame, title: str = "1-Minute OHLC Candlestick") -> plt.Figure:
    """
    Create candlestick chart from trade tape.

    Resamples trades to 1-minute OHLC bars.

    Args:
        tape_df: DataFrame with price column (datetime index)
        title: Title for the chart

    Returns:
        matplotlib Figure with candlestick chart
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    if tape_df.empty or len(tape_df) < 2:
        ax.text(0.5, 0.5, "No trade data", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title)
        return fig

    # Resample to 1-minute OHLC
    ohlc = tape_df["price"].resample("1min").ohlc().dropna()

    if ohlc.empty or len(ohlc) < 1:
        ax.text(0.5, 0.5, "Insufficient OHLC data", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title)
        return fig

    # Try mplfinance first
    if HAS_MPLFINANCE and len(ohlc) > 1:
        try:
            plt.close(fig)  # Close the basic figure
            ohlc_plot = ohlc.copy()
            ohlc_plot.columns = ["Open", "High", "Low", "Close"]
            fig_mpf, axes_mpf = mpf.plot(
                ohlc_plot,
                type="candle",
                style="charles",
                returnfig=True,
                figsize=(10, 6),
            )
            axes_mpf[0].set_title(title)
            return fig_mpf
        except Exception:
            # Fall back to manual plotting
            fig, ax = plt.subplots(figsize=(10, 6))

    # Manual candlestick plotting
    x = range(len(ohlc))
    for i in range(len(ohlc)):
        o, h, l, c = ohlc.iloc[i]["open"], ohlc.iloc[i]["high"], ohlc.iloc[i]["low"], ohlc.iloc[i]["close"]
        color = "green" if c >= o else "red"
        # Wick (high-low line)
        ax.plot([i, i], [l, h], color="black", linewidth=0.5)
        # Body (open-close bar)
        body_height = abs(c - o)
        if body_height < 0.001:
            body_height = 0.001  # Minimum visible height
        ax.bar(i, body_height, bottom=min(o, c), color=color,
               width=0.6, edgecolor="black", linewidth=0.5)

    ax.set_title(title)
    ax.set_xlabel("Minute")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


def plot_volume_bars(tape_df: pd.DataFrame, title: str = "Volume per Minute") -> plt.Figure:
    """
    Create volume bar chart from trade tape.

    Args:
        tape_df: DataFrame with quantity column (datetime index)
        title: Title for the chart

    Returns:
        matplotlib Figure with volume bars
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    if tape_df.empty:
        ax.text(0.5, 0.5, "No trade data", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title)
        return fig

    volume = tape_df["quantity"].resample("1min").sum().dropna()

    if volume.empty:
        ax.text(0.5, 0.5, "No volume data", ha="center", va="center",
                transform=ax.transAxes)
        ax.set_title(title)
        return fig

    ax.bar(range(len(volume)), volume.values, color="steelblue", alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Minute")
    ax.set_ylabel("Volume")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


def export_pdf(figures: list, filename: str) -> None:
    """
    Export figures to PDF, one figure per page.

    Args:
        figures: List of matplotlib Figure objects
        filename: Output PDF filename
    """
    with PdfPages(filename) as pdf:
        for fig in figures:
            pdf.savefig(fig)
            plt.close(fig)
