import numpy as np
import pandas as pd
from ..backtester.vectorbt_engine import VectorBTEngine, BacktestResult

def evaluate_strategy_signals(
    func, 
    indicator_arrays: list[np.ndarray], 
    n_bars: int,
    direction: str = "both"
) -> tuple[np.ndarray, np.ndarray]:
    """Execute compiled GP function to generate buy/sell signal boolean arrays.

    Returns (entries, exits) in the simulator/EA convention:
      entries = (signal > 0.0)  -> long entry / short exit candidates
      exits   = (signal <= 0.0) -> short entry / long exit candidates

    The trade direction restriction is applied INSIDE the simulator / EA from
    risk_config (previously the "short" branch inverted the signals here,
    making the Python simulator trade the opposite side of the EA).
    """
    try:
        raw_output = func(*indicator_arrays)
        if isinstance(raw_output, (int, float)):
            raw_output = np.full(n_bars, raw_output)
        elif not isinstance(raw_output, np.ndarray):
            raw_output = np.asarray(raw_output)
        
        if len(raw_output) != n_bars:
            raw_output = np.resize(raw_output, n_bars)

        entries = (raw_output > 0.0)
        exits = (raw_output <= 0.0)

        return entries, exits
    except Exception:
        return np.zeros(n_bars, dtype=bool), np.zeros(n_bars, dtype=bool)

def evaluate_fitness(
    func, 
    indicator_arrays: list[np.ndarray], 
    df: pd.DataFrame,
    risk_config: dict | None = None,
    tree_len: int = 5,
    atr_array: np.ndarray | None = None
) -> tuple[float, BacktestResult | None]:
    """Backtest a compiled GP strategy and return fitness with parsimony and trade frequency regularization."""
    n_bars = len(df)
    entries, exits = evaluate_strategy_signals(func, indicator_arrays, n_bars)

    if np.sum(entries) == 0:
        return (-10.0, None)

    engine = VectorBTEngine(risk_config)
    try:
        res = engine.backtest(df, entries, exits, atr_array=atr_array)
        sharpe = res.sharpe_ratio if not np.isnan(res.sharpe_ratio) else -5.0
        score = float(sharpe)

        if res.profit_factor > 1.0:
            score += min(3.0, res.profit_factor - 1.0)
        
        # Penalize insufficient trades (no statistical significance)
        if res.n_trades < 10:
            score -= 4.0
        elif res.n_trades < 25:
            score -= 2.0
            
        # Penalize excessive hyper-trading churn (> 400 trades on sample) to favor realistic swing setups
        if res.n_trades > 400:
            score -= min(5.0, (res.n_trades - 400) / 100.0)

        # Parsimony pressure: penalize unnecessarily large trees to favor compact 2-3 indicator combos
        score -= min(1.0, 0.02 * tree_len)

        return (float(score), res)
    except Exception:
        return (-10.0, None)
