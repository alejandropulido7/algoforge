import pytest
from engine.exporters.mt5_exporter import MT5Exporter
from engine.exporters.onnx_mt5_exporter import OnnxMT5Exporter
from algoforge.services.export_service import export_strategy, _LOCAL_STRATEGIES

def test_mt5_exporter_exact_inputs():
    strategy = {
        "id": "Test_Custom_Strategy_01",
        "rank": 3,
        "symbol": "NAS100",
        "timeframe": "M15",
        "total_score": 85.5,
        "sharpe_ratio": 2.45,
        "total_return_pct": 142.3,
        "win_rate": 62.5,
        "profit_factor": 2.15,
        "n_trades": 180,
        "max_drawdown_pct": 8.4,
        "mc_robustness": 94.2,
        "mc_prob_ruin": 0.05,
        "mc_95_drawdown": 11.2,
        "strategy_tree": "and(gt(RSI, EMA), gt(Close, SMA))",
        "indicator_config": [
            {"name": "RSI", "params": {"period": 21}},
            {"name": "EMA", "params": {"period": 50}},
            {"name": "SMA", "params": {"period": 200}}
        ],
        "risk_config": {
            "sizingMode": "risk_pct",
            "riskPct": 2.5,
            "lotSize": 0.5,
            "direction": "long",
            "orderType": "stop",
            "pendingTimeoutBars": 6,
            "pendingOffsetPips": 8.0,
            "maxHoldingBars": 12,
            "consecutiveLossAction": "stop_bot",
            "consecutiveLossThreshold": 4,
            "consecutiveLossReductionPct": 50.0,
            "consecutiveLossReactivation": "cooldown_bars",
            "consecutiveLossCooldownBars": 15,
            "consecutiveLossCooldownDays": 2,
            "slType": "atr",
            "slAtrMult": 2.0,
            "slPips": 40.0,
            "tpType": "atr",
            "tpAtrMult": 4.0,
            "tpPips": 80.0
        }
    }

    exporter = MT5Exporter()
    code = exporter.export(strategy)

    # 1. Check Header Info & Performance parms
    assert "Strategy Rank: #3" in code
    assert "Symbol: NAS100" in code
    assert "Timeframe: M15" in code
    assert "Sharpe Ratio: 2.45" in code
    assert "Win Rate: 62.50%" in code
    assert "Monte Carlo Robustness: 94.2%" in code

    # 2. Check Risk & Execution Inputs
    assert "InpTradeDirection       = 1;" in code  # Long Only
    assert "InpOrderExecution       = 1;" in code  # Buy Stop / Sell Stop
    assert "InpPendingTimeoutBars   = 6;" in code
    assert "InpPendingOffsetPips    = 8.0;" in code
    assert "InpMaxHoldingBars       = 12;" in code
    assert "InpConsecLossAction     = 2;" in code  # Stop Bot
    assert "InpConsecLossThreshold  = 4;" in code
    assert "InpReactivationMode     = 1;" in code  # Cooldown bars
    assert "InpCooldownBars         = 15;" in code
    assert "InpSizingMode           = 1;" in code  # Risk %
    assert "InpRiskPercent          = 2.50;" in code
    assert "InpStopLossType         = 1;" in code  # ATR Mode
    assert "InpStopLossATRMult      = 2.0;" in code
    assert "InpTakeProfitType       = 1;" in code  # ATR Mode
    assert "InpTakeProfitATRMult    = 4.0;" in code

    # 3. Check Indicator Inputs
    assert "Inp_rsi_Period = 21;" in code
    assert "Inp_ema_Period = 50;" in code
    assert "Inp_sma_Period = 200;" in code

    # 4. Max simultaneous positions exported
    assert "InpMaxSimultaneousTrades = 1;" in code

def test_onnx_mt5_exporter_exact_inputs():
    strategy = {
        "id": "RL_PPO_Strategy_07",
        "rank": 7,
        "symbol": "BTCUSD",
        "timeframe": "H1",
        "total_score": 91.0,
        "sharpe_ratio": 2.8,
        "total_return_pct": 210.0,
        "win_rate": 58.0,
        "profit_factor": 2.4,
        "n_trades": 320,
        "max_drawdown_pct": 12.0,
        "mc_robustness": 96.0,
        "mc_prob_ruin": 0.0,
        "mc_95_drawdown": 14.5,
        "is_rl": True,
        "risk_config": {
            "sizingMode": "lots",
            "lotSize": 0.35,
            "direction": "both",
            "maxHoldingBars": 24,
            "consecutiveLossAction": "reduce_risk",
            "consecutiveLossThreshold": 3,
            "consecutiveLossReductionPct": 60.0,
            "consecutiveLossReactivation": "next_day",
            "slType": "pips",
            "slPips": 150.0,
            "tpType": "pips",
            "tpPips": 300.0
        }
    }

    exporter = OnnxMT5Exporter()
    code = exporter.export(strategy)

    assert "Strategy Rank: #7" in code
    assert "Symbol: BTCUSD" in code
    assert "InpTradeDirection       = 0;" in code
    assert "InpMaxHoldingBars       = 24;" in code
    assert "InpConsecLossAction     = 1;" in code # Reduce risk
    assert "InpConsecLossThreshold  = 3;" in code
    assert "InpConsecLossReduction  = 60.0;" in code
    assert "InpReactivationMode     = 3;" in code # Next Day
    assert "InpSizingMode           = 0;" in code # Lots
    assert "InpLotSize              = 0.35;" in code
    assert "InpStopLossPips         = 150.0;" in code
    assert "InpTakeProfitPips       = 300.0;" in code

def test_mt5_exporter_williams_and_vwap():
    strategy = {
        "id": "d5906d9f-d1e9-4f01-bd4f-747ce8cdafce",
        "rank": 1,
        "symbol": "NAS100",
        "timeframe": "15m",
        "strategy_tree": "lt(add(VWAP, Williams_pctR), lt(VWAP, EMA))",
        "indicator_config": [
            {"name": "VWAP", "params": {"period": 14}},
            {"name": "Williams_pctR", "params": {"period": 14}},
            {"name": "EMA", "params": {"period": 20}}
        ],
        "risk_config": {
            "direction": "long",
            "orderType": "market",
            "slType": "atr",
            "tpType": "atr"
        }
    }

    exporter = MT5Exporter()
    code = exporter.export(strategy)

    # Verify handles use NATIVE MT5 indicators (not iCustom ta ports)
    assert "int handle_williams_pctr;" in code
    assert "iWPR(_Symbol, _Period, Inp_williams_pctr_Period);" in code
    assert "IndicatorRelease(handle_williams_pctr);" in code
    assert "double williams_pctr_val[];" in code
    assert "CopyBuffer(handle_williams_pctr, 0, 0, 4, williams_pctr_val)" in code
    assert "williams_pctr_val[1]" in code
    # EMA uses native iMA with MODE_EMA; VWAP is computed inline.
    assert "iMA(_Symbol, _Period, Inp_ema_Period, 0, MODE_EMA, PRICE_CLOSE);" in code
    assert "iCustom" not in code

def test_mt5_exporter_max_simultaneous_trades_exported():
    strategy = {
        "id": "MultiPos_01",
        "rank": 1,
        "strategy_tree": "gt(RSI, c_50)",
        "indicator_config": [{"name": "RSI", "params": {}}],
        "risk_config": {
            "direction": "both",
            "orderType": "market",
            "maxSimultaneousTrades": 3,
            "slType": "pips",
            "tpType": "pips"
        }
    }
    code = MT5Exporter().export(strategy)
    assert "InpMaxSimultaneousTrades = 3;" in code
    assert "position_count + pending_count < InpMaxSimultaneousTrades" in code

def test_mt5_exporter_raw_price_series_inline():
    strategy = {
        "id": "PriceSeries_01",
        "rank": 1,
        "strategy_tree": "and(gt(Close, SMA), gt(Open, Low))",
        "indicator_config": [
            {"name": "Close", "params": {}},
            {"name": "Open", "params": {}},
            {"name": "Low", "params": {}},
            {"name": "SMA", "params": {"period": 20}}
        ],
        "risk_config": {
            "direction": "long",
            "orderType": "market",
            "slType": "pips",
            "tpType": "pips"
        }
    }
    code = MT5Exporter().export(strategy)
    assert "CopyClose(_Symbol, _Period, 0, 4, close_val)" in code
    assert "CopyOpen(_Symbol, _Period, 0, 4, open_val)" in code
    assert "CopyLow(_Symbol, _Period, 0, 4, low_val)" in code
    assert "close_val[1]" in code
    assert "open_val[1]" in code
    assert "low_val[1]" in code
    assert "iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\EMA\"" not in code

def test_mt5_exporter_optimized_indicator_values_section():
    # The generated EA must document the OPTIMAL indicator values used to
    # select the strategy, and the header must show real net profit (not $0).
    strategy = {
        "id": "Optimal_01",
        "rank": 2,
        "symbol": "EURUSD",
        "timeframe": "1h",
        "strategy_tree": "and(gt(RSI, EMA), lt(Bollinger, c_50))",
        "n_trades": 25,
        "indicator_config": [
            {"name": "RSI", "params": {"period": 21}, "var_name": "RSI"},
            {"name": "EMA", "params": {"period": 50}, "var_name": "EMA"},
            {"name": "Bollinger", "params": {"period": 22, "deviation": 2.25}, "var_name": "Bollinger"},
        ],
        "trade_log": [
            {"pnl": 90.4}, {"pnl": -4.6}, {"pnl": 60.0},
        ],
        "risk_config": {"direction": "long", "orderType": "market", "slType": "none", "tpType": "none"}
    }
    code = MT5Exporter().export(strategy)

    # 1. Optimized indicator values section present with actual params.
    assert "Optimized Indicator Values (used to select this strategy)" in code
    assert "Bollinger: window=22, window_dev=2.25" in code
    assert "RSI: window=21" in code
    assert "EMA: window=50" in code

    # 2. Inputs reflect the effective (frontend-normalized) params.
    assert "Inp_bollinger_Period = 22;" in code
    assert "Inp_bollinger_Dev = 2.25;" in code
    assert "Inp_rsi_Period = 21;" in code

    # 3. Header net profit computed from trade_log when fields are missing.
    assert "Total Net Profit: $145.80" in code

def test_mt5_exporter_net_profit_fallback_to_detailed_metrics():
    strategy = {
        "id": "Fallback_01",
        "rank": 1,
        "strategy_tree": "gt(RSI, c_50)",
        "indicator_config": [{"name": "RSI", "params": {}}],
        "exit_rules": {
            "detailed_metrics": {"gross_profit": 500.0, "gross_loss": 200.0}
        },
        "risk_config": {"direction": "long", "orderType": "market", "slType": "none", "tpType": "none"}
    }
    code = MT5Exporter().export(strategy)
    assert "Total Net Profit: $300.00" in code

def test_mt5_exporter_combostrategy_iclose():
    strategy = {
        "id": "Combo_EMA_01",
        "rank": 1,
        "strategy_tree": "ComboStrategy(EMA(period=20))",
        "indicator_config": [{"name": "EMA", "params": {"window": 20}, "var_name": "EMA"}],
        "risk_config": {"swingLookback": 20, "slType": "atr", "slAtrMult": 1.5, "tpType": "atr", "tpAtrMult": 3.0}
    }
    code = MT5Exporter().export(strategy)
    assert "iClose(_Symbol, _Period, 1)" in code
    assert "close_val[1]" not in code
    assert "swing_structure_val" not in code

def test_mt5_exporter_combostrategy_tpsl_filtering():
    strategy = {
        "id": "Combo_Legacy_01",
        "rank": 2,
        "strategy_tree": "ComboStrategy(EMA(period=90) | TP/SL: atr_classic(sl_atr=0.5, tp_atr=5.0), swing_structure(lookback=20))",
        "indicator_config": [{"name": "EMA", "params": {"window": 90}, "var_name": "EMA"}],
        "risk_config": {"swingLookback": 20}
    }
    code = MT5Exporter().export(strategy)
    assert "iClose(_Symbol, _Period, 1)" in code
    assert "close_val[1]" not in code
    assert "swing_structure_val" not in code
    assert "atr_classic_val" not in code
