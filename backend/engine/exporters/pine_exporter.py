import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_pine

class PineScriptExporter:
    """Generate dynamic TradingView Pine Script v5 strategy code matching the exact strategy tree logic."""

    PINE_CALCS = {
        "rsi": "rsiVal = ta.rsi(close, input.int(14, 'RSI Length'))",
        "ema": "emaVal = ta.ema(close, input.int(20, 'EMA Length'))",
        "sma": "smaVal = ta.sma(close, input.int(20, 'SMA Length'))",
        "atr": "atrVal = ta.atr(input.int(14, 'ATR Length'))",
        "aroon": "aroonVal = ta.aroon(input.int(25, 'Aroon Length'))",
        "psar": "psarVal = ta.sar(input.float(0.02, 'SAR Step'), input.float(0.2, 'SAR Max'))",
        "macd": "[macdLine, macdSignal, macdHist] = ta.macd(close, 12, 26, 9)\nmacdVal = macdHist",
        "bollinger_bands": "[bbMid, bbUpper, bbLower] = ta.bb(close, 20, 2.0)\nbollinger_bandsVal = bbMid",
        "bbands": "[bbMid, bbUpper, bbLower] = ta.bb(close, 20, 2.0)\nbbandsVal = bbMid",
        "williams_r": "williams_rVal = ta.wpr(input.int(14, 'Williams %R Length'))",
        "williams_pct": "williams_pctVal = ta.wpr(input.int(14, 'Williams %R Length'))",
        "stochastic": "stochasticVal = ta.stoch(close, high, low, 14)",
        "obv": "obvVal = ta.obv",
        "vwap": "vwapVal = ta.vwap",
        "cci": "cciVal = ta.cci(close, 20)",
        "adx": "adxVal = ta.sma(ta.tr, 14)"
    }

    def export(self, strategy: dict) -> str:
        name = strategy.get("id", "AlgoForge_Strategy")
        score = strategy.get("total_score", 0.0)
        sharpe = strategy.get("sharpe_ratio", 0.0)
        mc = strategy.get("mc_robustness", 0.0)
        tree_str = strategy.get("strategy_tree", "")

        ast = parse_prefix_expression(tree_str)
        used_indicators = extract_indicators(ast)
        transpiled_expr = node_to_pine(ast)

        calcs = []
        for raw_ind in sorted(used_indicators):
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_ind).lower()
            calc = self.PINE_CALCS.get(clean_name, f"{clean_name}Val = ta.sma(close, 14)")
            calcs.append(calc)

        if not calcs:
            calcs.append("maVal = ta.sma(close, 14)")

        calcs_code = "\n".join(calcs)

        risk_cfg = strategy.get("risk_config", {})
        direction_str = risk_cfg.get("direction", "both")
        order_type_str = risk_cfg.get("orderType") or risk_cfg.get("order_type") or "market"
        max_holding_bars = int(risk_cfg.get("maxHoldingBars") or risk_cfg.get("max_holding_bars") or 0)
        pending_offset = float(risk_cfg.get("pendingOffsetPips") or risk_cfg.get("pending_offset_pips") or 5.0)

        return f"""//@version=5
//+------------------------------------------------------------------+
//| AlgoForge Generated Strategy                                     |
//| Total Score: {score:<6.2f} | Sharpe: {sharpe:<5.2f} | MC Robustness: {mc:<5.1f}% |
//| Rule: {tree_str}
//+------------------------------------------------------------------+
strategy(
    title="AlgoForge - {name}",
    shorttitle="AF_{name[:12]}",
    overlay=true,
    initial_capital=10000,
    default_qty_type=strategy.percent_of_equity,
    default_qty_value=10,
    commission_type=strategy.commission.percent,
    commission_value=0.1
)

// === Timing & Execution Inputs ===
inpMaxHoldingBars = input.int({max_holding_bars}, "Max Holding Bars (0 = Disabled)", minval=0)
inpPendingOffset = input.float({pending_offset}, "Pending Offset (Pips)", minval=0.0)

// === Indicator Calculations ===
{calcs_code}

// === Evolved Logic Signal ===
signalVal = {transpiled_expr}
allowLong  = "{"true" if direction_str in ["both", "long"] else "false"}"
allowShort = "{"true" if direction_str in ["both", "short"] else "false"}"

longCondition  = allowLong and (signalVal > 0)
shortCondition = allowShort and (signalVal < 0)

// === Order Execution ===
{"// Buy Stop / Sell Stop Orders" if order_type_str == "stop" else ("// Buy Limit / Sell Limit Orders" if order_type_str == "limit" else "// On Market Execution")}
if (longCondition and strategy.position_size == 0)
    {"strategy.entry('Long', strategy.long, stop=high[1] + (inpPendingOffset * syminfo.mintick * 10))" if order_type_str == "stop" else ("strategy.entry('Long', strategy.long, limit=low[1] - (inpPendingOffset * syminfo.mintick * 10))" if order_type_str == "limit" else "strategy.entry('Long', strategy.long)")}

if (shortCondition and strategy.position_size == 0)
    {"strategy.entry('Short', strategy.short, stop=low[1] - (inpPendingOffset * syminfo.mintick * 10))" if order_type_str == "stop" else ("strategy.entry('Short', strategy.short, limit=high[1] + (inpPendingOffset * syminfo.mintick * 10))" if order_type_str == "limit" else "strategy.entry('Short', strategy.short)")}

// === Time-Based Exit (Max Holding Bars) ===
if (inpMaxHoldingBars > 0 and strategy.position_size != 0)
    if (ta.barssince(strategy.opentrades.entry_bar_index(strategy.opentrades - 1)) >= inpMaxHoldingBars)
        strategy.close_all(comment="Time Exit")
"""
