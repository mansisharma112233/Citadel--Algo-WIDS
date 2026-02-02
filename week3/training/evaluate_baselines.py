"""
Generate baseline evaluation logs for comparison with PPO agent.

Baselines:
1. Random Agent - randomly chooses BUY/SELL/HOLD
2. Buy & Hold - buys once and holds

Outputs CSV files with portfolio values over time.
"""

import os
import sys
import csv
import random

import numpy as np

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from week3.env.trading_env import TradingEnv

SEED = 42
NUM_EPISODES = 5
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def evaluate_random_agent(num_episodes: int = NUM_EPISODES):
    """Evaluate a random agent that randomly chooses actions."""
    print("Evaluating Random Agent...")
    
    all_results = []
    
    for episode in range(num_episodes):
        env = TradingEnv(max_steps=2000, initial_cash=10000.0, seed=SEED + episode)
        obs, info = env.reset()
        
        done = False
        step = 0
        
        random.seed(SEED + episode)
        
        while not done:
            # Random action: 0=HOLD, 1=BUY, 2=SELL
            action = random.randint(0, 2)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Log portfolio value
            all_results.append({
                "episode": episode,
                "step": step,
                "portfolio_value": info.get("portfolio_value", 0),
                "cash": info.get("cash", 0),
                "inventory": info.get("inventory", 0),
                "mid_price": info.get("mid_price", 0),
            })
            step += 1
        
        print(f"  Episode {episode + 1}: Final portfolio = {info.get('portfolio_value', 0):.2f}")
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, "random_agent_log.csv")
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "step", "portfolio_value", "cash", "inventory", "mid_price"])
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Saved: {output_path}")
    return all_results


def evaluate_buy_and_hold(num_episodes: int = NUM_EPISODES):
    """Evaluate a buy-and-hold strategy - buy once, then hold forever."""
    print("Evaluating Buy & Hold Agent...")
    
    all_results = []
    
    for episode in range(num_episodes):
        env = TradingEnv(max_steps=2000, initial_cash=10000.0, seed=SEED + episode)
        obs, info = env.reset()
        
        done = False
        step = 0
        bought = False
        
        while not done:
            # Buy once, then hold
            if not bought:
                action = 1  # BUY
                bought = True
            else:
                action = 0  # HOLD
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Log portfolio value
            all_results.append({
                "episode": episode,
                "step": step,
                "portfolio_value": info.get("portfolio_value", 0),
                "cash": info.get("cash", 0),
                "inventory": info.get("inventory", 0),
                "mid_price": info.get("mid_price", 0),
            })
            step += 1
        
        print(f"  Episode {episode + 1}: Final portfolio = {info.get('portfolio_value', 0):.2f}")
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, "buyhold_agent_log.csv")
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "step", "portfolio_value", "cash", "inventory", "mid_price"])
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Saved: {output_path}")
    return all_results


def evaluate_ppo_agent(num_episodes: int = NUM_EPISODES):
    """Evaluate the trained PPO agent."""
    print("Evaluating PPO Agent...")
    
    from stable_baselines3 import PPO
    
    model_path = os.path.join(OUTPUT_DIR, "ppo_trading_agent.zip")
    if not os.path.exists(model_path):
        print(f"ERROR: PPO model not found at {model_path}")
        return []
    
    model = PPO.load(model_path)
    
    all_results = []
    
    for episode in range(num_episodes):
        env = TradingEnv(max_steps=2000, initial_cash=10000.0, seed=SEED + episode)
        obs, info = env.reset()
        
        done = False
        step = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Log portfolio value
            all_results.append({
                "episode": episode,
                "step": step,
                "portfolio_value": info.get("portfolio_value", 0),
                "cash": info.get("cash", 0),
                "inventory": info.get("inventory", 0),
                "mid_price": info.get("mid_price", 0),
                "action": int(action),
            })
            step += 1
        
        print(f"  Episode {episode + 1}: Final portfolio = {info.get('portfolio_value', 0):.2f}")
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, "ppo_agent_log.csv")
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "step", "portfolio_value", "cash", "inventory", "mid_price", "action"])
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Saved: {output_path}")
    return all_results


if __name__ == "__main__":
    print("=" * 60)
    print("BASELINE EVALUATION")
    print("=" * 60)
    
    evaluate_random_agent()
    print()
    evaluate_buy_and_hold()
    print()
    evaluate_ppo_agent()
    
    print("\n" + "=" * 60)
    print("All baseline evaluations complete!")
    print("=" * 60)
