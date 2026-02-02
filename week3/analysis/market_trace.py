"""
Week 3: Market Trace Analysis.

Runs a multi-agent simulation with:
- 1 PPO agent (trained)
- 50 Noise traders
- 10 Market makers

Logs per-step data for analysis.

Usage:
    python week3/analysis/market_trace.py
"""

import os
import sys
import csv

import numpy as np

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stable_baselines3 import PPO

from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook
from week2.orderbook.matching_engine import MatchingEngine
from week2.agents.noise_agent import NoiseAgent
from week2.agents.market_maker_agent import MarketMakerAgent
from week3.env.trading_env import TradingEnv


# Configuration
TOTAL_STEPS = 5000
NUM_NOISE_TRADERS = 50
NUM_MARKET_MAKERS = 10
SEED = 42


def create_seeded_orderbook():
    """Create an orderbook with initial liquidity."""
    orderbook = HeapOrderBook()

    # Seed with initial orders (50 bid levels, 50 ask levels)
    for i in range(50):
        bid_price = round(99.0 - i * 0.1, 2)
        ask_price = round(101.0 + i * 0.1, 2)
        orderbook.add_order(Order(
            order_id=i,
            side="BUY",
            price=bid_price,
            quantity=10,
            timestamp=0.0,
        ))
        orderbook.add_order(Order(
            order_id=1000 + i,
            side="SELL",
            price=ask_price,
            quantity=10,
            timestamp=0.0,
        ))

    return orderbook


def create_agents(seed: int):
    """Create noise traders and market makers."""
    agents = []

    # 50 Noise traders
    for i in range(NUM_NOISE_TRADERS):
        agents.append(NoiseAgent(
            agent_id=100 + i,
            cash=10000.0,
            inventory=50,
            initial_fair_value=100.0,
            volatility=0.1,
            seed=seed + i,
        ))

    # 10 Market makers
    for i in range(NUM_MARKET_MAKERS):
        agents.append(MarketMakerAgent(
            agent_id=200 + i,
            cash=10000.0,
            inventory=50,
            base_spread=2.0,
            inventory_skew_factor=0.1,
            quantity=5,
        ))

    return agents


def get_market_snapshot(orderbook):
    """Get current market state."""
    best_bid = orderbook.best_bid()
    best_ask = orderbook.best_ask()

    if best_bid is not None and best_ask is not None:
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
    elif best_bid is not None:
        mid_price = best_bid
        spread = None
    elif best_ask is not None:
        mid_price = best_ask
        spread = None
    else:
        mid_price = 100.0
        spread = None

    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid_price": mid_price,
        "spread": spread,
    }


def main():
    print("=" * 60)
    print("WEEK 3: MARKET TRACE ANALYSIS")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Steps: {TOTAL_STEPS}")
    print(f"  PPO Agents: 1")
    print(f"  Noise Traders: {NUM_NOISE_TRADERS}")
    print(f"  Market Makers: {NUM_MARKET_MAKERS}")
    print(f"  Seed: {SEED}")

    # Set seeds
    np.random.seed(SEED)

    # Create orderbook and engine
    print("\nInitializing market...")
    orderbook = create_seeded_orderbook()
    engine = MatchingEngine(orderbook)

    # Create background agents
    print("Creating agents...")
    background_agents = create_agents(SEED)

    # Load PPO agent
    print("Loading PPO model...")
    model_path = os.path.join(PROJECT_ROOT, "week3/training/ppo_trading_agent.zip")
    if os.path.exists(model_path):
        ppo_model = PPO.load(model_path)
        print(f"  Loaded: {model_path}")
    else:
        print(f"  WARNING: Model not found at {model_path}")
        print("  Using untrained PPO model")
        # Create a dummy environment for the model
        dummy_env = TradingEnv(engine, max_steps=TOTAL_STEPS)
        ppo_model = PPO("MlpPolicy", dummy_env, verbose=0)

    # Create environment for PPO agent
    env = TradingEnv(engine, max_steps=TOTAL_STEPS)
    obs, _ = env.reset(seed=SEED)

    # Prepare logging
    log_path = os.path.join(SCRIPT_DIR, "market_trace.csv")
    log_data = []

    order_id_counter = 5000

    print("\nRunning simulation...")
    print("-" * 60)

    last_trade_price = None

    for step in range(TOTAL_STEPS):
        timestamp = float(step)

        # Get market snapshot
        snapshot = get_market_snapshot(orderbook)

        # === PPO Agent Action ===
        ppo_action, _ = ppo_model.predict(obs, deterministic=True)
        ppo_action = int(ppo_action)

        # Log PPO action (before execution)
        log_entry = {
            "timestamp": timestamp,
            "mid_price": snapshot["mid_price"],
            "spread": snapshot["spread"],
            "trade_price": last_trade_price,
            "agent_id": "PPO",
            "action": ["HOLD", "BUY", "SELL"][ppo_action],
        }
        log_data.append(log_entry)

        # Execute PPO action (simplified - just track inventory/cash changes)
        if ppo_action == 1 and snapshot["best_ask"] is not None:
            # BUY at best ask
            order = Order(
                order_id=order_id_counter,
                side="BUY",
                price=snapshot["best_ask"],
                quantity=1,
                timestamp=timestamp,
            )
            order_id_counter += 1
            trades_before = len(engine.trades)
            engine.process_order(order)
            if len(engine.trades) > trades_before:
                last_trade_price = engine.trades[-1].price
                env.inventory += 1
                env.cash -= last_trade_price

        elif ppo_action == 2 and snapshot["best_bid"] is not None:
            # SELL at best bid
            order = Order(
                order_id=order_id_counter,
                side="SELL",
                price=snapshot["best_bid"],
                quantity=1,
                timestamp=timestamp,
            )
            order_id_counter += 1
            trades_before = len(engine.trades)
            engine.process_order(order)
            if len(engine.trades) > trades_before:
                last_trade_price = engine.trades[-1].price
                env.inventory -= 1
                env.cash += last_trade_price

        # === Background Agent Actions ===
        for agent in background_agents:
            # Build snapshot for agent
            agent_snapshot = {
                "best_bid": snapshot["best_bid"],
                "best_ask": snapshot["best_ask"],
                "mid_price": snapshot["mid_price"],
                "spread": snapshot["spread"],
                "timestamp": timestamp,
            }

            # Get agent action(s)
            action_result = agent.get_action(agent_snapshot)

            # Handle single action or list of actions
            if isinstance(action_result, dict):
                actions = [action_result]
            else:
                actions = action_result

            for action in actions:
                if action["type"] == "NONE" or action["quantity"] == 0:
                    continue

                if action["price"] is None or action["price"] <= 0:
                    continue

                # Create and process order
                order = Order(
                    order_id=order_id_counter,
                    side=action["side"],
                    price=action["price"],
                    quantity=action["quantity"],
                    timestamp=timestamp,
                )
                order_id_counter += 1

                trades_before = len(engine.trades)
                engine.process_order(order)

                # Track trade if occurred
                if len(engine.trades) > trades_before:
                    last_trade_price = engine.trades[-1].price

                    # Log trade
                    trade_snapshot = get_market_snapshot(orderbook)
                    log_entry = {
                        "timestamp": timestamp,
                        "mid_price": trade_snapshot["mid_price"],
                        "spread": trade_snapshot["spread"],
                        "trade_price": last_trade_price,
                        "agent_id": agent.agent_id,
                        "action": action["side"],
                    }
                    log_data.append(log_entry)

        # Update PPO observation for next step
        obs = env._get_observation()

        # Progress update
        if (step + 1) % 1000 == 0:
            spread_str = f"{snapshot['spread']:.2f}" if snapshot['spread'] else 'N/A'
            print(f"  Step {step + 1}/{TOTAL_STEPS}: "
                  f"mid={snapshot['mid_price']:.2f}, "
                  f"spread={spread_str}, "
                  f"trades={len(engine.trades)}")

    print("-" * 60)

    # Save log to CSV
    print(f"\nSaving trace to: {log_path}")
    with open(log_path, "w", newline="") as f:
        fieldnames = ["timestamp", "mid_price", "spread", "trade_price", "agent_id", "action"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_data)

    # Summary statistics
    print("\n--- Simulation Summary ---")
    print(f"Total steps: {TOTAL_STEPS}")
    print(f"Total trades: {len(engine.trades)}")
    print(f"Log entries: {len(log_data)}")

    # Count actions by agent type
    ppo_actions = [e for e in log_data if e["agent_id"] == "PPO"]
    noise_actions = [e for e in log_data if isinstance(e["agent_id"], int) and 100 <= e["agent_id"] < 200]
    mm_actions = [e for e in log_data if isinstance(e["agent_id"], int) and 200 <= e["agent_id"] < 300]

    print(f"\nPPO Agent: {len(ppo_actions)} actions")
    ppo_buys = sum(1 for e in ppo_actions if e["action"] == "BUY")
    ppo_sells = sum(1 for e in ppo_actions if e["action"] == "SELL")
    ppo_holds = sum(1 for e in ppo_actions if e["action"] == "HOLD")
    print(f"  HOLD: {ppo_holds}, BUY: {ppo_buys}, SELL: {ppo_sells}")

    print(f"\nNoise Traders: {len(noise_actions)} trades")
    print(f"Market Makers: {len(mm_actions)} trades")

    final_snapshot = get_market_snapshot(orderbook)
    final_spread_str = f"{final_snapshot['spread']:.2f}" if final_snapshot['spread'] else 'N/A'
    print(f"\nFinal market state:")
    print(f"  Mid-price: {final_snapshot['mid_price']:.2f}")
    print(f"  Spread: {final_spread_str}")

    print("\n" + "=" * 60)
    print("TRACE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
