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

def get_symbol_contract_specs(symbol: str = "", price: float = 0.0) -> tuple[float, float, float]:
    """
    Auto-detects (contract_size, point_size, default_spread_pips) matching MetaTrader 5 broker specifications.
    """
    sym = str(symbol or "").upper().replace("-", "").replace("/", "").replace("_", "").replace("=", "").replace("^", "")

    # 1. Crypto (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, etc. or suffixes USD/USDT/BUSD with crypto keys)
    crypto_keys = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "DOT", "MATIC", "LINK", "LTC", "NEAR", "ATOM", "SHIB", "UNI"]
    if any(k in sym for k in crypto_keys) or "CRYPTO" in sym or sym.endswith("USDT") or sym.endswith("BUSD"):
        # For crypto, 1 standard lot = 1.0 unit (1 BTC / 1 ETH)
        return 1.0, 0.01, 1.0

    # 2. Precious Metals (Gold, Silver)
    if "XAU" in sym or "GOLD" in sym:
        return 100.0, 0.01, 2.0  # 1 lot = 100 oz
    if "XAG" in sym or "SILVER" in sym:
        return 5000.0, 0.001, 2.0  # 1 lot = 5000 oz

    # 3. Stock Indices (US30, NAS100, SPX500, GER40, etc.)
    if any(k in sym for k in ["US30", "DJI", "NAS", "NDX", "100", "SPX", "500", "GER", "DAX", "UK100", "JP225", "N225"]):
        return 1.0, 1.0, 1.0

    # 4. Commodities / Energy (OIL, WTI, BRENT, NGAS)
    if any(k in sym for k in ["OIL", "WTI", "BRENT"]):
        return 1000.0, 0.01, 3.0

    # 5. Price heuristic if symbol string is generic (e.g. user uploaded custom CSV):
    if price > 500.0:
        # Asset price is over $500 (like BTC, ETH, SPX, or US30). In CFDs / MT5, contract_size = 1.0.
        return 1.0, 0.01, 1.0

    # 6. Forex Standard
    if any(k in sym for k in ["JPY", "HUF", "CZK"]):
        return 100000.0, 0.001, 1.5
    return 100000.0, 0.0001, 1.0

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
        self.symbol = str(cfg.get("symbol") or cfg.get("dataSource", {}).get("symbol") or "").upper()
        self.max_simultaneous_trades = int(cfg.get("maxSimultaneousTrades") or cfg.get("max_simultaneous_trades") or 1)
        self.initial_deposit = float(cfg.get("initialDeposit") or cfg.get("initial_deposit") or 10000.0)
        self.sizing_mode = cfg.get("sizingMode") or cfg.get("sizing_mode") or "lots"  # "lots" | "risk_pct" | "cash"
        self.lot_size = float(cfg.get("lotSize") or cfg.get("lot_size") or 0.1)
        self.risk_pct = float(cfg.get("riskPct") or cfg.get("risk_pct") or 1.0)
        self.risk_base = cfg.get("riskBase") or cfg.get("risk_base") or "initial_deposit"  # "initial_deposit" | "balance"
        self.direction = cfg.get("direction", "both")  # "both" | "long" | "short"
        
        # Order Execution & Timing Rules
        self.order_type = cfg.get("orderType") or cfg.get("order_type") or "market"  # "market" | "stop" | "limit" | "any"
        self.pending_timeout_bars = int(cfg.get("pendingTimeoutBars") or cfg.get("pending_timeout_bars") or 3)
        self.pending_offset_pips = float(cfg.get("pendingOffsetPips") or cfg.get("pending_offset_pips") or 5.0)
        self.max_holding_bars = int(cfg.get("maxHoldingBars") or cfg.get("max_holding_bars") or 0)

        # Stop Loss & Take Profit (Standard & Extended from TP/SL Management)
        self.sl_type = cfg.get("slType", "none")  # "pips" | "atr" | "pct" | "none"
        self.sl_pips = float(cfg.get("slPips") or cfg.get("sl_pips") or 0.0)
        self.sl_atr_mult = float(cfg.get("slAtrMult") or cfg.get("sl_atr_mult") or cfg.get("sl_atr") or (1.5 if self.sl_type == "atr" else 0.0))
        
        self.tp_type = cfg.get("tpType", "none")  # "pips" | "atr" | "pct" | "none"
        self.tp_pips = float(cfg.get("tpPips") or cfg.get("tp_pips") or 0.0)
        self.tp_atr_mult = float(cfg.get("tpAtrMult") or cfg.get("tp_atr_mult") or cfg.get("tp_atr") or (3.0 if self.tp_type == "atr" else 0.0))

        # Advanced TP/SL Management Modes
        self.trailing_stop_atr = float(cfg.get("trailingStopAtr") or cfg.get("trailing_stop_atr") or cfg.get("trail_atr") or 0.0)
        self.breakeven_atr = float(cfg.get("breakevenAtr") or cfg.get("breakeven_atr") or cfg.get("be_atr") or 0.0)
        self.swing_lookback = int(cfg.get("swingLookback") or cfg.get("swing_lookback") or cfg.get("lookback") or 0)
        self.sl_pct = float(cfg.get("slPct") or cfg.get("sl_pct") or 0.0)
        self.tp_pct = float(cfg.get("tpPct") or cfg.get("tp_pct") or 0.0)
        self.partial_tp1_atr = float(cfg.get("partialTp1Atr") or cfg.get("partial_tp1_atr") or cfg.get("tp1_atr") or 0.0)
        self.partial_tp2_atr = float(cfg.get("partialTp2Atr") or cfg.get("partial_tp2_atr") or cfg.get("tp2_atr") or 0.0)
        self.partial_close_pct = float(cfg.get("partialClosePct") or cfg.get("partial_close_pct") or cfg.get("close_pct") or 50.0)
        self.smoothed_sl_atr = float(cfg.get("smoothedSlAtr") or cfg.get("smoothed_sl_atr") or cfg.get("sl_atr_smooth") or 0.0)
        self.smoothed_tp_atr = float(cfg.get("smoothedTpAtr") or cfg.get("smoothed_tp_atr") or cfg.get("tp_atr_smooth") or 0.0)

        # Consecutive Loss Management
        self.consec_loss_action = cfg.get("consecutiveLossAction") or cfg.get("consecutive_loss_action") or "none"
        self.consec_loss_threshold = int(cfg.get("consecutiveLossThreshold") or cfg.get("consecutive_loss_threshold") or 3)
        self.consec_loss_reduction_pct = float(cfg.get("consecutiveLossReductionPct") or cfg.get("consecutive_loss_reduction_pct") or 50.0)
        self.consec_loss_reactivation = cfg.get("consecutiveLossReactivation") or cfg.get("consecutive_loss_reactivation") or "none"
        self.consec_loss_cooldown_bars = int(cfg.get("consecutiveLossCooldownBars") or cfg.get("consecutive_loss_cooldown_bars") or 20)
        self.consec_loss_cooldown_days = int(cfg.get("consecutiveLossCooldownDays") or cfg.get("consecutive_loss_cooldown_days") or 1)
        self.consec_loss_auto_cooldown = bool(cfg.get("consecutiveLossAutoCooldown", True) if "consecutiveLossAutoCooldown" in cfg else cfg.get("consecutive_loss_auto_cooldown", True))

        # Contract Specifications
        self.has_custom_contract_size = ("contractSize" in cfg or "contract_size" in cfg)
        self.has_custom_point_size = ("pointSize" in cfg or "point_size" in cfg)
        spec_c, spec_p, spec_sp = get_symbol_contract_specs(self.symbol)
        self.contract_size = float(cfg.get("contractSize") or cfg.get("contract_size") or spec_c)
        self.point_size = float(cfg.get("pointSize") or cfg.get("point_size") or spec_p)
        self.commission_per_lot = float(cfg.get("commissionPerLot", 7.0))
        self.commission_per_side = bool(cfg.get("commissionPerSide", cfg.get("commission_per_side", True)))
        self.spread_pips = float(cfg.get("spreadPips", cfg.get("spread_pips", spec_sp)))
        self.swap_per_lot_per_day = float(cfg.get("swapPerLotPerDay", cfg.get("swap_per_lot_per_day", 0.0)))
        self.fill_mode = str(cfg.get("fillMode") or cfg.get("fill_mode") or "intrabar").lower()

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

        # Auto-calibrate contract specifications based on price & symbol if not explicitly provided
        ref_price = float(closes[0]) if len(closes) > 0 else 1.0
        spec_c, spec_p, spec_sp = get_symbol_contract_specs(self.symbol, ref_price)
        if not self.has_custom_contract_size:
            self.contract_size = spec_c
        if not self.has_custom_point_size:
            self.point_size = spec_p

        if atr_array is None or len(atr_array) != n_bars:
            prev_close = np.roll(closes, 1)
            prev_close[0] = opens[0]
            tr = np.maximum(highs - lows, np.abs(highs - prev_close))
            tr = np.maximum(tr, np.abs(lows - prev_close))
            w = 14
            atr_array = np.zeros(n_bars)
            if n_bars > w:
                atr_array[w - 1] = tr[0:w].mean()
                for idx in range(w, n_bars):
                    atr_array[idx] = (atr_array[idx - 1] * (w - 1) + tr[idx]) / w

        # Calculate 50-period ATR if smoothed ATR mode is active
        atr50_array = np.zeros(n_bars)
        if self.smoothed_sl_atr > 0 or self.smoothed_tp_atr > 0:
            prev_close = np.roll(closes, 1)
            prev_close[0] = opens[0]
            tr = np.maximum(highs - lows, np.abs(highs - prev_close))
            tr = np.maximum(tr, np.abs(lows - prev_close))
            w50 = 50
            if n_bars > w50:
                atr50_array[w50 - 1] = tr[0:w50].mean()
                for idx in range(w50, n_bars):
                    atr50_array[idx] = (atr50_array[idx - 1] * (w50 - 1) + tr[idx]) / w50

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
        account_ruined = False
        stopped_bar_idx = -1

        # Deferred execution state
        deferred_entries = [] # list of directions
        deferred_entry_dirs = []  # opposite-direction entries queued on signal flips
        deferred_exit = False

        for i in range(1, n_bars):
            if account_ruined or (self.sizing_mode == "risk_pct" and balance <= 0.0):
                break

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
                
                # Check bankruptcy
                if self.sizing_mode == "risk_pct" and balance <= 0.0:
                    balance = max(0.0, balance)
                    account_ruined = True
                    bot_stopped = True
                    deferred_entries.clear()
                    deferred_entry_dirs.clear()
                    equity_curve.append(0.0)
                    break

                # EA parity: on a signal flip the EA closes the position and
                # re-opens the opposite one at the SAME bar open. Queue the
                # opposite direction so Phase 2 executes it at this open.
                if deferred_entry_dirs:
                    deferred_entries.extend(deferred_entry_dirs)
                    deferred_entry_dirs = []

            # =============================================================
            # Phase 2: Execute deferred MARKET ENTRY at current bar's Open
            # =============================================================
            prev_atr = max(1e-6, atr_array[i - 1]) if i > 0 else curr_atr
            prev_atr50 = max(1e-6, atr50_array[i - 1]) if (i > 0 and len(atr50_array) > 0 and atr50_array[i - 1] > 0) else prev_atr

            while deferred_entries:
                if bot_stopped or account_ruined or (self.sizing_mode == "risk_pct" and balance <= 0.0):
                    deferred_entries.clear()
                    break
                deferred_entry_dir = deferred_entries.pop(0)
                if len(active_positions) < self.max_simultaneous_trades:
                    if deferred_entry_dir == "buy":
                        pos_entry_price = curr_open + half_spread
                    else:
                        pos_entry_price = curr_open - half_spread
                    pos_sl, pos_tp, tp1_val, tp2_val, p_pct = self._calc_sltp(
                        deferred_entry_dir, pos_entry_price, prev_atr, prev_atr50, highs, lows, i
                    )
                    unrealized = self._floating_pnl(active_positions, curr_close)
                    pos_lots = self._calc_lots(balance + unrealized, pos_entry_price, pos_sl, live_consec_losses)
                    active_positions.append({
                        "dir": deferred_entry_dir,
                        "entry_price": pos_entry_price,
                        "entry_idx": i,
                        "sl": pos_sl,
                        "tp": pos_tp,
                        "tp1": tp1_val,
                        "tp2": tp2_val,
                        "partial_pct": p_pct,
                        "tp1_hit": False,
                        "lots": pos_lots,
                        "entry_cost": self._deal_commission(pos_lots, pos_entry_price) if self.commission_per_side else 0.0
                    })

            # =============================================================
            # Phase 3: Intrabar SL / TP / Trailing / Breakeven / Time Exit checks
            # =============================================================
            for pos in active_positions[:]:
                closed = False
                exit_price = curr_close
                exit_reason = "signal"
                bars_held = i - pos["entry_idx"]

                # 1. Trailing Stop Check (dynamic SL update)
                if self.trailing_stop_atr > 0:
                    trail_dist = self.trailing_stop_atr * prev_atr
                    if pos["dir"] == "buy":
                        new_sl = curr_high - trail_dist
                        if new_sl > pos["sl"]:
                            pos["sl"] = new_sl
                    else:
                        new_sl = curr_low + trail_dist
                        if pos["sl"] == 0.0 or new_sl < pos["sl"]:
                            pos["sl"] = new_sl

                # 2. Breakeven Check (lock in entry price when profit threshold reached)
                if self.breakeven_atr > 0:
                    be_dist = self.breakeven_atr * prev_atr
                    if pos["dir"] == "buy":
                        if curr_high >= pos["entry_price"] + be_dist:
                            if pos["sl"] < pos["entry_price"]:
                                pos["sl"] = pos["entry_price"]
                    else:
                        if curr_low <= pos["entry_price"] - be_dist:
                            if pos["sl"] == 0.0 or pos["sl"] > pos["entry_price"]:
                                pos["sl"] = pos["entry_price"]

                # 3. Partial Take Profit Check
                if pos.get("tp1", 0.0) > 0 and not pos.get("tp1_hit", False):
                    tp1_price = pos["tp1"]
                    hit_tp1 = (curr_high >= tp1_price) if pos["dir"] == "buy" else (curr_low <= tp1_price)
                    if hit_tp1:
                        close_ratio = pos.get("partial_pct", 50.0) / 100.0
                        partial_lots = max(0.01, round(pos["lots"] * close_ratio, 2))
                        if partial_lots < pos["lots"]:
                            p_diff = (tp1_price - pos["entry_price"]) if pos["dir"] == "buy" else (pos["entry_price"] - tp1_price)
                            p_pnl = self._close_pnl({"lots": partial_lots, "entry_cost": self._deal_commission(partial_lots, pos["entry_price"]) if self.commission_per_side else 0.0, "entry_idx": pos["entry_idx"]}, p_diff, bars_held, i, bar_dates)
                            balance += p_pnl
                            trades.append(TradeRecord(
                                entry_index=pos["entry_idx"], exit_index=i,
                                direction=pos["dir"], entry_price=pos["entry_price"],
                                exit_price=tp1_price, sl_price=pos["sl"], tp_price=tp1_price,
                                size=partial_lots, pnl=p_pnl, pnl_pct=p_diff / (pos["entry_price"] + 1e-8),
                                exit_reason="tp_partial_1", duration_bars=bars_held
                            ))
                            pos["lots"] = max(0.01, round(pos["lots"] - partial_lots, 2))
                            pos["tp1_hit"] = True
                            pos["tp"] = pos.get("tp2", pos["tp"])

                # 4. Standard Intrabar Stop Loss and Take Profit Check
                if pos["dir"] == "buy":
                    if self.fill_mode == "open_only":
                        if pos["sl"] > 0.0 and curr_open <= pos["sl"]:
                            exit_price = curr_open
                            exit_reason = "sl"
                            closed = True
                        elif pos["tp"] > 0.0 and curr_open >= pos["tp"]:
                            exit_price = curr_open
                            exit_reason = "tp"
                            closed = True
                    else:
                        if pos["sl"] > 0.0 and curr_low <= pos["sl"]:
                            exit_price = pos["sl"]
                            exit_reason = "sl"
                            closed = True
                        elif pos["tp"] > 0.0 and curr_high >= pos["tp"]:
                            exit_price = pos["tp"]
                            exit_reason = "tp"
                            closed = True
                    if not closed and self.max_holding_bars > 0 and bars_held >= self.max_holding_bars:
                        exit_price = curr_open
                        exit_reason = "time_exit"
                        closed = True
                elif pos["dir"] == "sell":
                    if self.fill_mode == "open_only":
                        if pos["sl"] > 0.0 and curr_open >= pos["sl"]:
                            exit_price = curr_open
                            exit_reason = "sl"
                            closed = True
                        elif pos["tp"] > 0.0 and curr_open <= pos["tp"]:
                            exit_price = curr_open
                            exit_reason = "tp"
                            closed = True
                    else:
                        if pos["sl"] > 0.0 and curr_high >= pos["sl"]:
                            exit_price = pos["sl"]
                            exit_reason = "sl"
                            closed = True
                        elif pos["tp"] > 0.0 and curr_low <= pos["tp"]:
                            exit_price = pos["tp"]
                            exit_reason = "tp"
                            closed = True
                    if not closed and self.max_holding_bars > 0 and bars_held >= self.max_holding_bars:
                        exit_price = curr_open
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

                    if self.sizing_mode == "risk_pct" and balance <= 0.0:
                        balance = max(0.0, balance)
                        account_ruined = True
                        bot_stopped = True
                        break

            if account_ruined or (self.sizing_mode == "risk_pct" and balance <= 0.0):
                # Stop Out / Ruin: liquidate all remaining positions and halt
                for pos in active_positions:
                    p_diff = (curr_close - pos["entry_price"]) if pos["dir"] == "buy" else (pos["entry_price"] - curr_close)
                    p_pnl = self._close_pnl(pos, p_diff, i - pos["entry_idx"], i, bar_dates)
                    trades.append(TradeRecord(
                        entry_index=pos["entry_idx"], exit_index=i,
                        direction=pos["dir"], entry_price=pos["entry_price"],
                        exit_price=curr_close, sl_price=pos["sl"], tp_price=pos["tp"],
                        size=pos["lots"], pnl=p_pnl, pnl_pct=p_diff / (pos["entry_price"] + 1e-8),
                        exit_reason="stop_out_ruin", duration_bars=i - pos["entry_idx"]
                    ))
                active_positions.clear()
                pending_orders.clear()
                deferred_entries.clear()
                deferred_entry_dirs.clear()
                equity_curve.append(0.0)
                break

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
                            "entry_cost": self._deal_commission(p_order.lots, exec_price) if self.commission_per_side else 0.0
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
                    if can_enter_sell[i]:
                        deferred_entry_dirs.append("sell")
                elif has_sell and buy_signals[i]:
                    deferred_exit = True
                    if can_enter_buy[i]:
                        deferred_entry_dirs.append("buy")

            total_incoming = len(active_positions) + len(pending_orders) + len(deferred_entries)
            if total_incoming < self.max_simultaneous_trades and not bot_stopped and not account_ruined and (self.sizing_mode != "risk_pct" or balance > 0.0):
                sizing_equity = balance + self._floating_pnl(active_positions, curr_close)
                if sizing_equity > 0.0 or self.sizing_mode != "risk_pct":
                    if can_enter_buy[i]:
                        if self.order_type == "stop":
                            target_p = highs[i] + offset_dist
                            sl_p, tp_p, *_ = self._calc_sltp("buy", target_p, curr_atr, prev_atr50, highs, lows, i)
                            lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                            if lots > 0:
                                pending_orders.append(PendingOrder(
                                    direction="buy_stop", target_price=target_p, created_bar=i,
                                    sl_price=sl_p, tp_price=tp_p, lots=lots
                                ))
                        elif self.order_type == "limit":
                            target_p = lows[i] - offset_dist
                            sl_p, tp_p, *_ = self._calc_sltp("buy", target_p, curr_atr, prev_atr50, highs, lows, i)
                            lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                            if lots > 0:
                                pending_orders.append(PendingOrder(
                                    direction="buy_limit", target_price=target_p, created_bar=i,
                                    sl_price=sl_p, tp_price=tp_p, lots=lots
                                ))
                        else:
                            deferred_entries.append("buy")

                    elif can_enter_sell[i]:
                        if self.order_type == "stop":
                            target_p = lows[i] - offset_dist
                            sl_p, tp_p, *_ = self._calc_sltp("sell", target_p, curr_atr, prev_atr50, highs, lows, i)
                            lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                            if lots > 0:
                                pending_orders.append(PendingOrder(
                                    direction="sell_stop", target_price=target_p, created_bar=i,
                                    sl_price=sl_p, tp_price=tp_p, lots=lots
                                ))
                        elif self.order_type == "limit":
                            target_p = highs[i] + offset_dist
                            sl_p, tp_p, *_ = self._calc_sltp("sell", target_p, curr_atr, prev_atr50, highs, lows, i)
                            lots = self._calc_lots(sizing_equity, target_p, sl_p, live_consec_losses)
                            if lots > 0:
                                pending_orders.append(PendingOrder(
                                    direction="sell_limit", target_price=target_p, created_bar=i,
                                    sl_price=sl_p, tp_price=tp_p, lots=lots
                                ))
                        else:
                            deferred_entries.append("sell")

            # Record floating equity
            unrealized_pnl = self._floating_pnl(active_positions, curr_close)
            if self.sizing_mode == "risk_pct" and (balance + unrealized_pnl) <= 0.0 and active_positions:
                # Floating equity dipped below 0: Stop Out
                account_ruined = True
                bot_stopped = True
                for pos in active_positions:
                    p_diff = (curr_close - pos["entry_price"]) if pos["dir"] == "buy" else (pos["entry_price"] - curr_close)
                    p_pnl = self._close_pnl(pos, p_diff, i - pos["entry_idx"], i, bar_dates)
                    trades.append(TradeRecord(
                        entry_index=pos["entry_idx"], exit_index=i,
                        direction=pos["dir"], entry_price=pos["entry_price"],
                        exit_price=curr_close, sl_price=pos["sl"], tp_price=pos["tp"],
                        size=pos["lots"], pnl=p_pnl, pnl_pct=p_diff / (pos["entry_price"] + 1e-8),
                        exit_reason="stop_out_ruin", duration_bars=i - pos["entry_idx"]
                    ))
                active_positions.clear()
                pending_orders.clear()
                deferred_entries.clear()
                deferred_entry_dirs.clear()
                equity_curve.append(0.0)
                break

            equity_curve.append(float(balance + unrealized_pnl))
        return self._compile_metrics(trades, equity_curve, df=df)

    def _deal_commission(self, lots: float, price: float = 1.0) -> float:
        """Calculates broker deal commission matching asset type."""
        if self.contract_size <= 1.0:
            # Crypto / Index commission (0.05% of notional volume capped at commission_per_lot)
            deal_rate = min(self.commission_per_lot, price * self.contract_size * 0.0005)
            return lots * deal_rate
        return lots * self.commission_per_lot

    def _floating_pnl(self, positions: list[dict], ref_price: float) -> float:
        """Unrealized PnL of open positions at ref_price (used for equity sizing)."""
        total = 0.0
        for pos in positions:
            if pos["dir"] == "buy":
                total += (ref_price - pos["entry_price"]) * self.contract_size * pos["lots"]
            else:
                total += (pos["entry_price"] - ref_price) * self.contract_size * pos["lots"]
            total -= pos.get("entry_cost", 0.0)
        return total

    def _close_pnl(self, pos: dict, price_diff: float, bars_held: int, curr_bar_idx: int, bar_dates: pd.DatetimeIndex | None = None) -> float:
        """Net PnL of a position upon closing: Gross PnL - Commissions - Overnight Swap."""
        gross = price_diff * self.contract_size * pos["lots"]
        entry_cost = pos.get("entry_cost", 0.0)
        exit_price = pos.get("entry_price", 1.0) + price_diff
        exit_cost = self._deal_commission(pos["lots"], exit_price) if self.commission_per_side else (0.0 if entry_cost > 0 else self._deal_commission(pos["lots"], exit_price))
        
        # Swap / Financing cost calculation
        swap_cost = 0.0
        if self.swap_per_lot_per_day != 0.0:
            if bar_dates is not None and len(bar_dates) > curr_bar_idx and len(bar_dates) > pos["entry_idx"]:
                t_entry = bar_dates[pos["entry_idx"]]
                t_exit = bar_dates[curr_bar_idx]
                if pd.notnull(t_entry) and pd.notnull(t_exit):
                    days_held = max(1, (t_exit - t_entry).total_seconds() / 86400.0)
                    swap_cost = pos["lots"] * self.swap_per_lot_per_day * days_held
            else:
                # Fallback: estimate 1 day per 24 bars for hourly data
                days_held = max(1, bars_held / 24.0)
                swap_cost = pos["lots"] * self.swap_per_lot_per_day * days_held

        return gross - entry_cost - exit_cost - swap_cost

    def _calc_sltp(
        self,
        direction: str,
        entry_price: float,
        atr_val: float,
        atr50_val: float = 0.0,
        highs: np.ndarray | None = None,
        lows: np.ndarray | None = None,
        entry_idx: int = 0
    ) -> tuple[float, float, float, float, float]:
        sl_price = 0.0
        tp_price = 0.0
        tp1_price = 0.0
        tp2_price = 0.0
        partial_pct = 0.0

        if direction == "buy":
            # 1. Stop Loss selection
            if self.sl_atr_mult > 0:
                sl_price = entry_price - (self.sl_atr_mult * atr_val)
            elif self.sl_pips > 0:
                sl_price = entry_price - (self.sl_pips * self.point_size)
            elif self.sl_pct > 0:
                sl_price = entry_price * (1.0 - self.sl_pct / 100.0)
            elif self.smoothed_sl_atr > 0 and atr50_val > 0:
                sl_price = entry_price - (self.smoothed_sl_atr * atr50_val)

            # Swing structure override
            if self.swing_lookback > 0 and lows is not None and entry_idx > 0:
                lookback_start = max(0, entry_idx - self.swing_lookback)
                swing_low = float(np.min(lows[lookback_start:entry_idx]))
                if swing_low < entry_price:
                    sl_price = swing_low

            # 2. Take Profit selection
            if self.tp_atr_mult > 0:
                tp_price = entry_price + (self.tp_atr_mult * atr_val)
            elif self.tp_pips > 0:
                tp_price = entry_price + (self.tp_pips * self.point_size)
            elif self.tp_pct > 0:
                tp_price = entry_price * (1.0 + self.tp_pct / 100.0)
            elif self.smoothed_tp_atr > 0 and atr50_val > 0:
                tp_price = entry_price + (self.smoothed_tp_atr * atr50_val)

            # Partial Take Profit
            if self.partial_tp1_atr > 0 and self.partial_tp2_atr > 0:
                tp1_price = entry_price + (self.partial_tp1_atr * atr_val)
                tp2_price = entry_price + (self.partial_tp2_atr * atr_val)
                partial_pct = self.partial_close_pct
                tp_price = tp1_price

        else: # sell
            # 1. Stop Loss selection
            if self.sl_atr_mult > 0:
                sl_price = entry_price + (self.sl_atr_mult * atr_val)
            elif self.sl_pips > 0:
                sl_price = entry_price + (self.sl_pips * self.point_size)
            elif self.sl_pct > 0:
                sl_price = entry_price * (1.0 + self.sl_pct / 100.0)
            elif self.smoothed_sl_atr > 0 and atr50_val > 0:
                sl_price = entry_price + (self.smoothed_sl_atr * atr50_val)

            # Swing structure override
            if self.swing_lookback > 0 and highs is not None and entry_idx > 0:
                lookback_start = max(0, entry_idx - self.swing_lookback)
                swing_high = float(np.max(highs[lookback_start:entry_idx]))
                if swing_high > entry_price:
                    sl_price = swing_high

            # 2. Take Profit selection
            if self.tp_atr_mult > 0:
                tp_price = entry_price - (self.tp_atr_mult * atr_val)
            elif self.tp_pips > 0:
                tp_price = entry_price - (self.tp_pips * self.point_size)
            elif self.tp_pct > 0:
                tp_price = entry_price * (1.0 - self.tp_pct / 100.0)
            elif self.smoothed_tp_atr > 0 and atr50_val > 0:
                tp_price = entry_price - (self.smoothed_tp_atr * atr50_val)

            # Partial Take Profit
            if self.partial_tp1_atr > 0 and self.partial_tp2_atr > 0:
                tp1_price = entry_price - (self.partial_tp1_atr * atr_val)
                tp2_price = entry_price - (self.partial_tp2_atr * atr_val)
                partial_pct = self.partial_close_pct
                tp_price = tp1_price

        return sl_price, tp_price, tp1_price, tp2_price, partial_pct

    def _calc_lots(self, balance: float, entry_price: float, sl_price: float, live_consec_losses: int = 0) -> float:
        lot_decimals = 4 if self.contract_size <= 1.0 else (3 if self.contract_size <= 100.0 else 2)
        min_lot = 0.001 if self.contract_size <= 1.0 else 0.01

        if self.sizing_mode == "lots":
            lots = max(min_lot, round(self.lot_size, lot_decimals))
        elif self.sizing_mode == "risk_pct":
            base_capital = self.initial_deposit if self.risk_base == "initial_deposit" else balance
            if base_capital <= 0.0 or balance <= 0.0:
                return 0.0
            # Minimum SL distance safeguard (at least 0.15% price movement) to prevent division by near-zero
            raw_sl_dist = abs(entry_price - sl_price) if sl_price > 0 else (entry_price * 0.01)
            sl_dist = max(raw_sl_dist, entry_price * 0.0015)
            
            risk_cash = max(0.0, base_capital) * (self.risk_pct / 100.0)
            calculated_lots = risk_cash / (max(1e-6, sl_dist) * self.contract_size)
            max_leverage_lots = max(min_lot, (base_capital * 100.0) / (max(1e-6, entry_price) * self.contract_size))
            lots = max(min_lot, min(max_leverage_lots, round(calculated_lots, lot_decimals)))
        elif self.sizing_mode == "cash":
            calculated_lots = self.lot_size / (entry_price * self.contract_size + 1e-8)
            lots = max(min_lot, round(calculated_lots, lot_decimals))
        else:
            lots = max(min_lot, round(self.lot_size, lot_decimals))

        # Dynamic risk reduction on consecutive loss streak
        if self.consec_loss_action == "reduce_risk" and live_consec_losses >= self.consec_loss_threshold:
            factor = max(0.1, 1.0 - (self.consec_loss_reduction_pct / 100.0))
            lots = max(min_lot, round(lots * factor, lot_decimals))

        return lots

    def _compile_metrics(
        self, 
        trades: list[TradeRecord], 
        equity_curve: list[float],
        df: pd.DataFrame | None = None
    ) -> MT5SimulationResult:
        n_trades = len(trades)
        pnls = [t.pnl for t in trades]

        # Rebuild the reported equity curve as a PER-TRADE balance step curve.
        # Previously one point per bar (including floating PnL of open
        # positions) was stored, so a strategy with 25 trades showed a
        # thousands-of-points curve that looked like many more trades, and the
        # final point did not equal initial_deposit + total_net_profit. Now the
        # number of steps == n_trades and the last value == initial + net_profit.
        balance_curve = [self.initial_deposit]
        for t in trades:
            balance_curve.append(balance_curve[-1] + t.pnl)
        equity_curve = balance_curve

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
                "lots": t.size,
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
