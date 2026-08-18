import re

file_path = "/Users/alejandropulido/Documents/software-projects/trading/algoforge/backend/engine/backtester/mt5_simulator.py"
with open(file_path, "r") as f:
    code = f.read()

code = code.replace(
    "self.initial_deposit = float(cfg.get(\"initialDeposit\", 10000.0))",
    "self.max_simultaneous_trades = int(cfg.get(\"maxSimultaneousTrades\") or cfg.get(\"max_simultaneous_trades\") or 1)\n        self.initial_deposit = float(cfg.get(\"initialDeposit\", 10000.0))"
)

old_simulate = """        balance = self.initial_deposit
        equity_curve = [balance]
        trades: list[TradeRecord] = []

        # Current position state
        in_position = False
        pos_dir = ""  # "buy" or "sell"
        pos_entry_price = 0.0
        pos_entry_idx = 0
        pos_lots = 0.0
        pos_sl = 0.0
        pos_tp = 0.0

        # Current pending order state
        pending_order: PendingOrder | None = None
        offset_dist = self.pending_offset_pips * self.point_size
        live_consec_losses = 0
        bot_stopped = False
        stopped_bar_idx = -1

        # Deferred execution state \u2014 matches real MT5/TradingView next-bar execution
        # Signal on bar[i] \u2192 action executes at Open[i+1]
        deferred_entry_dir = ""   # "" = none, "buy" or "sell"
        deferred_exit = False     # True = signal exit pending for next bar open"""

new_simulate = """        balance = self.initial_deposit
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
        deferred_exit = False"""

code = code.replace(old_simulate, new_simulate)

old_loop_body = code[code.find("            # ============================================================="):code.find("        return self._compile_metrics(trades, equity_curve, df=df)")]

new_loop_body = """            # =============================================================
            # Phase 1: Execute deferred SIGNAL EXIT at current bar's Open
            # =============================================================
            if deferred_exit and active_positions:
                for pos in active_positions:
                    exit_price = curr_open
                    exit_reason = "signal"
                    bars_held = i - pos["entry_idx"]

                    if pos["dir"] == "buy":
                        price_diff = exit_price - pos["entry_price"]
                    else:
                        price_diff = pos["entry_price"] - exit_price

                    trade_pnl = (price_diff * self.contract_size * pos["lots"]) - (pos["lots"] * self.commission_per_lot)
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
            while deferred_entries:
                deferred_entry_dir = deferred_entries.pop(0)
                if len(active_positions) < self.max_simultaneous_trades:
                    pos_entry_price = curr_open
                    pos_sl, pos_tp = self._calc_sltp(deferred_entry_dir, pos_entry_price, curr_atr)
                    pos_lots = self._calc_lots(balance, pos_entry_price, pos_sl, live_consec_losses)
                    active_positions.append({
                        "dir": deferred_entry_dir,
                        "entry_price": pos_entry_price,
                        "entry_idx": i,
                        "sl": pos_sl,
                        "tp": pos_tp,
                        "lots": pos_lots
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

                    trade_pnl = (price_diff * self.contract_size * pos["lots"]) - (pos["lots"] * self.commission_per_lot)
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
                            "lots": p_order.lots
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
                if can_enter_buy[i]:
                    if self.order_type == "stop":
                        target_p = highs[i] + offset_dist
                        sl_p, tp_p = self._calc_sltp("buy", target_p, curr_atr)
                        lots = self._calc_lots(balance, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="buy_stop", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    elif self.order_type == "limit":
                        target_p = lows[i] - offset_dist
                        sl_p, tp_p = self._calc_sltp("buy", target_p, curr_atr)
                        lots = self._calc_lots(balance, target_p, sl_p, live_consec_losses)
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
                        lots = self._calc_lots(balance, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="sell_stop", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    elif self.order_type == "limit":
                        target_p = highs[i] + offset_dist
                        sl_p, tp_p = self._calc_sltp("sell", target_p, curr_atr)
                        lots = self._calc_lots(balance, target_p, sl_p, live_consec_losses)
                        pending_orders.append(PendingOrder(
                            direction="sell_limit", target_price=target_p, created_bar=i,
                            sl_price=sl_p, tp_price=tp_p, lots=lots
                        ))
                    else:
                        deferred_entries.append("sell")

            # Record floating equity
            unrealized_pnl = 0.0
            for pos in active_positions:
                if pos["dir"] == "buy":
                    unrealized_pnl += (curr_close - pos["entry_price"]) * self.contract_size * pos["lots"]
                else:
                    unrealized_pnl += (pos["entry_price"] - curr_close) * self.contract_size * pos["lots"]
            
            equity_curve.append(float(balance + unrealized_pnl))
"""

code = code.replace(old_loop_body, new_loop_body)

with open(file_path, "w") as f:
    f.write(code)
