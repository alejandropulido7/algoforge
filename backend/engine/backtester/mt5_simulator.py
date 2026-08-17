import numpy as np
import pandas as pd
from dataclasses import dataclass, field

@dataclass
class TradeRecord:
    entry_index: int
    exit_index: int
    direction: str  # "buy" or "sell"
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_pct: float
    exit_reason: str  # "sl", "tp", "signal"
    duration_bars: int

@dataclass
class MT5SimulationResult:
    initial_deposit: float = 10000.0
    total_net_profit: float = 0.0
    total_return_pct: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    profit_trades: int = 0
    loss_trades: int = 0
    max_drawdown_pct: float = 0.0
    max_drawdown_cash: float = 0.0
    sharpe_ratio: float = 0.0
    recovery_factor: float = 0.0
    consecutive_wins_max: int = 0
    consecutive_wins_max_cash: float = 0.0
    consecutive_losses_max: int = 0
    consecutive_losses_max_cash: float = 0.0
    consecutive_wins_avg: float = 0.0
    consecutive_losses_avg: float = 0.0
    equity_curve: list[float] = field(default_factory=list)
    trade_pnls: list[float] = field(default_factory=list)
    trade_log: list[dict] = field(default_factory=list)

class MT5TradeSimulator:
    """Simulates exact bar-by-bar MetaTrader 5 execution with SL, TP, Lots/Risk sizing."""

    def __init__(self, risk_config: dict | None = None):
        cfg = risk_config or {}
        self.initial_deposit = float(cfg.get("initialDeposit", 10000.0))
        self.sizing_mode = cfg.get("sizingMode", "lots")  # "lots" | "risk_pct" | "cash"
        self.lot_size = float(cfg.get("lotSize", 0.1))
        self.risk_pct = float(cfg.get("riskPct", 1.0))
        self.direction = cfg.get("direction", "both")  # "both" | "long" | "short"
        
        self.sl_type = cfg.get("slType", "pips")  # "pips" | "atr" | "none"
        self.sl_pips = float(cfg.get("slPips", 50.0))
        self.sl_atr_mult = float(cfg.get("slAtrMult", 1.5))
        
        self.tp_type = cfg.get("tpType", "pips")  # "pips" | "atr" | "none"
        self.tp_pips = float(cfg.get("tpPips", 100.0))
        self.tp_atr_mult = float(cfg.get("tpAtrMult", 3.0))

        self.contract_size = float(cfg.get("contractSize", 100000.0))
        self.point_size = float(cfg.get("pointSize", 0.0001))
        self.commission_per_lot = float(cfg.get("commissionPerLot", 7.0))  # $7 per round lot

    def simulate(
        self,
        df: pd.DataFrame,
        buy_signals: np.ndarray,
        sell_signals: np.ndarray,
        atr_array: np.ndarray | None = None
    ) -> MT5SimulationResult:
        n_bars = len(df)
        if n_bars < 2:
            return MT5SimulationResult(initial_deposit=self.initial_deposit, equity_curve=[self.initial_deposit])

        # Filter entry signals by configured trade direction
        if self.direction == "long":
            can_enter_buy = buy_signals
            can_enter_sell = np.zeros(n_bars, dtype=bool)
        elif self.direction == "short":
            can_enter_buy = np.zeros(n_bars, dtype=bool)
            can_enter_sell = sell_signals
        else:
            can_enter_buy = buy_signals
            can_enter_sell = sell_signals

        opens = df['Open'].values if 'Open' in df.columns else df.iloc[:, 0].values
        highs = df['High'].values if 'High' in df.columns else df.iloc[:, 0].values
        lows = df['Low'].values if 'Low' in df.columns else df.iloc[:, 0].values
        closes = df['Close'].values if 'Close' in df.columns else df.iloc[:, 0].values

        if atr_array is None or len(atr_array) != n_bars:
            # Fallback simple true range
            tr = np.maximum(highs - lows, np.abs(highs - np.roll(closes, 1)))
            atr_array = pd.Series(tr).rolling(14).mean().bfill().values

        balance = self.initial_deposit
        equity = self.initial_deposit
        equity_curve = [balance]
        trades: list[TradeRecord] = []

        # Current open position state
        in_position = False
        pos_dir = ""  # "buy" or "sell"
        pos_entry_price = 0.0
        pos_entry_idx = 0
        pos_lots = 0.0
        pos_sl = 0.0
        pos_tp = 0.0

        for i in range(1, n_bars):
            curr_open = opens[i]
            curr_high = highs[i]
            curr_low = lows[i]
            curr_close = closes[i]
            curr_atr = max(1e-6, atr_array[i])

            # 1. If in position, check SL / TP hits first during the current bar
            if in_position:
                closed = False
                exit_price = curr_close
                exit_reason = "signal"

                if pos_dir == "buy":
                    # Check SL hit
                    if pos_sl > 0.0 and curr_low <= pos_sl:
                        exit_price = pos_sl
                        exit_reason = "sl"
                        closed = True
                    # Check TP hit
                    elif pos_tp > 0.0 and curr_high >= pos_tp:
                        exit_price = pos_tp
                        exit_reason = "tp"
                        closed = True
                    # Check reverse signal
                    elif sell_signals[i]:
                        exit_price = curr_open
                        exit_reason = "signal"
                        closed = True

                    if closed:
                        price_diff = exit_price - pos_entry_price
                        trade_pnl = (price_diff * self.contract_size * pos_lots) - (pos_lots * self.commission_per_lot)
                        pnl_pct = price_diff / (pos_entry_price + 1e-8)
                        balance += trade_pnl
                        trades.append(TradeRecord(
                            entry_index=pos_entry_idx,
                            exit_index=i,
                            direction="buy",
                            entry_price=pos_entry_price,
                            exit_price=exit_price,
                            size=pos_lots,
                            pnl=trade_pnl,
                            pnl_pct=pnl_pct,
                            exit_reason=exit_reason,
                            duration_bars=i - pos_entry_idx
                        ))
                        in_position = False

                elif pos_dir == "sell":
                    # Check SL hit for short
                    if pos_sl > 0.0 and curr_high >= pos_sl:
                        exit_price = pos_sl
                        exit_reason = "sl"
                        closed = True
                    # Check TP hit for short
                    elif pos_tp > 0.0 and curr_low <= pos_tp:
                        exit_price = pos_tp
                        exit_reason = "tp"
                        closed = True
                    # Check reverse signal
                    elif buy_signals[i]:
                        exit_price = curr_open
                        exit_reason = "signal"
                        closed = True

                    if closed:
                        price_diff = pos_entry_price - exit_price
                        trade_pnl = (price_diff * self.contract_size * pos_lots) - (pos_lots * self.commission_per_lot)
                        pnl_pct = price_diff / (pos_entry_price + 1e-8)
                        balance += trade_pnl
                        trades.append(TradeRecord(
                            entry_index=pos_entry_idx,
                            exit_index=i,
                            direction="sell",
                            entry_price=pos_entry_price,
                            exit_price=exit_price,
                            size=pos_lots,
                            pnl=trade_pnl,
                            pnl_pct=pnl_pct,
                            exit_reason=exit_reason,
                            duration_bars=i - pos_entry_idx
                        ))
                        in_position = False

            # 2. Check for new order entry if flat
            if not in_position:
                if can_enter_buy[i]:
                    in_position = True
                    pos_dir = "buy"
                    pos_entry_price = curr_close
                    pos_entry_idx = i

                    # Calculate SL
                    if self.sl_type == "pips" and self.sl_pips > 0:
                        pos_sl = pos_entry_price - (self.sl_pips * self.point_size)
                    elif self.sl_type == "atr" and self.sl_atr_mult > 0:
                        pos_sl = pos_entry_price - (self.sl_atr_mult * curr_atr)
                    else:
                        pos_sl = 0.0

                    # Calculate TP
                    if self.tp_type == "pips" and self.tp_pips > 0:
                        pos_tp = pos_entry_price + (self.tp_pips * self.point_size)
                    elif self.tp_type == "atr" and self.tp_atr_mult > 0:
                        pos_tp = pos_entry_price + (self.tp_atr_mult * curr_atr)
                    else:
                        pos_tp = 0.0

                    # Position sizing
                    pos_lots = self._calc_lots(balance, pos_entry_price, pos_sl)

                elif can_enter_sell[i]:
                    in_position = True
                    pos_dir = "sell"
                    pos_entry_price = curr_close
                    pos_entry_idx = i

                    # Calculate SL
                    if self.sl_type == "pips" and self.sl_pips > 0:
                        pos_sl = pos_entry_price + (self.sl_pips * self.point_size)
                    elif self.sl_type == "atr" and self.sl_atr_mult > 0:
                        pos_sl = pos_entry_price + (self.sl_atr_mult * curr_atr)
                    else:
                        pos_sl = 0.0

                    # Calculate TP
                    if self.tp_type == "pips" and self.tp_pips > 0:
                        pos_tp = pos_entry_price - (self.tp_pips * self.point_size)
                    elif self.tp_type == "atr" and self.tp_atr_mult > 0:
                        pos_tp = pos_entry_price - (self.tp_atr_mult * curr_atr)
                    else:
                        pos_tp = 0.0

                    pos_lots = self._calc_lots(balance, pos_entry_price, pos_sl)

            # Record floating equity
            unrealized_pnl = 0.0
            if in_position:
                if pos_dir == "buy":
                    unrealized_pnl = (curr_close - pos_entry_price) * self.contract_size * pos_lots
                else:
                    unrealized_pnl = (pos_entry_price - curr_close) * self.contract_size * pos_lots
            
            equity_curve.append(float(balance + unrealized_pnl))

        # Compile comprehensive metrics matching MT5 Strategy Tester
        return self._compile_metrics(trades, equity_curve, df=df)

    def _calc_lots(self, balance: float, entry_price: float, sl_price: float) -> float:
        if self.sizing_mode == "lots":
            return max(0.01, round(self.lot_size, 2))
        elif self.sizing_mode == "risk_pct":
            sl_dist = abs(entry_price - sl_price) if sl_price > 0 else (entry_price * 0.01)
            risk_cash = balance * (self.risk_pct / 100.0)
            lots = risk_cash / (max(1e-6, sl_dist) * self.contract_size)
            return max(0.01, round(min(100.0, lots), 2))
        elif self.sizing_mode == "cash":
            lots = self.lot_size / (entry_price * self.contract_size + 1e-8)
            return max(0.01, round(lots, 2))
        return max(0.01, round(self.lot_size, 2))

    def _compile_metrics(
        self, 
        trades: list[TradeRecord], 
        equity_curve: list[float],
        df: pd.DataFrame | None = None
    ) -> MT5SimulationResult:
        n_trades = len(trades)
        pnls = [t.pnl for t in trades]

        if n_trades == 0:
            return MT5SimulationResult(
                initial_deposit=self.initial_deposit,
                equity_curve=equity_curve,
                trade_pnls=[]
            )

        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        net_profit = sum(pnls)
        profit_trades = sum(1 for p in pnls if p > 0)
        loss_trades = sum(1 for p in pnls if p < 0)
        win_rate = (profit_trades / n_trades) * 100.0 if n_trades > 0 else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        expected_payoff = net_profit / n_trades if n_trades > 0 else 0.0
        total_return_pct = (net_profit / self.initial_deposit) * 100.0

        # Drawdown calculation
        eq_arr = np.array(equity_curve)
        peak = np.maximum.accumulate(eq_arr)
        dd_cash = peak - eq_arr
        max_dd_cash = float(np.max(dd_cash)) if len(dd_cash) > 0 else 0.0
        dd_pct = dd_cash / (peak + 1e-8)
        max_dd_pct = float(np.max(dd_pct) * 100.0) if len(dd_pct) > 0 else 0.0

        # Sharpe ratio
        pnl_arr = np.array(pnls)
        mean_pnl = np.mean(pnl_arr) if len(pnl_arr) > 0 else 0.0
        std_pnl = np.std(pnl_arr) + 1e-8
        sharpe = (mean_pnl / std_pnl) * np.sqrt(min(252, n_trades)) if len(pnl_arr) > 1 else 0.0

        # Recovery factor
        recovery_factor = (net_profit / max_dd_cash) if max_dd_cash > 0 else (99.0 if net_profit > 0 else 0.0)

        # Consecutive Wins & Losses Analysis
        curr_wins = 0
        curr_win_cash = 0.0
        max_wins = 0
        max_win_cash = 0.0
        win_streaks = []

        curr_losses = 0
        curr_loss_cash = 0.0
        max_losses = 0
        max_loss_cash = 0.0
        loss_streaks = []

        for p in pnls:
            if p > 0:
                curr_wins += 1
                curr_win_cash += p
                if curr_losses > 0:
                    loss_streaks.append(curr_losses)
                    curr_losses = 0
                    curr_loss_cash = 0.0
                if curr_wins > max_wins:
                    max_wins = curr_wins
                if curr_win_cash > max_win_cash:
                    max_win_cash = curr_win_cash
            elif p < 0:
                curr_losses += 1
                curr_loss_cash += abs(p)
                if curr_wins > 0:
                    win_streaks.append(curr_wins)
                    curr_wins = 0
                    curr_win_cash = 0.0
                if curr_losses > max_losses:
                    max_losses = curr_losses
                if curr_loss_cash > max_loss_cash:
                    max_loss_cash = curr_loss_cash

        if curr_wins > 0:
            win_streaks.append(curr_wins)
        if curr_losses > 0:
            loss_streaks.append(curr_losses)

        avg_wins = float(np.mean(win_streaks)) if win_streaks else 0.0
        avg_losses = float(np.mean(loss_streaks)) if loss_streaks else 0.0

        if 'Timestamp' in df.columns:
            timestamps = [str(ts) for ts in df['Timestamp'].values]
        elif hasattr(df, "index"):
            timestamps = [str(ts) for ts in df.index]
        else:
            timestamps = [f"Bar {k}" for k in range(n_bars)]

        trade_log = [
            {
                "trade_idx": idx + 1,
                "direction": t.direction,
                "entry_time": timestamps[t.entry_index] if t.entry_index < len(timestamps) else "",
                "exit_time": timestamps[t.exit_index] if t.exit_index < len(timestamps) else "",
                "entry_price": round(t.entry_price, 5),
                "exit_price": round(t.exit_price, 5),
                "size": t.size,
                "pnl": round(t.pnl, 2),
                "pnl_pct": round(t.pnl_pct * 100.0, 2),
                "exit_reason": t.exit_reason,
                "duration_bars": t.duration_bars
            }
            for idx, t in enumerate(trades)
        ]

        return MT5SimulationResult(
            initial_deposit=self.initial_deposit,
            total_net_profit=round(net_profit, 2),
            total_return_pct=round(total_return_pct, 2),
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
            profit_factor=round(profit_factor, 2),
            expected_payoff=round(expected_payoff, 2),
            win_rate=round(win_rate, 2),
            total_trades=n_trades,
            profit_trades=profit_trades,
            loss_trades=loss_trades,
            max_drawdown_pct=round(max_dd_pct, 2),
            max_drawdown_cash=round(max_dd_cash, 2),
            sharpe_ratio=round(float(sharpe), 2),
            recovery_factor=round(float(recovery_factor), 2),
            consecutive_wins_max=max_wins,
            consecutive_wins_max_cash=round(max_win_cash, 2),
            consecutive_losses_max=max_losses,
            consecutive_losses_max_cash=round(max_loss_cash, 2),
            consecutive_wins_avg=round(avg_wins, 1),
            consecutive_losses_avg=round(avg_losses, 1),
            equity_curve=[round(x, 2) for x in equity_curve],
            trade_pnls=[round(x, 2) for x in pnls],
            trade_log=trade_log
        )
