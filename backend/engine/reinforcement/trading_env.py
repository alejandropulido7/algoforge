import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """Ultra-fast vectorized Gymnasium trading environment for RL agents."""
    
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        df: pd.DataFrame,
        indicators: dict[str, np.ndarray] | None = None,
        initial_balance: float = 10000.0,
        commission: float = 0.001,
        window_size: int = 20,
        reward_type: str = "sharpe"
    ):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.indicators = indicators or {}
        self.initial_balance = initial_balance
        self.commission = commission
        self.window_size = window_size
        self.reward_type = reward_type

        # 0: Hold/Flat, 1: Buy/Long, 2: Sell/Short
        self.action_space = spaces.Discrete(3)

        # Precompute & vectorize normalized feature matrix once in memory for 100x speed
        c_names = [c for c in ['Open', 'High', 'Low', 'Close', 'Volume'] if c in self.df.columns]
        if len(c_names) < 5:
            ohlcv = self.df.iloc[:, :5].values.astype(np.float32)
        else:
            ohlcv = self.df[c_names].values.astype(np.float32)

        ohlcv_mean = np.mean(ohlcv, axis=0, keepdims=True) + 1e-8
        ohlcv_std = np.std(ohlcv, axis=0, keepdims=True) + 1e-8
        ohlcv_norm = (ohlcv - ohlcv_mean) / ohlcv_std

        if self.indicators:
            ind_matrix = np.column_stack([np.asarray(v, dtype=np.float32) for v in self.indicators.values()])
            ind_mean = np.mean(ind_matrix, axis=0, keepdims=True) + 1e-8
            ind_std = np.std(ind_matrix, axis=0, keepdims=True) + 1e-8
            ind_norm = (ind_matrix - ind_mean) / ind_std
            full_matrix = np.hstack([ohlcv_norm, ind_norm])
        else:
            full_matrix = ohlcv_norm

        self.feature_matrix = np.nan_to_num(full_matrix.astype(np.float32))
        n_features = self.feature_matrix.shape[1]

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(window_size, n_features),
            dtype=np.float32
        )

        close_col = 'Close' if 'Close' in self.df.columns else self.df.columns[0]
        self.close_prices = self.df[close_col].values.astype(np.float64)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.position = 0  # 0: flat, 1: long, -1: short
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = [self.initial_balance]
        return self._get_observation(), {}

    def _get_observation(self) -> np.ndarray:
        start = self.current_step - self.window_size
        end = self.current_step
        return self.feature_matrix[start:end]

    def step(self, action: int):
        current_price = self.close_prices[self.current_step]
        prev_balance = self.balance

        # Action logic
        if action == 1 and self.position == 0:  # Enter Long
            self.position = 1
            self.entry_price = current_price
            self.balance *= (1.0 - self.commission)
        elif action == 2 and self.position == 1:  # Close Long
            pnl_pct = (current_price - self.entry_price) / (self.entry_price + 1e-8)
            self.balance *= (1.0 + pnl_pct - self.commission)
            self.trades.append(pnl_pct)
            self.position = 0
        elif action == 2 and self.position == 0:  # Enter Short
            self.position = -1
            self.entry_price = current_price
            self.balance *= (1.0 - self.commission)
        elif action == 1 and self.position == -1:  # Close Short
            pnl_pct = (self.entry_price - current_price) / (self.entry_price + 1e-8)
            self.balance *= (1.0 + pnl_pct - self.commission)
            self.trades.append(pnl_pct)
            self.position = 0

        self.equity_curve.append(self.balance)
        self.current_step += 1

        # Reward computation
        step_return = (self.balance - prev_balance) / (prev_balance + 1e-8)
        reward = step_return

        terminated = self.current_step >= len(self.df) - 1
        truncated = self.balance <= self.initial_balance * 0.1

        return self._get_observation(), float(reward), terminated, truncated, {
            "balance": self.balance,
            "n_trades": len(self.trades)
        }
