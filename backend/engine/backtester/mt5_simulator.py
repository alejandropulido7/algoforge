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
    exit_reason: str  # "sl", "tp", "signal", "time_exit"
    duration_bars: int
    sl_price: float = 0.0
    tp_price: float = 0.0

@dataclass
class PendingOrder:
    direction: str  # "buy_stop", "sell_stop", "buy_limit", "sell_limit"
    target_price: float
    created_bar: int
    sl_price: float
    tp_price: float
    lots: float

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
    trade_pnns: list[float] = field(default_factory=list)
    trade_pnls: list[float] = field(default_factory=list)
    trade_log: list[dict] = field(default_factory=list)

class MT5TradeSimulator:
    """Simulates exact bar-by-bar MetaTrader 5 execution with SL, TP, Pending Orders, Candle Timeouts, and Lots/Risk sizing."""

    def __init__(self, risk_config: dict | None = None):
        cfg = risk_config or {}
        self.max_simultaneous_trades = int(cfg.get("maxSimultaneousTrades") or cfg.get("max_simultaneous_trades") or 1)
        self.initial_deposit = float(cfg.get("initialDeposit", 10000.0))
        self.sizing_mode = cfg.get("sizingMode", "lots")  # "lots" | "risk_pct" | "cash"
        self.lot_size = float(cfg.get("lotSize", 0.1))
        self.risk_pct = float(cfg.get("riskPct", 1.0))
        self.direction = cfg.get("direction", "both")  # "both" | "long" | "short"
        
        # Order Execution & Timing Rules
        self.order_type = cfg.get("orderType") or cfg.get("order_type") or "market"  # "market" | "stop" | "limit" | "any"
        self.pending_timeout_bars = int(cfg.get("pendingTimeoutBars") or cfg.get("pending_timeout_bars") or 3)
        self.pending_offset_pips = float(cfg.get("pendingOffsetPips") or cfg.get("pending_offset_pips") or 5.0)
        self.max_holding_bars = int(cfg.get("maxHoldingBars") or cfg.get("max_holding_bars") or 0)

        # Stop Loss & Take Profit
        self.sl_type = cfg.get("slType", "pips")  # "pips" | "atr" | "none"
        self.sl_pips = float(cfg.get("slPips", 50.0))
        self.sl_atr_mult = float(cfg.get("slAtrMult", 1.5))
        
        self.tp_type = cfg.get("tpType", "pips")  # "pips" | "atr" | "none"
        self.tp_pips = float(cfg.get("tpPips", 100.0))
        self.tp_atr_mult = float(cfg.get("tpAtrMult", 3.0))

        # Consecutive Loss Management
        self.consec_loss_action = cfg.get("consecutiveLossAction") or cfg.get("consecutive_loss_action") or "none"
        self.consec_loss_threshold = int(cfg.get("consecutiveLossThreshold") or cfg.get("consecutive_loss_threshold") or 3)
        self.consec_loss_reduction_pct = float(cfg.get("consecutiveLossReductionPct") or cfg.get("consecutive_loss_reduction_pct") or 50.0)
        self.consec_loss_reactivation = cfg.get("consecutiveLossReactivation") or cfg.get("consecutive_loss_reactivation") or "none"
        self.consec_loss_cooldown_bars = int(cfg.get("consecutiveLossCooldownBars") or cfg.get("consecutive_loss_cooldown_bars") or 20)
        self.consec_loss_cooldown_days = int(cfg.get("consecutiveLossCooldownDays") or cfg.get("consecutive_loss_cooldown_days") or 1)
        self.consec_loss_auto_cooldown = bool(cfg.get("consecutiveLossAutoCooldown", True) if "consecutiveLossAutoCooldown" in cfg else cfg.get("consecutive_loss_auto_cooldown", True))

        self.contract_size = float(cfg.get("contractSize", 100000.0))
        self.point_size = float(cfg.get("pointSize", 0.0001))
        self.commission_per_lot = float(cfg.get("commissionPerLot", 7.0))
        # True: charge commission on BOTH entry and exit (MT5 broker behavior,
        # commission is applied per deal). False: single charge per round-trip.
        self.commission_per_side = bool(cfg.get("commissionPerSide", cfg.get("commission_per_side", True)))
        # Broker spread in pips. MT5 fills BUY orders at Ask and SELL orders at
        # Bid; the Python simulator fills at the bar Open (mid price), which
        # silently gives every trade the spread for free.
        self.spread_pips = float(cfg.get("spreadPips", cfg.get("spread_pips", 1.0)))
        # Overnight financing per lot per calendar day held (0 = no swap).
        self.swap_per_lot_per_day = float(cfg.get("swapPerLotPerDay", cfg.get("swap_per_lot_per_day", 0.0)))

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
            tr = np.maximum(highs - lows, np.abs(highs - np.roll(closes, 1)))
            atr_array = pd.Series(tr).rolling(14).mean().ffill().fillna(0.0).values

        # Bar timestamps for swap (overnight) accounting. Falls back to None
        # for non-datetime indexes (swap disabled).
        try:
            bar_dates = pd.to_datetime(df.index, errors="coerce")
            if not isinstance(bar_dates, pd.DatetimeIndex) or bar_dates.isna().all():
                bar_dates = None
        except Exception:
            bar_dates = None

        half_spread = self.spread_pips * self.point_size / 2.0

        balance = self.initial_deposit
        equity_curve = [balance]
        trades: list[TradeRecord] = []

        # Current position state
        active_positions = []
        pending_orders = []
        
        offset_dist = self.pending_offset_pips * self.point_size
        live_consec_losses = 0
        bot_stopped = False
        stopped_bar_idx = -1

        # Deferred execution state
        deferred_entries = [] # list of directions
        deferred_exit = False

        for i in range(1, n_bars):
            curr_open = opens[i]
            curr_high = highs[i]
            curr_low = lows[i]
            curr_close = closes[i]
            curr_atr = max(1e-6, atr_array[i])

            # Check Automatic Reactivation if bot was stopped by kill-switch
            if bot_stopped and stopped_bar_idx >= 0:
                reactivate = False
                bars_stopped = i - stopped_bar_idx

                if self.consec_loss_reactivation == "cooldown_bars":
                    target_bars = self.consec_loss_cooldown_bars if not self.consec_loss_auto_cooldown else max(10, self.consec_loss_threshold * 5)
                    if bars_stopped >= target_bars:
                        reactivate = True
                elif self.consec_loss_reactivation == "next_session":
                    if bars_stopped >= 12:
                        reactivate = True
                elif self.consec_loss_reactivation == "next_day":
                    if bars_stopped >= 24:
                        reactivate = True
                elif self.consec_loss_reactivation == "days_count":
                    if bars_stopped >= max(1, self.consec_loss_cooldown_days) * 24:
                        reactivate = True
                elif self.consec_loss_reactivation == "next_week":
                    if bars_stopped >= 120:
                        reactivate = True

                if reactivate:
                    bot_stopped = False
                    live_consec_losses = 0

            # =============================================================
            # Phase 1: Execute deferred SIGNAL EXIT at current bar's Open
            # =============================================================
            if deferred_exit and active_positions:
                for pos in active_positions:
                    # Market close: longs sell at Bid, shorts buy at Ask (MT5 fills).
                    if pos["dir"] == "buy":
                        exit_price = curr_open - half_spread
                    else:
                        exit_price = curr_open + half_spread
                    exit_reason = "signal"
                    bars_held = i - pos["entry_idx"]

                    if pos["dir"] == "buy":
                        price_diff = exit_price - pos["entry_price"]
                    else:
                        price_diff = pos["entry_price"] - exit_price

                    trade_pnl = self._close_pnl(pos, price_diff, bars_held, i, bar_dates)
                    pnl_pct = price_diff / (pos["entry_price"] + 1e-8)
                    balance += trade_pnl

                    if trade_pnl < 0:
                        live_consec_losses += 1
                        if self.consec_loss_action == "stop_bot" and live_consec_losses >= self.consec_loss_threshold:
                            bot_stopped = True
                            stopped_bar_idx = i
                    elif trade_pnl > 0:
                        live_consec_losses = 0

                    trades.append(TradeRecord(
                        entry_index=pos["entry_idx"], exit_index=i,
                        direction=pos["dir"], entry_price=pos["entry_price"],
                        exit_price=exit_price, sl_price=pos["sl"], tp_price=pos["tp"],
                        size=pos["lots"], pnl=trade_pnl, pnl_pct=pnl_pct,
                        exit_reason=exit_reason, duration_bars=bars_held
                    ))
                active_positions.clear()
                deferred_exit = False

            # =============================================================
            # Phase 2: Execute deferred MARKET ENTRY at current bar's Open
            # =============================================================
            # MT5 fills BUY at Ask / SELL at Bid; SL/TP and ATR sizing are
            # computed from the last CLOSED bar (bar i-1), not the forming bar.
            prev_atr = max(1e-6, atr_array[i - 1]) if i > 0 else curr_atr
            while deferred_entries:
                deferred_entry_dir = deferred_entries.pop(0)
                if len(active_positions) < self.max_simultaneous_trades:
                    if deferred_entry_dir == "buy":
                        pos_entry_price = curr_open + half_spread
                    else:
                        pos_entry_price = curr_open - half_spread
                    pos_sl, pos_tp = self._calc_sltp(deferred_entry_dir, pos_entry_price, prev_atr)
                    unrealized = self._floating_pnl(active_positions, curr_close)
                    pos_lots = self._calc_lots(balance + unrealized, pos_entry_price, pos_sl, live_consec_losses)
                    active_positions.append({
                        "dir": deferred_entry_dir,
                        "entry_price": pos_entry_price,
                        "entry_idx": i,
                        "sl": pos_sl,
                        "tp": pos_tp,
                        "lots": pos_lots,
                        "entry_cost": (pos_lots * self.commission_per_lot) if self.commission_per_side else 0.0
                    })

            # =============================================================
            # Phase 3: Intrabar SL / TP / Time Exit checks (realistic)
            # =============================================================
            for pos in active_positions[:]:
                closed = False
                exit_price = curr_close
                exit_reason = "signal"
                bars_held = i - pos["entry_idx"]

                if pos["dir"] == "buy":
                    if pos["sl"] > 0.0 and curr_low <= pos["sl"]:
                        exit_price = pos["sl"]
                        exit_reason = "sl"
                        closed = True
                    elif pos["tp"] > 0.0 and curr_high >= pos["tp"]:
                        exit_price = pos["tp"]
                        exit_reason = "tp"
                        closed = True
                    elif self.max_holding_bars > 0 and bars_held >= self.max_holding_bars:
                        exit_price = curr_close
                        exit_reason = "time_exit"
                        closed = True
                elif pos["dir"] == "sell":
                    if pos["sl"] > 0.0 and curr_high >= pos["sl"]:
                        exit_price = pos["sl"]
                        exit_reason = "sl"
                        closed = True
                    elif pos["tp"] > 0.0 and curr_low <= pos["tp"]:
                        exit_price = pos["tp"]
                        exit_reason = "tp"
                        closed = True
                    elif self.max_holding_bars > 0 and bars_held >= self.max_holding_bars:
                        exit_price = curr_close
                        exit_reason = "time_exit"
                        closed = True

                if closed:
                    if pos["dir"] == "buy":
                        price_diff = exit_price - pos["entry_price"]
                    else:
                        price_diff = pos["entry_price"] - exit_price

                    trade_pnl = self._close_pnl(pos, price_diff, bars_held, i, bar_dates)
                    pnl_pct = price_diff / (pos["entry_price"] + 1e-8)
                    balance += trade_pnl

                    if trade_pnl < 0:
                        live_consec_losses += 1
                        if self.consec_loss_action == "stop_bot" and live_consec_losses >= self.consec_loss_threshold:
                            bot_stopped = True
                            stopped_bar_idx = i
                    elif trade_pnl > 0:
                        live_consec_losses = 0

                    trades.append(TradeRecord(
                        entry_index=pos["entry_idx"], exit_index=i,
                        direction=pos["dir"], entry_price=pos["entry_price"],
                        exit_price=exit_price, sl_price=pos["sl"], tp_price=pos["tp"],
                        size=pos["lots"], pnl=trade_pnl, pnl_pct=pnl_pct,
                        exit_reason=exit_reason, duration_bars=bars_held
                    ))
                    active_positions.remove(pos)

            if len(active_positions) == 0:
                deferred_exit = False

            # =============================================================
            # Phase 4: Pending order execution
            # =============================================================
            for p_order in pending_orders[:]:
                bars_waiting = i - p_order.created_bar
                order_triggered = False
                exec_price = 0.0
                p_dir = ""

                if p_order.direction == "buy_stop":
                    if curr_high >= p_order.target_price:
                        order_triggered = True
                        exec_price = max(curr_open, p_order.target_price)
                        p_dir = "buy"
                elif p_order.direction == "sell_stop":
                    if curr_low <= p_order.target_price:
                        order_triggered = True
                        exec_price = min(curr_open, p_order.target_price)
                        p_dir = "sell"
                elif p_order.direction == "buy_limit":
                    if curr_low <= p_order.target_price:
                        order_triggered = True
                        exec_price = p_order.target_price
                        p_dir = "buy"
                elif p_order.direction == "sell_limit":
                    if curr_high >= p_order.target_price:
                        order_triggered = True
                        exec_price = p_order.target_price
                        p_dir = "sell"

                if order_triggered:
                    if len(active_positions) < self.max_simultaneous_trades:
                        active_positions.append({
                            "dir": p_dir,
                            "entry_price": exec_price,
                            "entry_idx": i,
                            "sl": p_order.sl_price,
                            "tp": p_order.tp_price,
                            "lots": p_order.lots,
                            "entry_cost": (p_order.lots * self.commission_per_lot) if self.commission_per_side else 0.0
                        })
                    pending_orders.remove(p_order)
                elif self.pending_timeout_bars > 0 and bars_waiting >= self.pending_timeout_bars:
                    pending_orders.remove(p_order)

            # =============================================================
            # Phase 5: Evaluate current bar signals
            # =============================================================
            if active_positions and not deferred_exit:
                has_buy = any(p["dir"] == "buy" for p in active_positions)
                has_sell = any(p["dir"] == "sell" for p in active_positions)
                if has_buy and sell_signals[i]:
                    deferred_exit = True
                elif has_sell and buy_signals[i]:
                    deferred_exit = True

            total_incoming = len(active_positions) + len(pending_orders) + len(deferred_entries)
            if total_incoming < self.max_simultaneous_trades and not bot_stopped:
                sizing_equity = balance + self._floating_pnl(active_positions, curr_close)
                if can_enter_buy[i]:
                    if self.order_type == "stop":
                        target_p = highs[i] + offset_dist
                        # MT5 places the pending order on the first tick of the
                        # NEXT bar, using the last CLOSED bar (i) for SL/TP/ATR.
                        sl_p, tp_p = self._calc_sltp("buy", target_p, curr_atr)
                        lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="buy_stop", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    elif self.order_type == "limit":
                        target_p = lows[i] - offset_dist
                        sl_p, tp_p = self._calc_sltp("buy", target_p, curr_atr)
                        lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="buy_limit", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    else:
                        deferred_entries.append("buy")

                elif can_enter_sell[i]:
                    if self.order_type == "stop":
                        target_p = lows[i] - offset_dist
                        sl_p, tp_p = self._calc_sltp("sell", target_p, curr_atr)
                        lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="sell_stop", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    elif self.order_type == "limit":
                        target_p = highs[i] + offset_dist
                        sl_p, tp_p = self._calc_sltp("sell", target_p, curr_atr)
                        lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="sell_limit", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    else:
                        deferred_entries.append("sell")

            # Record floating equity
            unrealized_pnl = self._floating_pnl(active_positions, curr_close)
            equity_curve.append(float(balance + unrealized_pnl))
        return self._compile_metrics(trades, equity_curve, df=df)

    def _floating_pnl(self, positions: list[dict], ref_price: float) -> float:
        """Unrealized PnL of open positions at ref_price (used for equity sizing)."""
        total = 0.0
        for pos in positions:
            if pos["dir"] == "buy":
                total += (ref_price - pos["entry_price"]) * self.contract_size * pos["lots"]
            else:
                total += (pos["entry_price"] - ref_price) * self.contract_size * pos["lots"]
        return total

    def _close_pnl(
        self,
        pos: dict,
        price_diff: float,
        bars_held: int,
        exit_idx: int,
        bar_dates: pd.DatetimeIndex | None
    ) -> float:
        """Round-trip PnL: gross price PnL minus entry commission (MT5 charges
        per deal), exit commission and overnight swap financing."""
        gross = price_diff * self.contract_size * pos["lots"]
        # Exit commission always applies; entry commission only in per-side mode.
        exit_commission = pos["lots"] * self.commission_per_lot
        swap_cost = 0.0
        if self.swap_per_lot_per_day != 0.0 and bar_dates is not None:
            entry_date = bar_dates[pos["entry_idx"]]
            exit_date = bar_dates[min(exit_idx, len(bar_dates) - 1)]
            if pd.notna(entry_date) and pd.notna(exit_date):
                days_held = (exit_date.normalize() - entry_date.normalize()).days
                swap_cost = days_held * self.swap_per_lot_per_day * pos["lots"]
        return gross - pos.get("entry_cost", 0.0) - exit_commission - swap_cost

    def _calc_sltp(self, direction: str, entry_price: float, atr_val: float) -> tuple[float, float]:
        sl_price = 0.0
        tp_price = 0.0

        if direction == "buy":
            if self.sl_type == "pips" and self.sl_pips > 0:
                sl_price = entry_price - (self.sl_pips * self.point_size)
            elif self.sl_type == "atr" and self.sl_atr_mult > 0:
                sl_price = entry_price - (self.sl_atr_mult * atr_val)

            if self.tp_type == "pips" and self.tp_pips > 0:
                tp_price = entry_price + (self.tp_pips * self.point_size)
            elif self.tp_type == "atr" and self.tp_atr_mult > 0:
                tp_price = entry_price + (self.tp_atr_mult * atr_val)
        else:
            if self.sl_type == "pips" and self.sl_pips > 0:
                sl_price = entry_price + (self.sl_pips * self.point_size)
            elif self.sl_type == "atr" and self.sl_atr_mult > 0:
                sl_price = entry_price + (self.sl_atr_mult * atr_val)

            if self.tp_type == "pips" and self.tp_pips > 0:
                tp_price = entry_price - (self.tp_pips * self.point_size)
            elif self.tp_type == "atr" and self.tp_atr_mult > 0:
                tp_price = entry_price - (self.tp_atr_mult * atr_val)

        return sl_price, tp_price

    def _calc_lots(self, balance: float, entry_price: float, sl_price: float, live_consec_losses: int = 0) -> float:
        lots = self.lot_size
        if self.sizing_mode == "lots":
            lots = max(0.01, round(self.lot_size, 2))
        elif self.sizing_mode == "risk_pct":
            sl_dist = abs(entry_price - sl_price) if sl_price > 0 else (entry_price * 0.01)
            risk_cash = balance * (self.risk_pct / 100.0)
            calculated_lots = risk_cash / (max(1e-6, sl_dist) * self.contract_size)
            lots = max(0.01, round(min(100.0, calculated_lots), 2))
        elif self.sizing_mode == "cash":
            calculated_lots = self.lot_size / (entry_price * self.contract_size + 1e-8)
            lots = max(0.01, round(calculated_lots, 2))

        # Dynamic risk reduction on consecutive loss streak
        if self.consec_loss_action == "reduce_risk" and live_consec_losses >= self.consec_loss_threshold:
            factor = max(0.1, 1.0 - (self.consec_loss_reduction_pct / 100.0))
            lots = max(0.01, round(lots * factor, 2))

        return lots

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

        if df is not None and 'Timestamp' in df.columns:
            timestamps = [str(ts) for ts in df['Timestamp'].values]
        elif df is not None and hasattr(df, "index"):
            timestamps = [str(ts) for ts in df.index]
        else:
            timestamps = [f"Bar {k}" for k in range(len(equity_curve))]

        trade_log = [
            {
                "trade_idx": idx + 1,
                "direction": t.direction,
                "entry_time": timestamps[t.entry_index] if t.entry_index < len(timestamps) else "",
                "exit_time": timestamps[t.exit_index] if t.exit_index < len(timestamps) else "",
                "entry_price": round(t.entry_price, 5),
                "exit_price": round(t.exit_price, 5),
                "sl_price": round(t.sl_price, 5) if t.sl_price > 0 else None,
                "tp_price": round(t.tp_price, 5) if t.tp_price > 0 else None,
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
