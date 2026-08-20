import pandas as pd
import numpy as np
from engine.backtester.mt5_simulator import MT5TradeSimulator, get_symbol_contract_specs

def test_get_symbol_contract_specs():
    # Crypto
    c, p, sp = get_symbol_contract_specs("ETH-USD")
    assert c == 1.0
    c, p, sp = get_symbol_contract_specs("BTCUSDT")
    assert c == 1.0
    # Metals
    c, p, sp = get_symbol_contract_specs("XAUUSD")
    assert c == 100.0
    # Forex
    c, p, sp = get_symbol_contract_specs("EURUSD")
    assert c == 100000.0
    # Price fallback
    c, p, sp = get_symbol_contract_specs("", price=3300.0)
    assert c == 1.0

def test_eth_1_pct_risk_sizing_and_pnl():
    # ETH-USD around 3340
    dates = pd.date_range("2026-01-01", periods=50, freq="1h")
    closes = np.linspace(3342.0, 3338.0, 50)
    highs = closes + 5.0
    lows = closes - 5.0
    opens = closes + 1.0
    df = pd.DataFrame({"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": [1000]*50}, index=dates)

    buy_signals = np.zeros(50, dtype=bool)
    sell_signals = np.zeros(50, dtype=bool)
    buy_signals[5] = True
    sell_signals[15] = True

    sim = MT5TradeSimulator({
        "symbol": "ETH-USD",
        "initialDeposit": 1000.0,
        "sizingMode": "risk_pct",
        "riskPct": 1.0,
        "riskBase": "initial_deposit",
        "slType": "atr",
        "slAtrMult": 1.5
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    assert res.total_trades == 1
    t = res.trade_log[0]
    # Trade loss should be aligned with ~1% ($10), not thousands of dollars!
    assert abs(t["pnl"]) <= 20.0
    assert res.total_net_profit > -50.0

def test_ruin_protection_stops_trading():
    # Downward spiral dataset
    dates = pd.date_range("2026-01-01", periods=100, freq="1h")
    closes = np.linspace(100.0, 1.0, 100)
    df = pd.DataFrame({"Open": closes+1, "High": closes+2, "Low": closes-2, "Close": closes, "Volume": [100]*100}, index=dates)

    buy_signals = np.ones(100, dtype=bool)
    sell_signals = np.zeros(100, dtype=bool)

    sim = MT5TradeSimulator({
        "symbol": "CRYPTO",
        "initialDeposit": 10.0,
        "sizingMode": "risk_pct",
        "riskPct": 100.0,
        "slType": "pct",
        "slPct": 50.0
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    # The simulator should stop trading when ruined
    assert res.total_trades <= 2
