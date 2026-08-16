import pandas as pd
import numpy as np
from engine.backtester.vectorbt_engine import VectorBTEngine

def test_backtest_simple():
    df = pd.DataFrame({
        "Close": [100.0, 105.0, 102.0, 110.0, 108.0, 115.0, 112.0, 120.0]
    })
    entries = np.array([True, False, True, False, False, False, False, False])
    exits = np.array([False, True, False, True, False, False, False, False])
    
    engine = VectorBTEngine()
    res = engine.backtest(df, entries, exits)
    assert res.n_trades >= 1
    assert res.total_return is not None
