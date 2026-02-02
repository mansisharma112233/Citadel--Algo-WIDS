"""
Week 3: PPO Training Script.

Trains a PPO agent on the TradingEnv using Stable-Baselines3.
Logs metrics to CSV for analysis.

Usage:
    python week3/training/train_ppo.py
"""

import os
import sys
import csv
from collections import defaultdict

import numpy as np

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

from week3.env.trading_env import TradingEnv


class TrainingLogger(BaseCallback):
    """
    Custom callback for logging training metrics to CSV.

    Logs:
    - Mean episode reward
    - Entropy loss
    - Action counts (HOLD, BUY, SELL)
    """

    def __init__(self, log_path: str, verbose: int = 0):
        super().__init__(verbose)
        self.log_path = log_path
        self.log_data = []
        self.action_counts = defaultdict(int)
        self.episode_rewards = []
        self.current_episode_reward = 0.0

    def _on_step(self) -> bool:
        # Track actions
        actions = self.locals.get("actions", [])
        for action in actions:
            self.action_counts[int(action)] += 1

        # Track rewards
        rewards = self.locals.get("rewards", [])
        for reward in rewards:
            self.current_episode_reward += reward

        # Check for episode end
        dones = self.locals.get("dones", [])
        for done in dones:
            if done:
                self.episode_rewards.append(self.current_episode_reward)
                self.current_episode_reward = 0.0

        return True

    def _on_rollout_end(self) -> None:
        """Log metrics at end of each rollout."""
        # Get entropy from logger if available
        entropy = None
        if hasattr(self.model, "logger") and self.model.logger is not None:
            # Try to get entropy from the training info
            pass  # Entropy will be captured from locals in _on_training_end

        # Compute mean episode reward
        if self.episode_rewards:
            mean_reward = np.mean(self.episode_rewards[-10:])  # Last 10 episodes
        else:
            mean_reward = 0.0

        # Log entry
        log_entry = {
            "timestep": self.num_timesteps,
            "mean_episode_reward": mean_reward,
            "entropy": entropy,
            "action_hold": self.action_counts[0],
            "action_buy": self.action_counts[1],
            "action_sell": self.action_counts[2],
        }
        self.log_data.append(log_entry)

        if self.verbose > 0:
            print(f"  [Log] Step {self.num_timesteps}: reward={mean_reward:.4f}, "
                  f"actions=[H:{self.action_counts[0]}, B:{self.action_counts[1]}, S:{self.action_counts[2]}]")

    def _on_training_end(self) -> None:
        """Save logs to CSV at end of training."""
        # Try to get final entropy from model's logger
        try:
            if hasattr(self.model, "logger") and self.model.logger is not None:
                name_to_value = getattr(self.model.logger, "name_to_value", {})
                entropy = name_to_value.get("train/entropy_loss", None)
                if entropy is not None and self.log_data:
                    # Update last entries with entropy
                    for entry in self.log_data:
                        if entry["entropy"] is None:
                            entry["entropy"] = entropy
        except Exception:
            pass

        # Write to CSV
        if self.log_data:
            with open(self.log_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.log_data[0].keys())
                writer.writeheader()
                writer.writerows(self.log_data)
            print(f"\nTraining log saved to: {self.log_path}")

        # Print summary
        print("\n--- Training Summary ---")
        print(f"Total timesteps: {self.num_timesteps}")
        print(f"Total episodes: {len(self.episode_rewards)}")
        if self.episode_rewards:
            print(f"Mean episode reward: {np.mean(self.episode_rewards):.4f}")
        print(f"Action distribution: HOLD={self.action_counts[0]}, "
              f"BUY={self.action_counts[1]}, SELL={self.action_counts[2]}")


def main():
    print("=" * 60)
    print("WEEK 3: PPO TRAINING (50,000 timesteps) - REAL MARKET")
    print("=" * 60)

    # Create environment with REAL market (self-contained)
    print("\nInitializing environment with REAL market...")
    env = TradingEnv(max_steps=2000, initial_cash=10000.0, seed=42)

    # Initialize PPO model
    print("Initializing PPO model...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
    )

    # Setup logging callback
    log_path = os.path.join(SCRIPT_DIR, "training_log.csv")
    logger_callback = TrainingLogger(log_path=log_path, verbose=1)

    # Train the model
    print("\nStarting training (50,000 timesteps)...")
    print("-" * 60)
    model.learn(total_timesteps=50000, callback=logger_callback)
    print("-" * 60)

    # Save the model
    model_path = os.path.join(SCRIPT_DIR, "ppo_trading_agent")
    model.save(model_path)
    print(f"\nModel saved to: {model_path}.zip")

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
