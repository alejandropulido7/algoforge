class PythonLiveExporter:
    """Generate standalone, turnkey Python live trading script connecting directly to MT5."""

    def export(self, strategy: dict) -> str:
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
    
    # Ensure symbol is visible in Market Watch
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
    """Run model inference on recent bars. Returns 1 for Buy, 2 for Sell, 0 for Hold."""
    if len(df) < WINDOW_SIZE:
        return 0

    if session is not None and HAS_ONNX:
        # Extract features [1, WINDOW_SIZE, 5]
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
        # Heuristic fallback if running without onnx runtime
        close = df['Close'].values
        sma_fast = np.mean(close[-10:])
        sma_slow = np.mean(close[-30:])
        if sma_fast > sma_slow:
            return 1
        elif sma_fast < sma_slow:
            return 2
        return 0

def execute_trade(action: int, symbol: str):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return

    point = symbol_info.point
    ask = symbol_info.ask
    bid = symbol_info.bid

    # Check existing open position for this EA
    positions = mt5.positions_get(symbol=symbol)
    has_pos = False
    if positions:
        for pos in positions:
            if pos.magic == MAGIC_NUMBER:
                has_pos = True
                # Close long on sell signal
                if pos.type == mt5.ORDER_TYPE_BUY and action == 2:
                    close_req = {{
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": pos.volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "position": pos.ticket,
                        "price": bid,
                        "magic": MAGIC_NUMBER,
                        "comment": "AlgoForge RL Close Long",
                    }}
                    mt5.order_send(close_req)
                    has_pos = False
                # Close short on buy signal
                elif pos.type == mt5.ORDER_TYPE_SELL and action == 1:
                    close_req = {{
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": pos.volume,
                        "type": mt5.ORDER_TYPE_BUY,
                        "position": pos.ticket,
                        "price": ask,
                        "magic": MAGIC_NUMBER,
                        "comment": "AlgoForge RL Close Short",
                    }}
                    mt5.order_send(close_req)
                    has_pos = False

    if not has_pos:
        if action == 1:  # Buy
            sl = ask - (STOP_LOSS_PIPS * 10 * point) if STOP_LOSS_PIPS > 0 else 0.0
            tp = ask + (TAKE_PROFIT_PIPS * 10 * point) if TAKE_PROFIT_PIPS > 0 else 0.0
            request = {{
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": LOT_SIZE,
                "type": mt5.ORDER_TYPE_BUY,
                "price": ask,
                "sl": sl,
                "tp": tp,
                "magic": MAGIC_NUMBER,
                "comment": "AlgoForge RL Buy Order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }}
            res = mt5.order_send(request)
            print(f"[BUY EXECUTED]: Price={{ask}}, SL={{sl}}, TP={{tp}}, Result={{res.comment}}")

        elif action == 2:  # Sell
            sl = bid + (STOP_LOSS_PIPS * 10 * point) if STOP_LOSS_PIPS > 0 else 0.0
            tp = bid - (TAKE_PROFIT_PIPS * 10 * point) if TAKE_PROFIT_PIPS > 0 else 0.0
            request = {{
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": LOT_SIZE,
                "type": mt5.ORDER_TYPE_SELL,
                "price": bid,
                "sl": sl,
                "tp": tp,
                "magic": MAGIC_NUMBER,
                "comment": "AlgoForge RL Sell Order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }}
            res = mt5.order_send(request)
            print(f"[SELL EXECUTED]: Price={{bid}}, SL={{sl}}, TP={{tp}}, Result={{res.comment}}")

def main():
    if not initialize_mt5():
        return

    # Load ONNX session if available
    session = None
    if HAS_ONNX:
        try:
            session = ort.InferenceSession(MODEL_PATH)
            print(f"Loaded ONNX model: {{MODEL_PATH}}")
        except Exception as e:
            print(f"Notice: ONNX model not loaded, running in heuristic mode: {{e}}")

    print(f"Starting live monitoring loop for {{SYMBOL}}...")
    last_bar_time = None

    try:
        while True:
            df = fetch_recent_bars(SYMBOL, TIMEFRAME, 50)
            if not df.empty:
                curr_bar_time = df['time'].iloc[-1]
                if curr_bar_time != last_bar_time:
                    last_bar_time = curr_bar_time
                    action = predict_signal(df, session)
                    print(f"[BAR {{curr_bar_time}}] Model Action: {{action}} (0=Hold, 1=Buy, 2=Sell)")
                    execute_trade(action, SYMBOL)
            
            time.sleep(5)  # Poll every 5 seconds
    except KeyboardInterrupt:
        print("Stopping AlgoForge Live Trader...")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
'''
