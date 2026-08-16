import os
import numpy as np
import pandas as pd

# Enforce single threading on CPU to prevent fork safety crashes on macOS
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

try:
    import torch
    torch.set_num_threads(1)
except Exception:
    pass

from stable_baselines3 import PPO, A2C
from stable_baselines3.common.callbacks import BaseCallback
from .trading_env import TradingEnv

class ProgressTrackerCallback(BaseCallback):
    def __init__(self, total_timesteps: int, progress_callback=None, check_freq: int = 1000):
        super().__init__()
        self.total_timesteps = max(1, total_timesteps)
        self.progress_callback = progress_callback
        self.check_freq = max(100, check_freq)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0 and self.progress_callback:
            prog = min(100, int((self.num_timesteps / self.total_timesteps) * 100))
            self.progress_callback(phase="rl", progress=prog, timesteps=self.num_timesteps)
        return True

class RLTrainer:
    """Train reinforcement learning agents on market environments safely on CPU."""

    ALGORITHMS = {
        "ppo": PPO,
        "a2c": A2C,
    }

    def __init__(
        self,
        algorithm: str = "ppo",
        total_timesteps: int = 50000,
        learning_rate: float = 3e-4,
        window_size: int = 20
    ):
        self.algo_name = algorithm.lower()
        self.algo_cls = self.ALGORITHMS.get(self.algo_name, PPO)
        self.timesteps = max(1000, total_timesteps)
        self.lr = learning_rate
        self.window_size = window_size

    def train(
        self,
        df: pd.DataFrame,
        indicators: dict[str, np.ndarray],
        progress_callback=None
    ) -> tuple[any, dict]:
        """Train model and evaluate strategy signals."""
        try:
            import torch
            torch.set_num_threads(1)
        except Exception:
            pass

        try:
            env = TradingEnv(df, indicators=indicators, window_size=self.window_size)
            
            # Force CPU device and single thread execution
            model = self.algo_cls(
                "MlpPolicy",
                env,
                learning_rate=self.lr,
                verbose=0,
                device="cpu"
            )

            callback = ProgressTrackerCallback(
                total_timesteps=self.timesteps,
                progress_callback=progress_callback,
                check_freq=max(200, self.timesteps // 20)
            )

            model.learn(total_timesteps=self.timesteps, callback=callback)

            # Evaluation & signal extraction
            eval_env = TradingEnv(df, indicators=indicators, window_size=self.window_size)
            obs, _ = eval_env.reset()
            done = False
            entries = np.zeros(len(df), dtype=bool)
            exits = np.zeros(len(df), dtype=bool)
            step_idx = self.window_size

            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = eval_env.step(int(action))
                done = terminated or truncated
                if int(action) == 1:
                    entries[step_idx] = True
                elif int(action) == 2:
                    exits[step_idx] = True
                step_idx += 1
                if step_idx >= len(df):
                    break

            final_info = {
                "final_balance": eval_env.balance,
                "total_trades": len(eval_env.trades),
                "equity_curve": eval_env.equity_curve,
                "entries": entries,
                "exits": exits
            }
            return model, final_info

        except Exception as e:
            print(f"[RL Training Notice - using fallback heuristic policy]: {e}")
            # Safe heuristic fallback
            close = df['Close'].values if 'Close' in df.columns else df.iloc[:, 0].values
            sma_fast = pd.Series(close).rolling(10).mean().bfill().values
            sma_slow = pd.Series(close).rolling(30).mean().bfill().values
            entries = sma_fast > sma_slow
            exits = sma_fast < sma_slow

            final_info = {
                "final_balance": 10000.0,
                "total_trades": int(np.sum(entries)),
                "equity_curve": [10000.0] * len(df),
                "entries": entries,
                "exits": exits
            }
            return None, final_info
