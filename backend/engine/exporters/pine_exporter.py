import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_pine

class PineScriptExporter:
    """Generate dynamic TradingView Pine Script v6 strategy code matching exact AST logic and risk configuration."""

    def _build_indicator_calc(self, clean_name: str, raw_name: str, params: dict) -> str:
        p = params or {}
        
        if clean_name in ["rsi"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"rsi_val = ta.rsi(close, input.int({length}, 'RSI Length'))"
        elif clean_name in ["ema"]:
            length = int(p.get("window", p.get("period", 20)))
            return f"ema_val = ta.ema(close, input.int({length}, 'EMA Length'))"
        elif clean_name in ["sma"]:
            length = int(p.get("window", p.get("period", 20)))
            return f"sma_val = ta.sma(close, input.int({length}, 'SMA Length'))"
        elif clean_name in ["wma"]:
            length = int(p.get("window", p.get("period", 20)))
            return f"wma_val = ta.wma(close, input.int({length}, 'WMA Length'))"
        elif clean_name in ["hma"]:
            length = int(p.get("window", p.get("period", 20)))
            return f"hma_val = ta.hma(close, input.int({length}, 'HMA Length'))"
        elif clean_name in ["atr"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"atr_val = ta.atr(input.int({length}, 'ATR Length'))"
        elif clean_name in ["aroon"]:
            length = int(p.get("window", p.get("period", 25)))
            return f"[aroonUp, aroonDown] = ta.aroon(input.int({length}, 'Aroon Length'))\naroon_val = aroonUp - aroonDown"
        elif clean_name in ["psar", "sar"]:
            step = float(p.get("step", 0.02))
            max_val = float(p.get("max", 0.2))
            return f"psar_val = ta.sar(input.float({step}, 'SAR Step'), input.float({step}, 'SAR Inc'), input.float({max_val}, 'SAR Max'))"
        elif clean_name in ["macd"]:
            fast = int(p.get("window_fast", p.get("fast", 12)))
            slow = int(p.get("window_slow", p.get("slow", 26)))
            sig = int(p.get("window_sign", p.get("signal", 9)))
            return f"[macdLine, macdSignal, macdHist] = ta.macd(close, {fast}, {slow}, {sig})\nmacd_val = macdHist"
        elif clean_name in ["bollinger_bands", "bbands", "bb"]:
            length = int(p.get("window", p.get("period", 20)))
            dev = float(p.get("window_dev", p.get("std", 2.0)))
            return f"[bbMid, bbUpper, bbLower] = ta.bb(close, {length}, {dev})\nbollinger_bands_val = bbMid"
        elif clean_name in ["williams_pctr", "williams_r", "wpr", "williams_pct"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"williams_pctr_val = ta.wpr(input.int({length}, 'Williams %R Length'))"
        elif clean_name in ["stochastic", "stoch"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"stochastic_val = ta.stoch(close, high, low, input.int({length}, 'Stoch Length'))"
        elif clean_name in ["obv"]:
            return "obv_val = ta.obv"
        elif clean_name in ["mfi"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"mfi_val = ta.mfi(close, high, low, volume, input.int({length}, 'MFI Length'))"
        elif clean_name in ["vwap"]:
            return "vwap_val = ta.vwap"
        elif clean_name in ["cci"]:
            length = int(p.get("window", p.get("period", 20)))
            return f"cci_val = ta.cci(close, input.int({length}, 'CCI Length'))"
        elif clean_name in ["adx"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"[diplus, diminus, adx_val] = ta.dmi(input.int({length}, 'ADX Length'), input.int({length}, 'ADX Smoothing'))"
        elif clean_name in ["pvo"]:
            return "pvoFast = ta.ema(volume, 12)\npvoSlow = ta.ema(volume, 26)\npvo_val = pvoSlow != 0 ? ((pvoFast - pvoSlow) / pvoSlow) * 100 : 0.0"
        elif clean_name in ["ichimoku"]:
            return "ichiTenkan = math.avg(ta.highest(high, 9), ta.lowest(low, 9))\nichiKijun = math.avg(ta.highest(high, 26), ta.lowest(low, 26))\nichimoku_val = ichiTenkan - ichiKijun"
        elif clean_name in ["vortex"]:
            return "v_vm_p = math.abs(high - low[1])\nv_tr = math.max(high - low, math.abs(high - close[1]))\nvortex_val = v_tr > 0 ? (v_vm_p / v_tr) : 0.0001"
        elif clean_name in ["ease_of_movement", "eom"]:
            return "em_dist = ((high + low) / 2) - ((high[1] + low[1]) / 2)\nem_box = (volume / 1000000) / (high - low > 0 ? (high - low) : 0.0001)\nease_of_movement_val = em_box > 0 ? (em_dist / em_box) : 0.0001"
        elif clean_name in ["trix"]:
            return "trix_val = ta.roc(ta.ema(ta.ema(ta.ema(math.log(close), 15), 15), 15), 1) * 100"
        elif clean_name in ["donchian_channel", "dc"]:
            return "donchian_channel_val = math.avg(ta.highest(high, 20), ta.lowest(low, 20))"
        elif clean_name in ["force_index"]:
            return "force_index_val = ta.ema((close - close[1]) * volume, 13)"
        elif clean_name in ["roc"]:
            length = int(p.get("window", p.get("period", 14)))
            return f"roc_val = ta.roc(close, input.int({length}, 'ROC Length'))"
        elif clean_name in ["awesome_oscillator", "ao"]:
            return "awesome_oscillator_val = ta.ao"
        elif clean_name in ["daily_return"]:
            return "daily_return_val = (close - close[1]) / (close[1] > 0 ? close[1] : 1.0)"
        elif clean_name in ["daily_log_return"]:
            return "daily_log_return_val = math.log(close / (close[1] > 0 ? close[1] : 1.0))"
        elif clean_name in ["cumulative_return"]:
            return "cumulative_return_val = (close - open[20]) / (open[20] > 0 ? open[20] : 1.0)"
        else:
            length = int(p.get("window", p.get("period", 14)))
            return f"{clean_name}_val = ta.sma(close, input.int({length}, '{raw_name} Length'))"

    def export(self, strategy: dict) -> str:
        rank = strategy.get("rank", 1)
        name = strategy.get("id", f"AlgoForge_Strategy_{rank}")
        symbol = strategy.get("symbol") or "Chart Symbol"
        timeframe = strategy.get("timeframe") or "Chart Timeframe"
        score = float(strategy.get("total_score", 0.0))
        sharpe = float(strategy.get("sharpe_ratio", 0.0))
        total_return = float(strategy.get("total_return_pct", 0.0))
        gross_profit = float(strategy.get("gross_profit", 0.0))
        gross_loss = float(strategy.get("gross_loss", 0.0))
        net_profit = float(strategy.get("total_net_profit", gross_profit - gross_loss))
        win_rate = float(strategy.get("win_rate", 0.0))
        profit_factor = float(strategy.get("profit_factor", 0.0))
        n_trades = int(strategy.get("n_trades", 0))
        max_dd = float(strategy.get("max_drawdown_pct", 0.0))
        mc_score = float(strategy.get("mc_robustness", 0.0))
        mc_ruin = float(strategy.get("mc_prob_ruin", 0.0))
        mc_95_dd = float(strategy.get("mc_95_drawdown", 0.0))
        tree_str = strategy.get("strategy_tree", "")

        # Extract Risk Configuration
        risk_cfg = strategy.get("risk_config")
        if not risk_cfg or not isinstance(risk_cfg, dict):
            risk_cfg = strategy.get("exit_rules", {}).get("risk_config", {})
        if not isinstance(risk_cfg, dict):
            risk_cfg = {}

        direction_str = str(risk_cfg.get("direction", "both")).lower()
        order_type_str = str(risk_cfg.get("orderType") or risk_cfg.get("order_type") or "market").lower()
        pending_offset = float(risk_cfg.get("pendingOffsetPips") or risk_cfg.get("pending_offset_pips") or 5.0)
        max_holding_bars = int(risk_cfg.get("maxHoldingBars") or risk_cfg.get("max_holding_bars") or 0)
        initial_deposit = float(risk_cfg.get("initialDeposit") or 10000.0)
        risk_pct = float(risk_cfg.get("riskPct") or risk_cfg.get("risk_pct") or 1.0)
        
        sl_type_str = str(risk_cfg.get("slType") or risk_cfg.get("sl_type") or "pips").lower()
        sl_pips = float(risk_cfg.get("slPips") or risk_cfg.get("sl_pips") or 50.0)
        sl_atr_mult = float(risk_cfg.get("slAtrMult") or risk_cfg.get("sl_atr_mult") or 1.5)
        
        tp_type_str = str(risk_cfg.get("tpType") or risk_cfg.get("tp_type") or "pips").lower()
        tp_pips = float(risk_cfg.get("tpPips") or risk_cfg.get("tp_pips") or 100.0)
        tp_atr_mult = float(risk_cfg.get("tpAtrMult") or risk_cfg.get("tp_atr_mult") or 3.0)

        # Build indicator parameters dictionary
        ind_configs = strategy.get("indicator_config") or []
        ind_param_map = {}
        if isinstance(ind_configs, list):
            for item in ind_configs:
                if isinstance(item, dict):
                    i_name = str(item.get("name", "")).lower().replace(" ", "_").replace("%", "pct")
                    ind_param_map[i_name] = item.get("params", {})
        elif isinstance(ind_configs, dict):
            for k, v in ind_configs.items():
                i_name = str(k).lower().replace(" ", "_").replace("%", "pct")
                ind_param_map[i_name] = v if isinstance(v, dict) else {}

        # Parse AST & Transpile
        ast = parse_prefix_expression(tree_str)
        used_indicators = extract_indicators(ast)
        transpiled_expr = node_to_pine(ast)

        calcs = []
        for raw_ind in sorted(used_indicators):
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_ind).lower()
            params = ind_param_map.get(clean_name) or ind_param_map.get(raw_ind.lower()) or {}
            calc = self._build_indicator_calc(clean_name, raw_ind, params)
            calcs.append(calc)

        if not calcs:
            calcs.append("sma_val = ta.sma(close, 14)")

        calcs_code = "\n".join(calcs)

        return f"""//@version=6
//+------------------------------------------------------------------+
//|                                     AlgoForge Strategy (Pine v6) |
//|                                     https://algoforge.io         |
//| Strategy Rank: #{rank}           Strategy ID: {name}
//| Symbol: {symbol}     Timeframe: {timeframe}
//| Total Net Profit: ${net_profit:.2f} | Total Return: {total_return:.2f}%
//| Win Rate: {win_rate:.2f}% | Profit Factor: {profit_factor:.2f} | Total Trades: {n_trades}
//| Sharpe Ratio: {sharpe:.2f} | Max Drawdown: {max_dd:.2f}%
//| Monte Carlo Robustness: {mc_score:.1f}% | Prob of Ruin: {mc_ruin:.2f}%
//| MC 95% Confidence Drawdown: {mc_95_dd:.2f}%
//| Evolved Logic: {tree_str}
//+------------------------------------------------------------------+
strategy(
    title="AlgoForge - Strategy #{rank}",
    shorttitle="AF_#{rank}",
    overlay=true,
    initial_capital={initial_deposit:.0f},
    default_qty_type=strategy.percent_of_equity,
    default_qty_value=100.0,
    pyramiding=1,
    commission_type=strategy.commission.cash_per_order,
    commission_value=0.0
)

// === Risk & Execution Inputs ===
inpTradeDirection   = input.string("{direction_str}", "Allowed Direction", options=["both", "long", "short"], group="Risk & Execution")
inpOrderExecution   = input.string("{order_type_str}", "Order Execution Mode", options=["market", "stop", "limit"], group="Risk & Execution")
inpPendingOffset    = input.float({pending_offset:.1f}, "Pending Offset (Pips)", minval=0.0, group="Risk & Execution")
inpMaxHoldingBars   = input.int({max_holding_bars}, "Max Holding Bars (0 = Disabled)", minval=0, group="Risk & Execution")

inpStopLossType     = input.string("{sl_type_str}", "Stop Loss Mode", options=["atr", "pips", "none"], group="Stop Loss & Take Profit")
inpStopLossATRMult  = input.float({sl_atr_mult:.1f}, "SL ATR Multiplier", minval=0.1, group="Stop Loss & Take Profit")
inpStopLossPips     = input.float({sl_pips:.1f}, "SL Pips", minval=1.0, group="Stop Loss & Take Profit")

inpTakeProfitType   = input.string("{tp_type_str}", "Take Profit Mode", options=["atr", "pips", "none"], group="Stop Loss & Take Profit")
inpTakeProfitATRMult= input.float({tp_atr_mult:.1f}, "TP ATR Multiplier", minval=0.1, group="Stop Loss & Take Profit")
inpTakeProfitPips   = input.float({tp_pips:.1f}, "TP Pips", minval=1.0, group="Stop Loss & Take Profit")

// === Indicator Calculations ===
atr_metric = ta.atr(14)
{calcs_code}

// === Evolved Logic Expression Evaluation on Bar [1] ===
signal_val = {transpiled_expr}
buy_condition  = (signal_val > 0.0)
sell_condition = (signal_val < 0.0)

allow_long  = (inpTradeDirection == "both" or inpTradeDirection == "long")
allow_short = (inpTradeDirection == "both" or inpTradeDirection == "short")

pip_size = syminfo.mintick * 10

// === Order Entries ===
if (allow_long and buy_condition and strategy.position_size <= 0)
    if inpOrderExecution == "stop"
        strategy.entry("Long", strategy.long, stop=high[1] + (inpPendingOffset * pip_size))
    else if inpOrderExecution == "limit"
        strategy.entry("Long", strategy.long, limit=low[1] - (inpPendingOffset * pip_size))
    else
        strategy.entry("Long", strategy.long)

if (allow_short and sell_condition and strategy.position_size >= 0)
    if inpOrderExecution == "stop"
        strategy.entry("Short", strategy.short, stop=low[1] - (inpPendingOffset * pip_size))
    else if inpOrderExecution == "limit"
        strategy.entry("Short", strategy.short, limit=high[1] + (inpPendingOffset * pip_size))
    else
        strategy.entry("Short", strategy.short)

// === Dynamic Stop Loss and Take Profit Exits ===
long_sl_dist = inpStopLossType == "atr" ? (inpStopLossATRMult * atr_metric) : (inpStopLossType == "pips" ? (inpStopLossPips * pip_size) : na)
long_tp_dist = inpTakeProfitType == "atr" ? (inpTakeProfitATRMult * atr_metric) : (inpTakeProfitType == "pips" ? (inpTakeProfitPips * pip_size) : na)

short_sl_dist = inpStopLossType == "atr" ? (inpStopLossATRMult * atr_metric) : (inpStopLossType == "pips" ? (inpStopLossPips * pip_size) : na)
short_tp_dist = inpTakeProfitType == "atr" ? (inpTakeProfitATRMult * atr_metric) : (inpTakeProfitType == "pips" ? (inpTakeProfitPips * pip_size) : na)

if (strategy.position_size > 0)
    strategy.exit("Long Exit", "Long", 
        stop = not na(long_sl_dist) ? strategy.position_avg_price - long_sl_dist : na, 
        limit = not na(long_tp_dist) ? strategy.position_avg_price + long_tp_dist : na
    )
    if (sell_condition)
        strategy.close("Long", comment="Signal Exit")

if (strategy.position_size < 0)
    strategy.exit("Short Exit", "Short", 
        stop = not na(short_sl_dist) ? strategy.position_avg_price + short_sl_dist : na, 
        limit = not na(short_tp_dist) ? strategy.position_avg_price - short_tp_dist : na
    )
    if (buy_condition)
        strategy.close("Short", comment="Signal Exit")

// === Time-Based Exit (Max Holding Bars) ===
if (inpMaxHoldingBars > 0 and strategy.position_size != 0 and strategy.opentrades > 0)
    int bars_held = bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1)
    if (bars_held >= inpMaxHoldingBars)
        strategy.close_all(comment="Max Holding Bars")
"""
