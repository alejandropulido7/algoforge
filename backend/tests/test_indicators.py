import pandas as pd
import numpy as np
from engine.indicators.calculator import calculate_single, calculate_all

def test_sma():
    df = pd.DataFrame({"Close": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]})
    res = calculate_single(df, "SMA", {"length": 3})
    assert res is not None

def test_rsi():
    df = pd.DataFrame({
        "Close": [10, 12, 11, 13, 15, 14, 16, 18, 17, 19, 21, 20, 22, 24, 23, 25, 27, 26, 28, 30]
    })
    res = calculate_single(df, "RSI", {"length": 5})
    assert res is not None

def test_calculate_all():
    df = pd.DataFrame({
        "Open": np.linspace(100, 110, 50),
        "High": np.linspace(101, 112, 50),
        "Low": np.linspace(99, 109, 50),
        "Close": np.linspace(100, 110, 50),
        "Volume": np.full(50, 1000)
    })
    results = calculate_all(df, [{"name": "SMA", "params": {"length": 5}}, {"name": "EMA", "params": {"length": 5}}])
    assert len(results) >= 2
