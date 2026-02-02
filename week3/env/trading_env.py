"""
Gymnasium-compatible Trading Environment.

CONNECTED to the real Week 2 market engine components:
- MatchingEngine for order execution
- TradeTape for trade logging
- L1Snapshots for market data

Actions:
    0 = HOLD (do nothing)
    1 = BUY 1 unit (market order)
    2 = SELL 1 unit (market order)

Observation (length 10, all normalized 0-1):
    [best_bid, best_ask, spread, mid_price,
     bid_volume, ask_volume,
     inventory, cash,
     last_trade_price, volatility_estimate]
"""

import os
import sys
import random
import itertools

import gymnasium as gym
from gymnasium import spaces
import numpy as np

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import REAL Week 2 components
from week2.orderbook.order import Order
from week2.orderbook.orderbook_heap import HeapOrderBook
from week2.orderbook.matching_engine import MatchingEngine
from week2.analytics.tape import TradeTape
from week2.analytics.snapshots import L1Snapshots


# RL Agent order ID prefix (to identify agent's trades)
RL_AGENT_ORDER_ID_START = 900000


class TradingEnv(gym.Env):
    """
    Trading environment compatible with Gymnasium API.

    CONNECTED to real Week 2 orderbook/matching engine.
    All price movement comes from actual order flow.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, max_steps: int = 2000, initial_cash: float = 10000.0,
                 initial_inventory: int = 0, seed: int = None):
        """
        Initialize the trading environment with REAL market components.

        Args:
            max_steps: Maximum steps before truncation
            initial_cash: Starting cash for the agent
            initial_inventory: Starting inventory for the agent
            seed: Random seed for reproducibility
        """
        super().__init__()

        # Configuration
        self.max_steps = max_steps
        self.initial_cash = initial_cash
        self.initial_inventory = initial_inventory
        self._seed = seed

        # These will be initialized in reset()
        self.orderbook = None
        self.engine = None
        self.tape = None
        self.snapshots = None
        self.order_id_counter = None

        # Episode state
        self.current_step = 0
        self.current_timestamp = 0.0

        # Agent state
        self.inventory = initial_inventory
        self.cash = initial_cash

        # History tracking for observations
        self.mid_price_history = []
        self.last_trade_price = None
        self.volatility_lookback = 50

        # Reward engineering attributes
        self.portfolio_values = []
        self.peak_value = 0.0
        self.lambda_risk = 0.1

        # Action space: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)

        # Observation space: 10-dimensional normalized vector
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(10,),
            dtype=np.float32,
        )

    def _create_fresh_market(self):
        """Create fresh market components (orderbook, engine, tape, snapshots)."""
        # Create new orderbook
        self.orderbook = HeapOrderBook()

        # Create matching engine
        self.engine = MatchingEngine(self.orderbook)

        # Create trade tape
        self.tape = TradeTape()

        # Create snapshot recorder
        self.snapshots = L1Snapshots()

        # Reset order ID counter for RL agent
        self.order_id_counter = itertools.count(RL_AGENT_ORDER_ID_START)

    def _seed_orderbook(self):
        """
        Pre-seed the orderbook with 50 limit orders on both sides.
        This ensures the book is NOT empty at start.
        """
        # Use numpy random for seeding if seed is set
        if self._seed is not None:
            np.random.seed(self._seed + self.current_step)
            random.seed(self._seed + self.current_step)

        base_price = 100.0

        # Add 50 BUY orders (bids) at decreasing prices
        for i in range(50):
            price = round(base_price - 0.5 - i * 0.1 + np.random.uniform(-0.05, 0.05), 2)
            quantity = np.random.randint(5, 20)
            order = Order(
                order_id=i,
                side="BUY",
                price=price,
                quantity=quantity,
                timestamp=0.0,
            )
            self.orderbook.add_order(order)

        # Add 50 SELL orders (asks) at increasing prices
        for i in range(50):
            price = round(base_price + 0.5 + i * 0.1 + np.random.uniform(-0.05, 0.05), 2)
            quantity = np.random.randint(5, 20)
            order = Order(
                order_id=1000 + i,
                side="SELL",
                price=price,
                quantity=quantity,
                timestamp=0.0,
            )
            self.orderbook.add_order(order)

    def reset(self, seed=None, options=None):
        """
        Reset the environment to initial state with fresh market.

        Args:
            seed: Random seed for reproducibility
            options: Additional options (unused)

        Returns:
            observation: Initial observation from real market state
            info: Empty info dict
        """
        # Call parent reset for seeding
        super().reset(seed=seed)

        # Update seed if provided
        if seed is not None:
            self._seed = seed

        # Reset step counter
        self.current_step = 0
        self.current_timestamp = 0.0

        # Reset agent state
        self.inventory = self.initial_inventory
        self.cash = self.initial_cash

        # Reset history tracking
        self.mid_price_history = []
        self.last_trade_price = None

        # Reset reward tracking
        self.portfolio_values = []
        self.peak_value = self.initial_cash  # Start peak at initial cash

        # Create fresh market components
        self._create_fresh_market()

        # Pre-seed orderbook with liquidity
        self._seed_orderbook()

        # Record initial snapshot
        self.snapshots.record(self.current_timestamp, self.orderbook)

        # Build initial observation from REAL market state
        observation = self._get_observation()
        info = {
            "initial_cash": self.cash,
            "initial_inventory": self.inventory,
        }

        return observation, info

    def step(self, action: int):
        """
        Execute one step in the environment with REAL order execution.

        Args:
            action: 0=HOLD, 1=BUY, 2=SELL

        Returns:
            observation: Current state observation from real market
            reward: Reward for this step
            terminated: Whether episode ended naturally
            truncated: Whether episode was cut short (max_steps)
            info: Additional information including trade details
        """
        # Advance timestamp
        self.current_timestamp = float(self.current_step)

        # Track trades before action
        trades_before = len(self.engine.trades)

        # 1. Execute action via REAL matching engine
        trade_executed = self._execute_action(action)

        # 2. Record any new trades to tape
        new_trades = self.engine.trades[trades_before:]
        if new_trades:
            self.tape.record_trades(new_trades, self.current_timestamp)
            # Update last trade price
            self.last_trade_price = new_trades[-1].price

        # 3. Record L1 snapshot
        self.snapshots.record(self.current_timestamp, self.orderbook)

        # 4. Get market snapshot for portfolio calculation
        snapshot = self._get_snapshot()

        # 5. Compute portfolio value and reward
        mid_price = snapshot["mid_price"] if snapshot["mid_price"] is not None else 100.0
        portfolio_value = self.cash + self.inventory * mid_price
        reward, drawdown = self._calculate_reward(portfolio_value)

        # 6. Build observation from REAL market state
        observation = self._get_observation()

        # 7. Increment step counter
        self.current_step += 1

        # 8. Check termination conditions
        terminated = False
        truncated = self.current_step >= self.max_steps

        # 9. Build info dict with trade details
        info = {
            "portfolio_value": portfolio_value,
            "drawdown": drawdown,
            "inventory": self.inventory,
            "cash": self.cash,
            "mid_price": mid_price,
            "spread": snapshot["spread"],
            "trade_executed": trade_executed,
            "action": ["HOLD", "BUY", "SELL"][action],
        }

        return observation, reward, terminated, truncated, info

    def _execute_action(self, action: int) -> bool:
        """
        Execute the given action on the REAL market.

        Args:
            action: 0=HOLD, 1=BUY, 2=SELL

        Returns:
            True if a trade was executed, False otherwise
        """
        if action == 0:
            # HOLD - do nothing
            return False

        elif action == 1:
            # BUY 1 unit at market (aggressive buy crosses the spread)
            best_ask = self.orderbook.best_ask()
            if best_ask is None:
                return False  # No liquidity

            # Submit MARKET BUY order (price=None means market order)
            order_id = next(self.order_id_counter)
            order = Order(
                order_id=order_id,
                side="BUY",
                price=None,  # Market order - will match at best ask
                quantity=1,
                timestamp=self.current_timestamp,
            )

            trades_before = len(self.engine.trades)
            self.engine.process_order(order)

            # Check if trade occurred
            if len(self.engine.trades) > trades_before:
                trade = self.engine.trades[-1]
                # Update agent state
                self.inventory += trade.quantity
                self.cash -= trade.price * trade.quantity
                return True

            return False

        elif action == 2:
            # SELL 1 unit at market (aggressive sell crosses the spread)
            best_bid = self.orderbook.best_bid()
            if best_bid is None:
                return False  # No liquidity

            # Submit MARKET SELL order (price=None means market order)
            order_id = next(self.order_id_counter)
            order = Order(
                order_id=order_id,
                side="SELL",
                price=None,  # Market order - will match at best bid
                quantity=1,
                timestamp=self.current_timestamp,
            )

            trades_before = len(self.engine.trades)
            self.engine.process_order(order)

            # Check if trade occurred
            if len(self.engine.trades) > trades_before:
                trade = self.engine.trades[-1]
                # Update agent state
                self.inventory -= trade.quantity
                self.cash += trade.price * trade.quantity
                return True

            return False

        return False

    def _calculate_reward(self, new_value: float) -> tuple:
        """
        Calculate reward based on portfolio value change, drawdown, and inventory.

        Reward formula:
            reward = (V_t - V_{t-1}) - lambda_risk * drawdown - 0.01 * |inventory|

        Args:
            new_value: Current portfolio value V_t

        Returns:
            Tuple of (reward, drawdown)
        """
        # Get previous portfolio value
        if len(self.portfolio_values) > 0:
            prev_value = self.portfolio_values[-1]
        else:
            prev_value = new_value  # No change on first step

        # Update peak value for drawdown calculation
        self.peak_value = max(self.peak_value, new_value)

        # Calculate drawdown (only positive values count)
        drawdown = max(0.0, self.peak_value - new_value)

        # Calculate reward components
        pnl_change = new_value - prev_value  # P&L change
        risk_penalty = self.lambda_risk * drawdown  # Drawdown penalty
        inventory_penalty = 0.01 * abs(self.inventory)  # Inventory penalty

        # Total reward
        reward = pnl_change - risk_penalty - inventory_penalty

        # Store current portfolio value
        self.portfolio_values.append(new_value)

        return reward, drawdown

    def _get_snapshot(self) -> dict:
        """
        Get current REAL market snapshot.

        Returns:
            Dictionary with market state from real orderbook
        """
        best_bid = self.orderbook.best_bid()
        best_ask = self.orderbook.best_ask()

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
            mid_price = None
            spread = None

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid_price": mid_price,
            "spread": spread,
            "inventory": self.inventory,
            "cash": self.cash,
        }

    def _get_observation(self) -> np.ndarray:
        """
        Build normalized observation vector from REAL market state.

        Observation vector (length 10):
            [best_bid, best_ask, spread, mid_price,
             bid_volume, ask_volume,
             inventory, cash,
             last_trade_price, volatility_estimate]

        All values normalized to [0, 1].

        Returns:
            np.ndarray of shape (10,) with dtype float32
        """
        # Get REAL market data from orderbook
        best_bid = self.orderbook.best_bid()
        best_ask = self.orderbook.best_ask()

        # Compute mid-price (use 100.0 as default if no quotes)
        if best_bid is not None and best_ask is not None:
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
        elif best_bid is not None:
            mid_price = best_bid
            spread = 0.0
        elif best_ask is not None:
            mid_price = best_ask
            spread = 0.0
        else:
            mid_price = 100.0  # Default
            spread = 0.0

        # Update mid-price history for volatility
        self.mid_price_history.append(mid_price)
        if len(self.mid_price_history) > self.volatility_lookback:
            self.mid_price_history = self.mid_price_history[-self.volatility_lookback:]

        # Get REAL volumes at best bid/ask
        bid_volume = self._get_volume_at_price("BUY", best_bid) if best_bid else 0
        ask_volume = self._get_volume_at_price("SELL", best_ask) if best_ask else 0

        # Get last trade price (default to mid-price)
        last_trade = self.last_trade_price if self.last_trade_price is not None else mid_price

        # Compute volatility from rolling std of mid-prices
        if len(self.mid_price_history) >= 2:
            volatility = np.std(self.mid_price_history)
        else:
            volatility = 0.0

        # === NORMALIZATION ===
        # Prices: normalize by mid-price (result around 1.0, clip to [0, 2] then /2)
        norm_best_bid = self._normalize_price(best_bid, mid_price)
        norm_best_ask = self._normalize_price(best_ask, mid_price)
        norm_mid_price = 0.5  # mid/mid = 1.0, scaled to 0.5
        norm_spread = np.clip(spread / mid_price, 0.0, 1.0) if mid_price > 0 else 0.0
        norm_last_trade = self._normalize_price(last_trade, mid_price)

        # Volumes: log scaling, log(1+vol) / 10
        norm_bid_volume = np.clip(np.log1p(bid_volume) / 10.0, 0.0, 1.0)
        norm_ask_volume = np.clip(np.log1p(ask_volume) / 10.0, 0.0, 1.0)

        # Inventory: divide by 100, clip to [-1, 1], then shift to [0, 1]
        norm_inventory = np.clip(self.inventory / 100.0, -1.0, 1.0)
        norm_inventory = (norm_inventory + 1.0) / 2.0  # Shift to [0, 1]

        # Cash: divide by 10000, clip to [-1, 1], then shift to [0, 1]
        norm_cash = np.clip(self.cash / 10000.0, -1.0, 1.0)
        norm_cash = (norm_cash + 1.0) / 2.0  # Shift to [0, 1]

        # Volatility: scale by dividing by mid_price, then clip
        norm_volatility = np.clip(volatility / (mid_price * 0.1), 0.0, 1.0) if mid_price > 0 else 0.0

        # Build observation vector
        obs = np.array([
            norm_best_bid,
            norm_best_ask,
            norm_spread,
            norm_mid_price,
            norm_bid_volume,
            norm_ask_volume,
            norm_inventory,
            norm_cash,
            norm_last_trade,
            norm_volatility,
        ], dtype=np.float32)

        # Final safety: replace any NaN with 0, clip to [0, 1]
        obs = np.nan_to_num(obs, nan=0.0, posinf=1.0, neginf=0.0)
        obs = np.clip(obs, 0.0, 1.0)

        return obs

    def _normalize_price(self, price, mid_price: float) -> float:
        """
        Normalize price relative to mid-price.

        Args:
            price: Raw price (can be None)
            mid_price: Current mid-price for normalization

        Returns:
            Normalized price in [0, 1]
        """
        if price is None or mid_price <= 0:
            return 0.5  # Default to mid
        # price/mid gives ~1.0, divide by 2 to center at 0.5
        normalized = price / mid_price / 2.0
        return float(np.clip(normalized, 0.0, 1.0))

    def _get_volume_at_price(self, side: str, price) -> int:
        """
        Get total volume at a specific price level from REAL orderbook.

        Args:
            side: "BUY" or "SELL"
            price: Price level

        Returns:
            Total quantity at that price level
        """
        if price is None:
            return 0

        if side == "BUY" and price in self.orderbook.bids:
            return sum(order.quantity for order in self.orderbook.bids[price])
        elif side == "SELL" and price in self.orderbook.asks:
            return sum(order.quantity for order in self.orderbook.asks[price])
        return 0

    def render(self):
        """Render the environment state."""
        snapshot = self._get_snapshot()
        spread_str = f"{snapshot['spread']:.2f}" if snapshot['spread'] else 'N/A'
        mid_str = f"{snapshot['mid_price']:.2f}" if snapshot['mid_price'] else 'N/A'
        print(f"Step {self.current_step}: "
              f"Mid={mid_str}, Spread={spread_str}, "
              f"Inv={self.inventory}, Cash={self.cash:.2f}")

    def get_tape_dataframe(self):
        """Get trade tape as DataFrame."""
        return self.tape.to_dataframe()

    def get_snapshots_dataframe(self):
        """Get snapshots as DataFrame."""
        return self.snapshots.to_dataframe()


# Quick test when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING REAL MARKET CONNECTED TradingEnv")
    print("=" * 60)

    # Create environment (no external engine needed - creates its own)
    env = TradingEnv(max_steps=100, initial_cash=10000.0, seed=42)

    # Test reset
    obs, info = env.reset(seed=42)
    print(f"\nReset: obs shape = {obs.shape}")
    print(f"  Initial cash: {info['initial_cash']}")
    print(f"  Initial inventory: {info['initial_inventory']}")
    print(f"  obs = {obs}")

    # Validate observation
    assert obs.shape == (10,), "Observation shape mismatch"
    assert obs.dtype == np.float32, "Observation dtype mismatch"
    assert not np.any(np.isnan(obs)), "Observation contains NaN"
    assert np.all(obs >= 0) and np.all(obs <= 1), "Observation out of [0, 1] range"

    # Test a few steps with real execution
    print("\nRunning 20 steps with real order execution...")
    total_reward = 0.0
    trades_executed = 0

    for i in range(20):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        total_reward += reward
        if info["trade_executed"]:
            trades_executed += 1

        if (i + 1) % 5 == 0:
            print(f"  Step {i+1}: action={info['action']}, "
                  f"reward={reward:.4f}, portfolio={info['portfolio_value']:.2f}, "
                  f"inv={info['inventory']}, trade={info['trade_executed']}")

        # Validate observation
        assert obs.shape == (10,), "Observation shape mismatch"
        assert not np.any(np.isnan(obs)), "Observation contains NaN"
        assert np.all(obs >= 0) and np.all(obs <= 1), "Observation out of [0, 1] range"

    print(f"\nSummary:")
    print(f"  Total reward: {total_reward:.4f}")
    print(f"  Trades executed: {trades_executed}")
    print(f"  Final inventory: {env.inventory}")
    print(f"  Final cash: {env.cash:.2f}")
    print(f"  Trades in tape: {len(env.tape.trades)}")
    print(f"  Snapshots recorded: {len(env.snapshots.records)}")

    # Test reward calculation
    print("\nTesting reward calculation...")
    env2 = TradingEnv(max_steps=100, seed=123)
    env2.reset(seed=123)

    # Manually set state to test reward
    env2.inventory = 10
    env2.cash = 1000.0
    env2.portfolio_values = [2000.0]
    env2.peak_value = 2100.0

    # Calculate reward for new value
    new_value = 2050.0
    reward, drawdown = env2._calculate_reward(new_value)

    # Expected: pnl=50, drawdown=50, inv_penalty=0.1
    # reward = 50 - 0.1*50 - 0.01*10 = 50 - 5 - 0.1 = 44.9
    expected_reward = 50.0 - 0.1 * 50.0 - 0.01 * 10
    assert abs(reward - expected_reward) < 0.001, f"Reward mismatch: {reward} != {expected_reward}"
    assert drawdown == 50.0, f"Drawdown mismatch: {drawdown} != 50.0"
    print(f"  Manual test: reward={reward:.4f} (expected {expected_reward:.4f})")

    print("\n" + "=" * 60)
    print("REAL MARKET TradingEnv TEST PASSED")
    print("=" * 60)
