"""
Week 3: Stylized Facts Analysis.

Analyzes market_trace.csv for stylized facts:
1. Log returns time series
2. Autocorrelation of absolute returns (volatility clustering)
3. Fat-tailed return distribution vs Gaussian
4. Herding behavior among momentum agents

Usage:
    python week3/analysis/stylized_facts.py
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Output directory
RESULTS_DIR = os.path.join(PROJECT_ROOT, "week3/results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_market_trace():
    """Load market_trace.csv and return DataFrame."""
    trace_path = os.path.join(SCRIPT_DIR, "market_trace.csv")
    df = pd.read_csv(trace_path)
    print(f"Loaded {len(df)} rows from market_trace.csv")
    return df


def compute_log_returns(df: pd.DataFrame) -> pd.Series:
    """
    Compute log returns from mid_price.
    
    Returns:
        Series of log returns (excluding NaN)
    """
    # Get unique mid_prices per timestamp (take first occurrence)
    mid_prices = df.groupby("timestamp")["mid_price"].first().sort_index()
    
    # Compute log returns: r_t = log(P_t / P_{t-1})
    log_returns = np.log(mid_prices / mid_prices.shift(1)).dropna()
    
    print(f"Computed {len(log_returns)} log returns")
    return log_returns


def plot_returns_timeseries(log_returns: pd.Series):
    """Plot returns over time."""
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(log_returns.index, log_returns.values, linewidth=0.5, color="blue", alpha=0.7)
    ax.axhline(y=0, color="red", linestyle="--", linewidth=0.5)
    
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Log Returns")
    ax.set_title("Log Returns Time Series")
    ax.grid(True, alpha=0.3)
    
    # Add statistics annotation
    stats_text = f"Mean: {log_returns.mean():.6f}\nStd: {log_returns.std():.6f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    fig.tight_layout()
    
    output_path = os.path.join(RESULTS_DIR, "returns_timeseries.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")


def compute_and_plot_acf_abs_returns(log_returns: pd.Series, max_lag: int = 50):
    """
    Compute autocorrelation of |returns| and plot.
    
    Volatility clustering: |r_t| is positively autocorrelated.
    """
    abs_returns = np.abs(log_returns)
    
    # Compute autocorrelation for each lag
    acf_values = []
    for lag in range(max_lag + 1):
        if lag == 0:
            acf_values.append(1.0)
        else:
            corr = abs_returns.autocorr(lag=lag)
            acf_values.append(corr if not np.isnan(corr) else 0.0)
    
    # Plot ACF
    fig, ax = plt.subplots(figsize=(10, 5))
    
    lags = range(max_lag + 1)
    ax.bar(lags, acf_values, color="steelblue", alpha=0.7, width=0.8)
    
    # Confidence interval (95%) for white noise
    n = len(abs_returns)
    conf_interval = 1.96 / np.sqrt(n)
    ax.axhline(y=conf_interval, color="red", linestyle="--", linewidth=1, label="95% CI")
    ax.axhline(y=-conf_interval, color="red", linestyle="--", linewidth=1)
    ax.axhline(y=0, color="black", linewidth=0.5)
    
    ax.set_xlabel("Lag")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("Autocorrelation of Absolute Returns (Volatility Clustering)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    
    output_path = os.path.join(RESULTS_DIR, "acf_abs_returns.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")
    
    # Print some ACF values
    print(f"ACF of |returns|: lag1={acf_values[1]:.4f}, lag5={acf_values[5]:.4f}, lag10={acf_values[10]:.4f}")


def plot_histogram_vs_gaussian(log_returns: pd.Series):
    """Plot histogram of returns and overlay Gaussian."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histogram of returns
    n, bins, patches = ax.hist(log_returns, bins=100, density=True, alpha=0.7,
                                color="steelblue", edgecolor="black", linewidth=0.5,
                                label="Empirical Returns")
    
    # Overlay Gaussian with same mean/std
    mu = log_returns.mean()
    sigma = log_returns.std()
    x = np.linspace(log_returns.min(), log_returns.max(), 200)
    gaussian = stats.norm.pdf(x, mu, sigma)
    ax.plot(x, gaussian, color="red", linewidth=2, label=f"Gaussian (μ={mu:.4f}, σ={sigma:.4f})")
    
    ax.set_xlabel("Log Returns")
    ax.set_ylabel("Density")
    ax.set_title("Return Distribution vs Gaussian (Fat Tails Test)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    
    output_path = os.path.join(RESULTS_DIR, "histogram_vs_gaussian.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")


def compute_kurtosis(log_returns: pd.Series):
    """Compute and print kurtosis."""
    # Excess kurtosis (Normal = 0)
    excess_kurtosis = stats.kurtosis(log_returns, fisher=True)
    # Regular kurtosis (Normal = 3)
    regular_kurtosis = stats.kurtosis(log_returns, fisher=False)
    
    print("\n--- Kurtosis Analysis ---")
    print(f"Excess Kurtosis: {excess_kurtosis:.4f} (Normal = 0)")
    print(f"Regular Kurtosis: {regular_kurtosis:.4f} (Normal = 3)")
    
    if excess_kurtosis > 0:
        print("→ Distribution is LEPTOKURTIC (fat tails, peaked center)")
    elif excess_kurtosis < 0:
        print("→ Distribution is PLATYKURTIC (thin tails, flat center)")
    else:
        print("→ Distribution is MESOKURTIC (normal-like)")
    
    # Skewness
    skewness = stats.skew(log_returns)
    print(f"Skewness: {skewness:.4f} (Normal = 0)")
    
    return excess_kurtosis


def analyze_herding_behavior(df: pd.DataFrame):
    """
    Track positions of agents and compute herding correlation.
    
    Herding = high correlation in positions among similar agents.
    
    Agent ID Ranges (from market_trace.py):
    - PPO: Reinforcement learning agent
    - 100-149: Noise traders (50 total)
    - 200-209: Market makers (10 total)
    """
    # Get unique agent IDs (excluding PPO)
    agent_ids = df[df["agent_id"] != "PPO"]["agent_id"].dropna().unique()
    
    # Convert string IDs to integers for range checking
    numeric_ids = []
    for aid in agent_ids:
        try:
            numeric_ids.append(int(aid))
        except (ValueError, TypeError):
            pass
    
    # Try market makers first (IDs 200-209)
    mm_ids = [aid for aid in numeric_ids if 200 <= aid < 210]
    
    # Try noise traders (IDs 100-149)
    noise_ids = [aid for aid in numeric_ids if 100 <= aid < 150]
    
    print(f"\nFound {len(mm_ids)} market makers, {len(noise_ids)} noise traders")
    
    # Use noise traders for herding analysis (larger sample)
    momentum_ids = noise_ids[:20] if len(noise_ids) >= 2 else mm_ids
    
    if len(momentum_ids) < 2:
        print("Insufficient agents for herding analysis.")
        return
    
    print(f"Analyzing herding among {len(momentum_ids)} agents")
    
    # Track cumulative position for each agent over time
    # Position: +1 for BUY, -1 for SELL
    positions = {}
    
    for agent_id in momentum_ids:
        # Use string comparison since agent_ids are stored as strings
        agent_df = df[df["agent_id"] == str(agent_id)].copy()
        agent_df = agent_df.sort_values("timestamp")
        
        if agent_df.empty:
            continue
        
        # Convert actions to position changes
        agent_df["position_change"] = agent_df["action"].map({"BUY": 1, "SELL": -1}).fillna(0)
        agent_df["cumulative_position"] = agent_df["position_change"].cumsum()
        
        positions[agent_id] = agent_df[["timestamp", "cumulative_position"]].set_index("timestamp")
    
    # Create a DataFrame of positions over time
    pos_df = pd.DataFrame()
    for agent_id, pos_series in positions.items():
        pos_df[agent_id] = pos_series["cumulative_position"]
    
    # Forward fill missing values and fill NaN with 0
    pos_df = pos_df.sort_index().ffill().fillna(0)
    
    if pos_df.empty or len(pos_df) < 10:
        print("Insufficient position data for herding analysis.")
        return
    
    # Compute rolling pairwise correlation
    window_size = min(100, len(pos_df) // 5)
    if window_size < 10:
        window_size = 10
    
    # Compute rolling correlation matrix and extract mean pairwise correlation
    rolling_correlations = []
    timestamps = []
    
    for i in range(window_size, len(pos_df), window_size // 2):
        window_df = pos_df.iloc[i - window_size:i]
        
        if window_df.shape[1] < 2:
            continue
            
        corr_matrix = window_df.corr()
        
        # Extract upper triangle (excluding diagonal)
        upper_tri = np.triu(corr_matrix.values, k=1)
        mask = upper_tri != 0
        if mask.sum() > 0:
            mean_corr = upper_tri[mask].mean()
            rolling_correlations.append(mean_corr)
            timestamps.append(pos_df.index[i])
    
    if len(rolling_correlations) == 0:
        print("Could not compute rolling correlations.")
        return
    
    # Plot herding correlation over time
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(timestamps, rolling_correlations, linewidth=1, color="purple", alpha=0.8)
    ax.axhline(y=0, color="black", linestyle="--", linewidth=0.5)
    ax.axhline(y=np.mean(rolling_correlations), color="red", linestyle="--", linewidth=1,
               label=f"Mean: {np.mean(rolling_correlations):.3f}")
    
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Mean Pairwise Correlation")
    ax.set_title(f"Herding Behavior: Rolling Position Correlation (window={window_size})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1, 1)
    
    fig.tight_layout()
    
    output_path = os.path.join(RESULTS_DIR, "herding_correlation.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")
    
    print(f"Mean herding correlation: {np.mean(rolling_correlations):.4f}")
    print(f"Max herding correlation: {np.max(rolling_correlations):.4f}")


def main():
    print("=" * 60)
    print("WEEK 3: STYLIZED FACTS ANALYSIS")
    print("=" * 60)
    
    # Load data
    df = load_market_trace()
    
    # 1) Compute log returns from mid_price
    print("\n--- Computing Log Returns ---")
    log_returns = compute_log_returns(df)
    
    # 2) Plot returns over time
    print("\n--- Plotting Returns Time Series ---")
    plot_returns_timeseries(log_returns)
    
    # 3) Compute and plot ACF of |returns|
    print("\n--- Autocorrelation of Absolute Returns ---")
    compute_and_plot_acf_abs_returns(log_returns)
    
    # 4) Plot histogram vs Gaussian
    print("\n--- Return Distribution vs Gaussian ---")
    plot_histogram_vs_gaussian(log_returns)
    
    # 5) Compute kurtosis
    excess_kurtosis = compute_kurtosis(log_returns)
    
    # 6) Herding analysis
    print("\n--- Herding Behavior Analysis ---")
    analyze_herding_behavior(df)
    
    # Summary
    print("\n" + "=" * 60)
    print("STYLIZED FACTS SUMMARY")
    print("=" * 60)
    print(f"• Log returns computed: {len(log_returns)}")
    print(f"• Excess kurtosis: {excess_kurtosis:.4f} (fat tails if > 0)")
    print(f"• Plots saved to: {RESULTS_DIR}")
    print("  - returns_timeseries.png")
    print("  - acf_abs_returns.png")
    print("  - histogram_vs_gaussian.png")
    print("  - herding_correlation.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
