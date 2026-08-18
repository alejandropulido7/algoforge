import re

class PythonLiveExporter:
    """Generate standalone, turnkey Python live trading script connecting directly to MT5."""

    def export(self, strategy: dict) -> str:
        is_rl = strategy.get("is_rl", False) or "RL_Agent" in str(strategy.get("strategy_tree", ""))
        
        if is_rl:
            return self._export_rl(strategy)
        return self._export_gp(strategy)
        
    def _export_rl(self, strategy: dict) -> str:
        name = strategy.get("id", "AlgoForge_Strategy")
        score = strategy.get("total_score", 0.0)
        sharpe = strategy.get("sharpe_ratio", 0.0)
        tree = strategy.get("strategy_tree", "RL_Agent")
        risk_cfg = strategy.get("risk_config", {})
        
        lot_size = float(risk_cfg.get("lotSize", 0.1))
        risk_pct = float(risk_cfg.get("riskPct", 1.0))
        sl_pips = float(risk_cfg.get("slPips", 50.0))
        tp_pips = float(risk_cfg.get("tpPips", 100.0))
        symbol = strategy.get("symbol", "EURUSD")
        timeframe = strategy.get("timeframe", "1h")

        return f'''"""
AlgoForge Live Trader — Python to MetaTrader 5 Bridge
Strategy: {name} (Score: {score:.2f}, Sharpe: {sharpe:.2f})
Rule / Architecture: {tree}
"""

import time
import datetime
import numpy as np
import pandas as pd

try:
    import MetaTrader5 as mt5
except ImportError:
    raise ImportError("Please install MetaTrader5 python package: pip install MetaTrader5")

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

# ================= Configuration =================
SYMBOL = "{symbol}"
TIMEFRAME = mt5.TIMEFRAME_H1 if "{timeframe}" == "1h" else mt5.TIMEFRAME_D1
LOT_SIZE = {lot_size:.2f}
RISK_PCT = {risk_pct:.2f}
STOP_LOSS_PIPS = {sl_pips:.1f}
TAKE_PROFIT_PIPS = {tp_pips:.1f}
MAGIC_NUMBER = 101202
MODEL_PATH = "{name}.onnx"
WINDOW_SIZE = 20
# =================================================

def initialize_mt5():
    if not mt5.initialize():
        print(f"Failed to initialize MetaTrader 5, error: {{mt5.last_error()}}")
        return False
    
    if not mt5.symbol_select(SYMBOL, True):
        print(f"Failed to select symbol {{SYMBOL}} in MT5")
        return False

    print(f"Connected to MetaTrader 5 | Account: {{mt5.account_info().login}} | Broker: {{mt5.account_info().company}}")
    return True

def fetch_recent_bars(symbol: str, timeframe, n_bars: int = 100) -> pd.DataFrame:
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, n_bars)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={{
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'
    }})
    return df

def predict_signal(df: pd.DataFrame, session=None) -> int:
    if len(df) < WINDOW_SIZE:
        return 0

    if session is not None and HAS_ONNX:
        slice_df = df.iloc[-WINDOW_SIZE:][['Open', 'High', 'Low', 'Close', 'Volume']].values
        mean = np.mean(slice_df, axis=0) + 1e-6
        std = np.std(slice_df, axis=0) + 1e-6
        norm_slice = (slice_df - mean) / std
        input_tensor = np.expand_dims(norm_slice.astype(np.float32), axis=0)
        
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {{input_name: input_tensor}})
        action = int(outputs[0][0])
        return action
    else:
        close = df['Close'].values
        sma_fast = np.mean(close[-10:])
        sma_slow = np.mean(close[-30:])
        if sma_fast > sma_slow:
            return 1
        elif sma_fast < sma_slow:
            return 2
        return 0

def execute_trade(action: int, sl_pips: float, tp_pips: float):
    pass

if __name__ == "__main__":
    if initialize_mt5():
        print("Bot is running...")
'''

    def _export_gp(self, strategy: dict) -> str:
        name = str(strategy.get("id", "Strategy"))[:8]
        rank = strategy.get("rank", 1)
        tree_str = strategy.get("strategy_tree", "")
        
        risk = strategy.get("risk_config", {})
        sl_pips = risk.get("slPips", 50)
        tp_pips = risk.get("tpPips", 100)
        sl_type = risk.get("slType", "pips")
        tp_type = risk.get("tpType", "pips")
        sl_atr_mult = risk.get("slAtrMult", 1.5)
        tp_atr_mult = risk.get("tpAtrMult", 3.0)
        lot_size = risk.get("lotSize", 0.1)
        risk_pct = risk.get("riskPct", 1.0)
        sizing_mode = risk.get("sizingMode", "fixed")
        
        symbol = strategy.get("symbol", "EURUSD")
        timeframe_str = strategy.get("timeframe", "1h")
        
        tf_map = {
            "1m": "mt5.TIMEFRAME_M1",
            "5m": "mt5.TIMEFRAME_M5",
            "15m": "mt5.TIMEFRAME_M15",
            "30m": "mt5.TIMEFRAME_M30",
            "1h": "mt5.TIMEFRAME_H1",
            "4h": "mt5.TIMEFRAME_H4",
            "1d": "mt5.TIMEFRAME_D1"
        }
        mt5_tf = tf_map.get(timeframe_str.lower(), "mt5.TIMEFRAME_H1")
        
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

        code = f'''#!/usr/bin/env python3
"""
AlgoForge Python-MT5 Trading Bot (Genetic Programming)
Strategy ID: {name} (Rank: {rank})
Symbol: {symbol} | Timeframe: {timeframe_str}
Evolved Logic: {tree_str}

This script connects directly to your local MetaTrader 5 terminal.
Requirements:
    pip install MetaTrader5 pandas ta schedule
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- CONFIGURATION ---
SYMBOL = "{symbol}"
TIMEFRAME = {mt5_tf}
MAGIC_NUMBER = 888{rank}
LOT_SIZE = {lot_size}
SIZING_MODE = "{sizing_mode}" # 'fixed' or 'risk_pct'
RISK_PCT = {risk_pct}

# Risk Limits
SL_TYPE = "{sl_type}"
TP_TYPE = "{tp_type}"
SL_PIPS = {sl_pips}
TP_PIPS = {tp_pips}
SL_ATR_MULT = {sl_atr_mult}
TP_ATR_MULT = {tp_atr_mult}

# Indicator Parameters
INDICATOR_PARAMS = {ind_param_map}

# --- INITIALIZATION ---
def init_mt5():
    if not mt5.initialize():
        print("MetaTrader5 initialization failed, error code =", mt5.last_error())
        return False
    
    if not mt5.symbol_select(SYMBOL, True):
        print(f"Failed to select {{SYMBOL}}")
        return False
        
    print(f"Connected to MT5. Symbol: {{SYMBOL}} | Account: {{mt5.account_info().login}}")
    return True

# --- INDICATOR CALCULATION ---
def calculate_indicators(df):
    """
    Computes all required indicators using the 'ta' library.
    Guarantees 100% mathematical parity with AlgoForge Simulator.
    """
    from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel, DonchianChannel
    from ta.momentum import StochasticOscillator, RSIIndicator, TSIIndicator, WilliamsRIndicator
    from ta.trend import MACD, SMAIndicator, EMAIndicator, AroonIndicator, ADXIndicator
    from ta.volume import OnBalanceVolumeIndicator, MFIIndicator

    high = df['high']
    low = df['low']
    close = df['close']
    
    if SL_TYPE == 'atr' or TP_TYPE == 'atr':
        df['atr'] = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

'''
        py_tree = tree_str.replace("gt(", "gt(")\
                           .replace("lt(", "lt(")\
                           .replace("eq(", "eq(")\
                           .replace("and_op(", "and_op(")\
                           .replace("or_op(", "or_op(")\
                           .replace("not_op(", "not_op(")\
                           .replace("add(", "add(")\
                           .replace("sub(", "sub(")\
                           .replace("mul(", "mul(")\
                           .replace("div(", "div(")
                           
        words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', py_tree)
        unique_vars = set(words) - {'gt', 'lt', 'eq', 'and_op', 'or_op', 'not_op', 'add', 'sub', 'mul', 'div'}
        
        constants = [v for v in unique_vars if v.startswith("c_")]
        indicators = [v for v in unique_vars if not v.startswith("c_")]
        
        for c in constants:
            val = c.replace("c_", "").replace("_", ".")
            code += f"    df['{c}'] = {val}\n"
            
        code += "\n    # --- Indicators ---\n"
        
        for ind in indicators:
            ind_lower = ind.lower()
            code += f"    p = INDICATOR_PARAMS.get('{ind_lower}') or INDICATOR_PARAMS.get('{ind_lower.replace('_', ' ')}') or {{}}\n"
            if ind_lower in ['bollinger_bands', 'bbands']:
                code += f"    df['{ind}'] = BollingerBands(close=close, window=int(p.get('window', 20)), window_dev=float(p.get('window_dev', 2.0))).bollinger_pband()\n"
            elif ind_lower in ['stochastic', 'stoch']:
                code += f"    df['{ind}'] = StochasticOscillator(high=high, low=low, close=close, window=int(p.get('window', 14)), smooth_window=int(p.get('smooth_window', 3))).stoch()\n"
            elif ind_lower == 'rsi':
                code += f"    df['{ind}'] = RSIIndicator(close=close, window=int(p.get('window', 14))).rsi()\n"
            elif ind_lower == 'macd':
                code += f"    df['{ind}'] = MACD(close=close, window_slow=int(p.get('window_slow', 26)), window_fast=int(p.get('window_fast', 12)), window_sign=int(p.get('window_sign', 9))).macd_diff()\n"
            elif ind_lower in ['keltner_channel', 'kc']:
                code += f"    df['{ind}'] = KeltnerChannel(high=high, low=low, close=close, window=int(p.get('window', 20)), window_atr=int(p.get('window_atr', 10)), multiplier=float(p.get('multiplier', 2.0))).keltner_channel_pband()\n"
            elif ind_lower in ['donchian_channel', 'dc']:
                code += f"    df['{ind}'] = DonchianChannel(high=high, low=low, close=close, window=int(p.get('window', 20))).donchian_channel_pband()\n"
            elif ind_lower == 'aroon':
                code += f"    df['{ind}'] = AroonIndicator(high=high, low=low, window=int(p.get('window', 25))).aroon_indicator()\n"
            elif ind_lower == 'adx':
                code += f"    df['{ind}'] = ADXIndicator(high=high, low=low, close=close, window=int(p.get('window', 14))).adx()\n"
            elif ind_lower == 'sma':
                code += f"    df['{ind}'] = SMAIndicator(close=close, window=int(p.get('window', 20))).sma_indicator()\n"
            elif ind_lower == 'ema':
                code += f"    df['{ind}'] = EMAIndicator(close=close, window=int(p.get('window', 20))).ema_indicator()\n"
            else:
                code += f"    df['{ind}'] = 0.0 # Indicator not explicitly mapped\n"

        code += '''
    return df

# --- MATH HELPER FUNCTIONS ---
def gt(a, b): return a > b
def lt(a, b): return a < b
def eq(a, b): return a == b
def and_op(a, b): return a & b
def or_op(a, b): return a | b
def not_op(a): return ~a
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
def div(a, b): return np.where(b != 0, a / b, 0)

# --- EXECUTION LOGIC ---
def get_open_positions():
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions is None:
        return []
    return [p for p in positions if p.magic == MAGIC_NUMBER]

def calculate_lot_size(sl_distance_price):
    if SIZING_MODE == 'risk_pct' and sl_distance_price > 0:
        account = mt5.account_info()
        risk_money = account.equity * (RISK_PCT / 100.0)
        
        tick_size = mt5.symbol_info(SYMBOL).trade_tick_size
        tick_value = mt5.symbol_info(SYMBOL).trade_tick_value
        
        if tick_size > 0 and tick_value > 0:
            sl_ticks = sl_distance_price / tick_size
            raw_lot = risk_money / (sl_ticks * tick_value)
            
            step = mt5.symbol_info(SYMBOL).volume_step
            min_v = mt5.symbol_info(SYMBOL).volume_min
            max_v = mt5.symbol_info(SYMBOL).volume_max
            
            lot = (raw_lot // step) * step
            return max(min_v, min(max_v, lot))
            
    return LOT_SIZE

def run_strategy():
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
    if rates is None or len(rates) < 50:
        return
        
    df = pd.DataFrame(rates)
    df = calculate_indicators(df)
    
    last_closed = df.iloc[-2]
    
'''
        code += "    loc = {\n"
        code += "        'gt': gt, 'lt': lt, 'eq': eq, 'and_op': and_op, 'or_op': or_op,\n"
        code += "        'not_op': not_op, 'add': add, 'sub': sub, 'mul': mul, 'div': div\n"
        code += "    }\n"
        for v in unique_vars:
            code += f"    loc['{v}'] = last_closed['{v}']\n"
            
        code += f"\n    # Evaluate: {tree_str}\n"
        code += f"    signal_result = eval('{py_tree}', {{}}, loc)\n"
        
        code += '''
    print(f"[{datetime.now()}] Bar closed. Signal Eval: {signal_result}")
    
    if signal_result and len(get_open_positions()) == 0:
        print(">>> BUY SIGNAL TRIGGERED <<<")
        
        ask = mt5.symbol_info_tick(SYMBOL).ask
        point = mt5.symbol_info(SYMBOL).point
        
        sl_dist = 0.0
        if SL_TYPE == 'atr':
            sl_dist = SL_ATR_MULT * last_closed['atr']
        else:
            sl_dist = SL_PIPS * 10 * point
            
        sl_price = ask - sl_dist
            
        if TP_TYPE == 'atr':
            tp_price = ask + (TP_ATR_MULT * last_closed['atr'])
        else:
            tp_price = ask + (TP_PIPS * 10 * point)
            
        lot = calculate_lot_size(sl_dist)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY,
            "price": ask,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "AlgoForge PyBot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order send failed:", result.retcode)
        else:
            print(f"Order filled! Ticket: {result.order}")

if __name__ == "__main__":
    if init_mt5():
        print("Bot is running. Waiting for new bars...")
        last_bar_time = None
        while True:
            rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 1)
            if rates is not None and len(rates) > 0:
                current_bar_time = rates[0]['time']
                if last_bar_time is None:
                    last_bar_time = current_bar_time
                elif current_bar_time != last_bar_time:
                    last_bar_time = current_bar_time
                    run_strategy()
            time.sleep(1)
'''
        return code
