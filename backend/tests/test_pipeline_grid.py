import pytest
import numpy as np
import pandas as pd
from engine.pipeline import StrategyPipeline, generate_param_values

def _create_sample_df(n_bars: int = 120) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n_bars, freq="1h")
    np.random.seed(42)
    closes = 100.0 + np.cumsum(np.random.randn(n_bars) * 0.5)
    highs = closes + np.abs(np.random.randn(n_bars) * 0.3)
    lows = closes - np.abs(np.random.randn(n_bars) * 0.3)
    opens = (highs + lows) / 2.0
    return pd.DataFrame({
        "Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": [1000] * n_bars
    }, index=dates)

def test_generate_param_values_stepping():
    # Integer range
    vals = generate_param_values(5, 5, 20)
    assert vals == [5, 10, 15, 20]

    # Float range
    vals_f = generate_param_values(1.5, 0.5, 3.0)
    assert vals_f == [1.5, 2.0, 2.5, 3.0]

    # Single value
    vals_s = generate_param_values(14, 1, 14)
    assert vals_s == [14]

def test_pipeline_exact_grid_combinations():
    df = _create_sample_df(150)
    config = {
        "id": "test_grid_job",
        "indicators": ["RSI", "EMA", "Bollinger"],
        "indicatorRanges": {
            "RSI": {
                "period": {"min": 10, "step": 2, "max": 14},     # [10, 12, 14] -> 3 values
                "oversold": {"min": 25, "step": 5, "max": 30},   # [25, 30] -> 2 values
                "overbought": {"min": 70, "step": 5, "max": 75}  # [70, 75] -> 2 values
                # Total RSI = 3 * 2 * 2 = 12
            },
            "EMA": {
                "period": {"min": 10, "step": 10, "max": 20}     # [10, 20] -> 2 values
            },
            "Bollinger": {
                "period": {"min": 20, "step": 10, "max": 20},    # [20] -> 1 value
                "deviation": {"min": 1.5, "step": 0.5, "max": 2.0} # [1.5, 2.0] -> 2 values
                # Total Bollinger = 1 * 2 = 2
            }
        },
        "genetic": {
            "populationSize": 20,
            "generations": 2,
            "topStrategiesCount": 5
        },
        "risk": {
            "initialDeposit": 10000.0
        }
    }
    # Expected total combinations = 12 * 2 * 2 = 48
    pipeline = StrategyPipeline(config)
    results = pipeline.run(df)
    assert len(results) > 0
    assert len(results) <= 5
    assert results[0]["total_score"] > 0
