"""
Week 2 Final Deliverable: Full Multi-Agent Simulation with Scenarios and PDF Report.

Runs three scenarios with different agent mixes:
- Scenario A: 100 NoiseAgents
- Scenario B: 80 NoiseAgents + 20 MarketMakerAgents
- Scenario C: 80 NoiseAgents + 20 MomentumAgents

Produces simulation_report.pdf with comparison analysis.

Usage:
    python week2/run_simulation.py
"""

import random
import os
import sys

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook
from week2.orderbook.matching_engine import MatchingEngine
from week2.engine.event_loop import EventLoop
from week2.analytics.tape import TradeTape
from week2.analytics.snapshots import L1Snapshots
from week2.analytics.metrics import compute_vwap, average_spread, compute_midprice_volatility

from week2.agents.noise_agent import NoiseAgent
from week2.agents.market_maker_agent import MarketMakerAgent
from week2.agents.momentum_agent import MomentumAgent

from week2.visualization.report import (
    plot_midprice_and_spread,
    plot_candlestick,
    export_pdf,
)

# ============================================================
# CONFIGURATION (Hardcoded as required)
# ============================================================
SEED = 42
TOTAL_AGENTS = 100
SIM_TIME = 30 * 60  # 30 minutes in seconds
SNAPSHOT_INTERVAL = 1  # 1 second


# ============================================================
# AGENT FACTORY FUNCTIONS
# ============================================================
def create_agents_scenario_a(seed: int) -> list:
    """Scenario A: 100 NoiseAgents."""
    agents = []
    for i in range(100):
        agents.append(NoiseAgent(
            agent_id=i + 1,
            cash=10000.0,
            inventory=50,
            initial_fair_value=100.0,
            volatility=0.1,
            seed=seed + i,
        ))
    return agents


def create_agents_scenario_b(seed: int) -> list:
    """Scenario B: 80 NoiseAgents + 20 MarketMakerAgents."""
    agents = []
    for i in range(80):
        agents.append(NoiseAgent(
            agent_id=i + 1,
            cash=10000.0,
            inventory=50,
            initial_fair_value=100.0,
            volatility=0.1,
            seed=seed + i,
        ))
    for i in range(20):
        agents.append(MarketMakerAgent(
            agent_id=80 + i + 1,
            cash=10000.0,
            inventory=50,
            base_spread=2.0,
            inventory_skew_factor=0.1,
            quantity=5,
        ))
    return agents


def create_agents_scenario_c(seed: int) -> list:
    """Scenario C: 80 NoiseAgents + 20 MomentumAgents."""
    agents = []
    for i in range(80):
        agents.append(NoiseAgent(
            agent_id=i + 1,
            cash=10000.0,
            inventory=50,
            initial_fair_value=100.0,
            volatility=0.1,
            seed=seed + i,
        ))
    for i in range(20):
        agents.append(MomentumAgent(
            agent_id=80 + i + 1,
            cash=10000.0,
            inventory=50,
            lookback=50,
        ))
    return agents


# ============================================================
# SIMULATION RUNNER
# ============================================================
def run_scenario(scenario_name: str, agents: list, seed: int):
    """Run a single simulation scenario."""
    random.seed(seed)
    np.random.seed(seed)

    # 1) Initialize components
    orderbook = HeapOrderBook()
    engine = MatchingEngine(orderbook)
    event_loop = EventLoop()
    tape = TradeTape()
    snapshots = L1Snapshots()

    # 2) Schedule agent action events (staggered, every 3 seconds per agent)
    for idx, agent in enumerate(agents):
        agent_interval = 3.0
        start_offset = (idx / len(agents)) * agent_interval
        t = start_offset
        while t < SIM_TIME:
            event_loop.schedule_event(
                timestamp=t,
                event_type="AGENT_ACTION",
                payload={"agent_idx": idx},
            )
            t += agent_interval

    # Schedule snapshot events every SNAPSHOT_INTERVAL seconds
    for t in range(0, SIM_TIME + 1, SNAPSHOT_INTERVAL):
        event_loop.schedule_event(
            timestamp=float(t),
            event_type="SNAPSHOT",
            payload={},
        )

    # Seed the book with initial orders
    for i in range(50):
        bid_price = round(99.0 - i * 0.1, 2)
        ask_price = round(101.0 + i * 0.1, 2)
        orderbook.add_order(Order(
            order_id=10000 + i,
            side="BUY",
            price=bid_price,
            quantity=10,
            timestamp=0.0,
        ))
        orderbook.add_order(Order(
            order_id=20000 + i,
            side="SELL",
            price=ask_price,
            quantity=10,
            timestamp=0.0,
        ))

    order_id_counter = 30000

    # 3) Event handler with tape and snapshots recording
    def event_handler(event):
        nonlocal order_id_counter

        if event.event_type == "AGENT_ACTION":
            agent_idx = event.payload["agent_idx"]
            agent = agents[agent_idx]

            # Build snapshot for agent
            best_bid = orderbook.best_bid()
            best_ask = orderbook.best_ask()
            if best_bid is not None and best_ask is not None:
                mid_price = (best_bid + best_ask) / 2
                spread = best_ask - best_bid
            else:
                mid_price = 100.0
                spread = None

            snapshot = {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "mid_price": mid_price,
                "spread": spread,
                "timestamp": event.timestamp,
            }

            # Get agent action(s)
            action_result = agent.get_action(snapshot)

            # Handle single action or list of actions
            if isinstance(action_result, dict):
                actions = [action_result]
            else:
                actions = action_result

            for action in actions:
                if action["type"] == "NONE":
                    continue

                # Sanity assertions
                if action["price"] is not None:
                    assert action["price"] >= 0, f"Invalid price: {action['price']}"
                assert action["quantity"] >= 0, f"Invalid quantity: {action['quantity']}"

                if action["quantity"] == 0:
                    continue

                order = Order(
                    order_id=order_id_counter,
                    side=action["side"],
                    price=action["price"],
                    quantity=action["quantity"],
                    timestamp=event.timestamp,
                )
                order_id_counter += 1

                # Process order
                trades_before = len(engine.trades)
                engine.process_order(order)

                # Record new trades to tape
                for trade in engine.trades[trades_before:]:
                    assert trade.price >= 0, f"Invalid trade price: {trade.price}"
                    assert trade.quantity >= 0, f"Invalid trade quantity: {trade.quantity}"
                    tape.record_trade(trade)

                    # Update agent inventories
                    if action["side"] == "BUY":
                        agent.inventory += trade.quantity
                        agent.cash -= trade.price * trade.quantity
                    else:
                        agent.inventory -= trade.quantity
                        agent.cash += trade.price * trade.quantity

        elif event.event_type == "SNAPSHOT":
            best_bid = orderbook.best_bid()
            best_ask = orderbook.best_ask()

            # Sanity assertions
            if best_bid is not None:
                assert best_bid >= 0, f"Invalid best_bid: {best_bid}"
            if best_ask is not None:
                assert best_ask >= 0, f"Invalid best_ask: {best_ask}"
            if best_bid is not None and best_ask is not None:
                spread = best_ask - best_bid
                assert spread >= 0, f"Invalid spread: {spread}"

            # Record snapshot
            snapshots.record(event.timestamp, orderbook)

    # 4) Run the event loop for SIM_TIME
    event_loop.run(event_handler)

    # 5) Convert tape & snapshots to DataFrames
    tape_df = tape.to_dataframe()
    snapshot_df = snapshots.to_dataframe()

    # Compute metrics
    metrics = {}
    if not tape_df.empty:
        metrics["vwap"] = compute_vwap(tape_df)
        metrics["total_trades"] = len(tape_df)
        metrics["total_volume"] = tape_df["quantity"].sum()
    else:
        metrics["vwap"] = None
        metrics["total_trades"] = 0
        metrics["total_volume"] = 0

    if not snapshot_df.empty:
        metrics["avg_spread"] = average_spread(snapshot_df)
        metrics["volatility"] = compute_midprice_volatility(snapshot_df)
    else:
        metrics["avg_spread"] = None
        metrics["volatility"] = None

    return tape_df, snapshot_df, metrics


# ============================================================
# VISUALIZATION HELPERS (using visualization module)
# ============================================================
def generate_scenario_figures(tape_df: pd.DataFrame, snapshot_df: pd.DataFrame,
                              scenario_name: str) -> list:
    """Generate figures for a scenario using visualization module."""
    figures = []

    # Mid-price and spread plot
    fig1 = plot_midprice_and_spread(snapshot_df, title=f"{scenario_name}")
    figures.append(fig1)

    # Candlestick chart
    fig2 = plot_candlestick(tape_df, title=f"{scenario_name}: 1-Min OHLC")
    figures.append(fig2)

    return figures


def create_comparison_table(results: dict):
    """Create a comparison table figure."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    columns = ["Metric", "Scenario A\n(100 Noise)", "Scenario B\n(80 Noise + 20 MM)", "Scenario C\n(80 Noise + 20 Mom)"]
    rows = []

    metrics_names = [
        ("Total Trades", "total_trades"),
        ("Total Volume", "total_volume"),
        ("VWAP", "vwap"),
        ("Avg Spread", "avg_spread"),
        ("Volatility", "volatility"),
    ]

    for label, key in metrics_names:
        row = [label]
        for scenario in ["A", "B", "C"]:
            val = results[scenario]["metrics"].get(key)
            if val is None:
                row.append("N/A")
            elif isinstance(val, float):
                row.append(f"{val:.4f}")
            else:
                row.append(str(val))
        rows.append(row)

    table = ax.table(
        cellText=rows,
        colLabels=columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    ax.set_title("Scenario Comparison", fontsize=14, fontweight="bold", pad=20)
    return fig


def create_setup_page():
    """Create setup/configuration page."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")

    text = f"""
    SIMULATION REPORT
    ═══════════════════════════════════════════════════════════════

    Week 2 Final: Multi-Agent Limit Order Book Simulation

    CONFIGURATION:
    • Total Agents: {TOTAL_AGENTS}
    • Random Seed: {SEED}
    • Simulation Time: {SIM_TIME // 60} minutes ({SIM_TIME} seconds)
    • Snapshot Interval: {SNAPSHOT_INTERVAL} second(s)

    SCENARIOS:
    • Scenario A: 100 NoiseAgents
    • Scenario B: 80 NoiseAgents + 20 MarketMakerAgents
    • Scenario C: 80 NoiseAgents + 20 MomentumAgents

    AGENT PARAMETERS:
    • NoiseAgent: cash=10000, inventory=50, volatility=0.1
    • MarketMakerAgent: cash=10000, inventory=50, spread=2.0
    • MomentumAgent: cash=10000, inventory=50, lookback=50

    ═══════════════════════════════════════════════════════════════
    """

    ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=10,
            verticalalignment="top", fontfamily="monospace")

    return fig


def create_interpretation_page():
    """Create interpretation text page."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")

    text = """
    INTERPRETATION OF RESULTS
    ═══════════════════════════════════════════════════════════════

    Scenario A (100 NoiseAgents):
    • Pure random order flow creates baseline market dynamics
    • Spread fluctuates randomly without systematic tightening
    • Volatility reflects Brownian fair value randomness

    Scenario B (80 NoiseAgents + 20 MarketMakerAgents):
    • Market makers provide two-sided quotes, tightening spreads
    • Expected: Lower average spread compared to Scenario A
    • Market makers absorb noise trader flow, stabilizing prices

    Scenario C (80 NoiseAgents + 20 MomentumAgents):
    • Momentum agents amplify trends via positive feedback
    • Expected: Higher volatility compared to Scenario A
    • Trend-following can create larger price swings

    KEY OBSERVATIONS:
    • Market makers reduce spread and may reduce volatility
    • Momentum traders increase volatility and trend persistence
    • Agent composition significantly affects market microstructure

    ═══════════════════════════════════════════════════════════════
    This completes Week 2: Limit Order Book Simulator
    """

    ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=10,
            verticalalignment="top", fontfamily="monospace")

    return fig


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    print("=" * 60)
    print("WEEK 2 FINAL: MULTI-AGENT SIMULATION")
    print("=" * 60)

    results = {}
    all_figures = []

    # Run Scenario A
    print("\nRunning Scenario A: 100 NoiseAgents...")
    agents_a = create_agents_scenario_a(SEED)
    tape_a, snap_a, metrics_a = run_scenario("Scenario A", agents_a, SEED)
    results["A"] = {"tape": tape_a, "snapshots": snap_a, "metrics": metrics_a}
    avg_spread_a = f"{metrics_a['avg_spread']:.4f}" if metrics_a['avg_spread'] else 'N/A'
    print(f"  Trades: {metrics_a['total_trades']}, Avg Spread: {avg_spread_a}")

    # Run Scenario B
    print("\nRunning Scenario B: 80 NoiseAgents + 20 MarketMakerAgents...")
    agents_b = create_agents_scenario_b(SEED)
    tape_b, snap_b, metrics_b = run_scenario("Scenario B", agents_b, SEED)
    results["B"] = {"tape": tape_b, "snapshots": snap_b, "metrics": metrics_b}
    avg_spread_b = f"{metrics_b['avg_spread']:.4f}" if metrics_b['avg_spread'] else 'N/A'
    print(f"  Trades: {metrics_b['total_trades']}, Avg Spread: {avg_spread_b}")

    # Run Scenario C
    print("\nRunning Scenario C: 80 NoiseAgents + 20 MomentumAgents...")
    agents_c = create_agents_scenario_c(SEED)
    tape_c, snap_c, metrics_c = run_scenario("Scenario C", agents_c, SEED)
    results["C"] = {"tape": tape_c, "snapshots": snap_c, "metrics": metrics_c}
    avg_spread_c = f"{metrics_c['avg_spread']:.4f}" if metrics_c['avg_spread'] else 'N/A'
    print(f"  Trades: {metrics_c['total_trades']}, Avg Spread: {avg_spread_c}")

    # Determinism check
    print("\nVerifying determinism (re-running Scenario A)...")
    agents_a2 = create_agents_scenario_a(SEED)
    tape_a2, snap_a2, metrics_a2 = run_scenario("Scenario A (verify)", agents_a2, SEED)
    assert metrics_a["total_trades"] == metrics_a2["total_trades"], "Determinism check failed"
    print("  Determinism verified!")

    # Generate PDF report
    print("\nGenerating PDF report...")

    # Page 1: Setup
    all_figures.append(create_setup_page())

    # Pages 2-3: Scenario A plots
    all_figures.extend(generate_scenario_figures(
        results["A"]["tape"], results["A"]["snapshots"], "Scenario A: 100 NoiseAgents"))

    # Pages 4-5: Scenario B plots
    all_figures.extend(generate_scenario_figures(
        results["B"]["tape"], results["B"]["snapshots"], "Scenario B: 80 Noise + 20 MM"))

    # Pages 6-7: Scenario C plots
    all_figures.extend(generate_scenario_figures(
        results["C"]["tape"], results["C"]["snapshots"], "Scenario C: 80 Noise + 20 Mom"))

    # Page 8: Comparison table
    all_figures.append(create_comparison_table(results))

    # Page 9: Interpretation
    all_figures.append(create_interpretation_page())

    # Export PDF
    pdf_path = os.path.join(SCRIPT_DIR, "simulation_report.pdf")
    export_pdf(all_figures, pdf_path)

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print(f"PDF report saved: {pdf_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
