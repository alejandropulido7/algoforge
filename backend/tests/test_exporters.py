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
    assert "InpRSIPeriod = 21;" in code
    assert "InpEMAPeriod = 50;" in code
    assert "InpSMAPeriod = 200;" in code

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
