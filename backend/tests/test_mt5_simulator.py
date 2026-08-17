import pytest
import pandas as pd
import numpy as np
from engine.backtester.mt5_simulator import MT5TradeSimulator

def test_mt5_simulator_consecutive_stats():
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

def test_mt5_simulator_buy_stop_and_timeout():
    # Price stays flat at 100 (high=100.2), buy stop set at 100.5 -> Should expire after 3 bars
    df = pd.DataFrame({
        'Open': [100.0] * 30,
        'High': [100.2] * 30,
        'Low': [99.8] * 30,
        'Close': [100.0] * 30,
    })

    buy_signals = np.zeros(30, dtype=bool)
    sell_signals = np.zeros(30, dtype=bool)
    buy_signals[5] = True

    sim = MT5TradeSimulator({
        "orderType": "stop",
        "pendingTimeoutBars": 3,
        "pendingOffsetPips": 50.0,  # +0.0050 above high
        "pointSize": 0.0001
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    # Never triggered -> 0 trades executed
    assert res.total_trades == 0

def test_mt5_simulator_max_holding_bars_exit():
    # Buy signal at bar 2, holding limit of 5 bars -> must close at bar 7 with time_exit
    df = pd.DataFrame({
        'Open': [100.0] * 30,
        'High': [101.0] * 30,
        'Low': [99.0] * 30,
        'Close': [100.5] * 30,
    })

    buy_signals = np.zeros(30, dtype=bool)
    sell_signals = np.zeros(30, dtype=bool)
    buy_signals[2] = True

    sim = MT5TradeSimulator({
        "orderType": "market",
        "maxHoldingBars": 5,
        "slType": "none",
        "tpType": "none"
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    assert res.total_trades == 1
    assert res.trade_log[0]["exit_reason"] == "time_exit"
    assert res.trade_log[0]["duration_bars"] >= 5

def test_consecutive_loss_stop_bot():
    # Sequence of 3 losing trades -> bot should stop on 2 consecutive losses
    df = pd.DataFrame({
        'Open': [100.0, 95.0, 90.0, 85.0, 80.0, 75.0, 70.0, 65.0, 60.0, 55.0],
        'High': [101.0, 96.0, 91.0, 86.0, 81.0, 76.0, 71.0, 66.0, 61.0, 56.0],
        'Low': [94.0, 89.0, 84.0, 79.0, 74.0, 69.0, 64.0, 59.0, 54.0, 49.0],
        'Close': [95.0, 90.0, 85.0, 80.0, 75.0, 70.0, 65.0, 60.0, 55.0, 50.0],
    })

    buy_signals = np.zeros(10, dtype=bool)
    sell_signals = np.zeros(10, dtype=bool)
    buy_signals[1] = True
    buy_signals[3] = True
    buy_signals[5] = True
    buy_signals[7] = True

    sim = MT5TradeSimulator({
        "orderType": "market",
        "consecutiveLossAction": "stop_bot",
        "consecutiveLossThreshold": 2,
        "slType": "pips",
        "slPips": 10.0,
        "pointSize": 0.1
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    # The bot triggers SL on trade 1, SL on trade 2 (2 consecutive losses), and stops further entries
    assert res.total_trades <= 2

def test_consecutive_loss_cooldown_reactivation():
    # Sequence with 2 initial losses, 5 bars cooldown, then a new signal -> bot reactivates and trades
    n = 30
    df = pd.DataFrame({
        'Open': [100.0] * n,
        'High': [101.0] * n,
        'Low': [95.0] * n,
        'Close': [98.0] * n,
    })

    buy_signals = np.zeros(n, dtype=bool)
    sell_signals = np.zeros(n, dtype=bool)
    buy_signals[1] = True # Trade 1 (Loss)
    buy_signals[3] = True # Trade 2 (Loss -> triggers stop_bot at bar 3)
    buy_signals[4] = True # Ignored (during cooldown)
    buy_signals[10] = True # Bar 10 is >= 5 bars cooldown -> Reactivated and takes Trade 3!

    sim = MT5TradeSimulator({
        "orderType": "market",
        "consecutiveLossAction": "stop_bot",
        "consecutiveLossThreshold": 2,
        "consecutiveLossReactivation": "cooldown_bars",
        "consecutiveLossAutoCooldown": False,
        "consecutiveLossCooldownBars": 5,
        "slType": "pips",
        "slPips": 10.0,
        "pointSize": 0.1
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    # Trade 1 + Trade 2 + Trade 3 after cooldown = 3 trades
    assert res.total_trades == 3
