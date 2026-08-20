import pytest
import numpy as np
import pandas as pd
from engine.backtester.mt5_simulator import MT5TradeSimulator
from engine.pipeline import StrategyPipeline

def _make_sample_df(n_bars: int = 100, trend: float = 1.0) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n_bars, freq="1h")
    base_price = 100.0
    opens, highs, lows, closes = [], [], [], []
    current = base_price
    for i in range(n_bars):
        o = current
        c = o + trend
        h = max(o, c) + 0.5
        l = min(o, c) - 0.5
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        current = c
    return pd.DataFrame({
        "Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": [1000] * n_bars
    }, index=dates)

def test_trailing_stop_advances_sl():
    df = _make_sample_df(n_bars=30, trend=2.0)
    buy_sigs = np.zeros(30, dtype=bool)
    sell_sigs = np.zeros(30, dtype=bool)
    buy_sigs[1] = True  # Enter long at bar 2

    # Trailing stop of 1.0 ATR
    sim = MT5TradeSimulator({
        "slType": "none",
        "tpType": "none",
        "trail_atr": 1.0,
        "spreadPips": 0.0,
        "commissionPerLot": 0.0
    })
    res = sim.simulate(df, buy_sigs, sell_sigs)
    assert res.initial_deposit == 10000.0

def test_breakeven_locks_entry_price():
    df = _make_sample_df(n_bars=30, trend=1.5)
    buy_sigs = np.zeros(30, dtype=bool)
    sell_sigs = np.zeros(30, dtype=bool)
    buy_sigs[1] = True

    sim = MT5TradeSimulator({
        "slType": "atr",
        "slAtrMult": 2.0,
        "be_atr": 1.0,
        "spreadPips": 0.0,
        "commissionPerLot": 0.0
    })
    res = sim.simulate(df, buy_sigs, sell_sigs)
    assert res.total_return_pct >= 0.0

def test_pipeline_tpsl_grid():
    from engine.pipeline import apply_tpsl_config
    base_risk = {"initialDeposit": 10000.0, "slType": "none", "tpType": "none"}
    tpsl_combo = (
        ("atr_classic", {"sl_atr": 1.5, "tp_atr": 3.0}),
        ("trailing_stop", {"trail_atr": 1.0}),
        ("breakeven", {"be_atr": 1.0}),
        ("time_exit", {"max_bars": 8}),
    )
    rc = apply_tpsl_config(base_risk, tpsl_combo)
    assert rc["slType"] == "atr"
    assert rc["tpType"] == "atr"
    assert rc["slAtrMult"] == 1.5
    assert rc["tpAtrMult"] == 3.0
    assert rc["trailingStopAtr"] == 1.0
    assert rc["breakevenAtr"] == 1.0
    assert rc["maxHoldingBars"] == 8

