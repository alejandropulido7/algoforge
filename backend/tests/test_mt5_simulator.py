import pytest
import pandas as pd
import numpy as np
from engine.backtester.mt5_simulator import MT5TradeSimulator

def test_mt5_simulator_consecutive_stats():
    # 100 bars of synthetic data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Open': [100.0] * 100,
        'High': [102.0] * 100,
        'Low': [98.0] * 100,
        'Close': [100.0] * 100,
    })

    buy_signals = np.zeros(100, dtype=bool)
    sell_signals = np.zeros(100, dtype=bool)
    buy_signals[5] = True
    sell_signals[10] = True
    buy_signals[15] = True
    sell_signals[20] = True

    sim = MT5TradeSimulator({
        "initialDeposit": 10000.0,
        "sizingMode": "lots",
        "lotSize": 0.1,
        "slType": "pips",
        "slPips": 50.0,
        "tpType": "pips",
        "tpPips": 100.0
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    assert res.initial_deposit == 10000.0
    assert hasattr(res, "consecutive_wins_max")
    assert hasattr(res, "consecutive_losses_max")
    assert hasattr(res, "consecutive_wins_avg")
    assert hasattr(res, "consecutive_losses_avg")
    assert hasattr(res, "expected_payoff")
    assert hasattr(res, "gross_profit")
    assert hasattr(res, "gross_loss")
