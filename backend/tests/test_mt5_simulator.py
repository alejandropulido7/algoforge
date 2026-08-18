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

def test_mt5_simulator_spread_commission_swap_costs():
    # Flat market at 100: buy at bar 2, opposite signal at bar 3 -> market signal exit.
    # BUY fills at Ask (open + half spread), SELL exit fills at Bid (open - half spread),
    # so the round-trip pays the full spread plus commissions on BOTH sides plus swap.
    df = pd.DataFrame({
        'Open': [100.0] * 10,
        'High': [100.1] * 10,
        'Low': [99.9] * 10,
        'Close': [100.0] * 10,
    }, index=pd.date_range("2026-01-01", periods=10, freq="1D"))

    buy_signals = np.zeros(10, dtype=bool)
    sell_signals = np.zeros(10, dtype=bool)
    buy_signals[2] = True   # entry at bar 3 open
    sell_signals[3] = True  # exit at bar 4 open

    sim = MT5TradeSimulator({
        "sizingMode": "lots",
        "lotSize": 0.1,
        "slType": "none",
        "tpType": "none",
        "pointSize": 0.0001,
        "spreadPips": 10.0,           # 10 pips = 0.0010 full spread (0.0005 half)
        "commissionPerLot": 5.0,      # per lot per side
        "commissionPerSide": True,
        "swapPerLotPerDay": 2.0,
    })

    res = sim.simulate(df, buy_signals, sell_signals)
    assert res.total_trades == 1
    t = res.trade_log[0]
    # Entry at 100.0005, exit at 99.9995 -> price PnL = -0.001 * 100000 * 0.1 = -10.0
    # Commission: 0.1 * 5 * 2 sides = -1.0. Swap: held 1 calendar day * 2.0 * 0.1 = -0.2
    assert t["entry_price"] == 100.0005
    assert t["exit_price"] == 99.9995
    assert round(t["pnl"], 1) == -11.2

    # Single-side commission mode (legacy behavior): only -5.0 * 0.1 = -0.5 commission
    sim2 = MT5TradeSimulator({
        "sizingMode": "lots",
        "lotSize": 0.1,
        "slType": "none",
        "tpType": "none",
        "pointSize": 0.0001,
        "spreadPips": 10.0,
        "commissionPerLot": 5.0,
        "commissionPerSide": False,
        "swapPerLotPerDay": 2.0,
    })
    res2 = sim2.simulate(df, buy_signals, sell_signals)
    assert round(res2.trade_log[0]["pnl"], 1) == -10.7

def test_mt5_simulator_atr_uses_last_closed_bar():
    # Entry at bar 3 uses ATR of bar 2 (last CLOSED bar), not the forming bar.
    # ATR[2] = 5.0 (huge) vs ATR[3] = 1.0 (calm). SL must be entry - 5.0 = 95.0
    # (old code used the forming bar ATR and produced SL = 99.0).
    atr_val = 5.0
    df = pd.DataFrame({
        'Open': [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        'High': [106.0, 100.0, 106.0, 102.0, 100.0, 100.0, 100.0, 100.0],
        'Low':  [94.0,  100.0, 94.0,  94.0,  100.0, 100.0, 100.0, 100.0],
        'Close':[100.0] * 8,
    })
    # Explicit ATR array: bar 2 (entry-1) has a huge ATR, bar 3 (entry bar) is calm.
    atr = np.full(8, 1.0)
    atr[2] = atr_val

    buy_signals = np.zeros(8, dtype=bool)
    sell_signals = np.zeros(8, dtype=bool)
    buy_signals[2] = True  # deferred entry executes at bar 3 open

    sim = MT5TradeSimulator({
        "sizingMode": "lots",
        "lotSize": 0.1,
        "slType": "atr",
        "slAtrMult": 1.0,
        "tpType": "none",
        "pointSize": 0.0001,
        "spreadPips": 0.0,
    })
    res = sim.simulate(df, buy_signals, sell_signals, atr_array=atr)
    assert res.total_trades == 1
    t = res.trade_log[0]
    # SL = entry - 1.0 * ATR[2] = 100 - 5.0 -> the bar-3 low (94) hits it.
    assert t["exit_reason"] == "sl"
    assert round(t["sl_price"], 4) == 95.0
