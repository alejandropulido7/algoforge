import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """Custom Gymnasium trading environment for RL agents."""
    
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

        # Feature matrix shape
        n_features = 5 + len(self.indicators)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(window_size, n_features),
            dtype=np.float32
        )

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
        
        # Columns
        c_names = [c for c in ['Open', 'High', 'Low', 'Close', 'Volume'] if c in self.df.columns]
        if len(c_names) < 5:
            ohlcv = self.df.iloc[start:end, :5].values
        else:
            ohlcv = self.df.iloc[start:end][c_names].values

        # Normalize OHLCV
        mean = np.mean(ohlcv, axis=0) + 1e-8
        std = np.std(ohlcv, axis=0) + 1e-8
        ohlcv_norm = (ohlcv - mean) / std

        if self.indicators:
            ind_matrix = np.column_stack([v[start:end] for v in self.indicators.values()])
            ind_mean = np.mean(ind_matrix, axis=0) + 1e-8
            ind_std = np.std(ind_matrix, axis=0) + 1e-8
            ind_norm = (ind_matrix - ind_mean) / ind_std
            obs = np.hstack([ohlcv_norm, ind_norm])
        else:
            obs = ohlcv_norm

        return np.nan_to_num(obs.astype(np.float32))

    def step(self, action: int):
        close_col = 'Close' if 'Close' in self.df.columns else self.df.columns[0]
        current_price = float(self.df.iloc[self.current_step][close_col])
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
