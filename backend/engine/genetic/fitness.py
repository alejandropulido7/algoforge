import numpy as np
import pandas as pd
from ..backtester.vectorbt_engine import VectorBTEngine, BacktestResult

def evaluate_strategy_signals(func, indicator_arrays: list[np.ndarray], n_bars: int) -> tuple[np.ndarray, np.ndarray]:
    """Execute compiled GP function with indicator arrays to generate entry/exit boolean arrays."""
    try:
        raw_output = func(*indicator_arrays)
        if isinstance(raw_output, (int, float)):
            raw_output = np.full(n_bars, raw_output)
        elif not isinstance(raw_output, np.ndarray):
            raw_output = np.asarray(raw_output)
        
        if len(raw_output) != n_bars:
            raw_output = np.resize(raw_output, n_bars)

        # Non-zero or positive values trigger entries
        entries = (raw_output > 0.0)
        # Exit on negative or zero
        exits = (raw_output < 0.0)
        return entries, exits
    except Exception:
        return np.zeros(n_bars, dtype=bool), np.zeros(n_bars, dtype=bool)

def evaluate_fitness(
    func, 
    indicator_arrays: list[np.ndarray], 
    df: pd.DataFrame,
    risk_config: dict | None = None
) -> tuple[float, BacktestResult | None]:
    """Backtest a compiled GP strategy and return fitness (Sharpe ratio / Profit Factor) and detailed result."""
    n_bars = len(df)
    entries, exits = evaluate_strategy_signals(func, indicator_arrays, n_bars)
    
    if np.sum(entries) == 0:
        return (-10.0, None)

    engine = VectorBTEngine(risk_config)
    try:
        res = engine.backtest(df, entries, exits)
        score = res.sharpe_ratio if not np.isnan(res.sharpe_ratio) else -5.0
        if res.profit_factor > 1.0:
            score += res.profit_factor
        if res.n_trades < 5:
            score -= 3.0
        return (float(score), res)
    except Exception:
        return (-10.0, None)
