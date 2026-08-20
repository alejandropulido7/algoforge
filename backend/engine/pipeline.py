import pandas as pd
import numpy as np
import itertools
import math
import json
from .indicators.calculator import IndicatorCalculator
from .indicators.catalog_defaults import get_catalog_default_ranges, get_tpsl_catalog_default_ranges
from .indicators.registry import get_indicator, normalize_indicator_params
from .reinforcement.trainer import RLTrainer
from .backtester.vectorbt_engine import VectorBTEngine
from .montecarlo.simulator import MonteCarloSimulator
from .ranker.scoring import StrategyRanker


class JobCancelledException(Exception):
    """Raised when an analysis job is cancelled by the user."""
    pass


def generate_param_values(p_min: float, p_step: float, p_max: float) -> list:
    """Generate deterministic discrete values from [min, step, max] without floating point drift."""
    try:
        p_min = float(p_min)
        p_step = float(p_step)
        p_max = float(p_max)
    except (ValueError, TypeError):
        return [p_min]

    if p_step <= 0 or p_max < p_min:
        return [int(p_min) if p_min.is_integer() else round(p_min, 4)]

    steps_count = int(round((p_max - p_min) / p_step))
    is_int = p_min.is_integer() and p_step.is_integer() and p_max.is_integer()

    values = []
    for s in range(steps_count + 1):
        val = p_min + (s * p_step)
        if val > p_max + 1e-9:
            break
        values.append(int(round(val)) if is_int else round(val, 4))

    return values if values else [int(p_min) if p_min.is_integer() else round(p_min, 4)]


def generate_signals_for_combination(df: pd.DataFrame, combo_arrays: dict, combo_dict: dict) -> tuple[np.ndarray, np.ndarray]:
    """Generate long and short signals based on indicator logic for a combination."""
    n_bars = len(df)
    close = df['Close'].values if 'Close' in df.columns else df.iloc[:, 0].values

    buy_conditions = []
    sell_conditions = []

    for ind_name, arr in combo_arrays.items():
        if arr is None or len(arr) != n_bars:
            continue
        arr_val = np.asarray(arr, dtype=float)
        params = combo_dict.get(ind_name, {})
        norm_name = ind_name.upper().replace(" ", "").replace("_", "")

        # 1. Oscillators / Level Bounds (RSI, Stochastic, StochRSI, TSI, UO, WilliamsR, MFI, CCI)
        if any(k in norm_name for k in ["RSI", "STOCH", "TSI", "ULTIMATE", "WILLIAMS", "MFI", "CCI"]):
            os_def = 30.0 if ("RSI" in norm_name or "ULTIMATE" in norm_name) else (20.0 if ("STOCH" in norm_name or "MFI" in norm_name) else (-80.0 if "WILLIAMS" in norm_name else -100.0))
            ob_def = 70.0 if ("RSI" in norm_name or "ULTIMATE" in norm_name) else (80.0 if ("STOCH" in norm_name or "MFI" in norm_name) else (-20.0 if "WILLIAMS" in norm_name else 100.0))
            os_val = float(params.get("oversold", os_def))
            ob_val = float(params.get("overbought", ob_def))

            prev_arr = np.roll(arr_val, 1)
            prev_arr[0] = arr_val[0]
            buy_c = (arr_val <= os_val) | ((prev_arr < os_val) & (arr_val >= os_val))
            sell_c = (arr_val >= ob_val) | ((prev_arr > ob_val) & (arr_val <= ob_val))
            buy_conditions.append(buy_c)
            sell_conditions.append(sell_c)

        # 2. Moving Averages / Price-level filters (EMA, SMA, WMA, HMA, KAMA, ParabolicSAR, Donchian)
        elif any(k in norm_name for k in ["EMA", "SMA", "WMA", "HMA", "KAMA", "SAR", "PSAR", "DONCHIAN"]):
            buy_c = (close > arr_val)
            sell_c = (close < arr_val)
            buy_conditions.append(buy_c)
            sell_conditions.append(sell_c)

        # 3. Bollinger Bands, Keltner Channels
        elif any(k in norm_name for k in ["BOLLINGER", "BBANDS", "KELTNER"]):
            med = np.nanmedian(arr_val)
            if -5.0 < med < 5.0:  # Normalized ratio / %B series
                buy_c = (arr_val < 0.25)
                sell_c = (arr_val > 0.75)
            else:  # Price level
                buy_c = (close > arr_val)
                sell_c = (close < arr_val)
            buy_conditions.append(buy_c)
            sell_conditions.append(sell_c)

        # 4. Zero-line Oscillators (MACD, AO, PPO, PVO, ROC, DPO, TRIX, Vortex, CMF)
        else:
            prev_arr = np.roll(arr_val, 1)
            prev_arr[0] = arr_val[0]
            buy_c = (arr_val > 0.0) | ((prev_arr <= 0.0) & (arr_val > 0.0))
            sell_c = (arr_val < 0.0) | ((prev_arr >= 0.0) & (arr_val < 0.0))
            buy_conditions.append(buy_c)
            sell_conditions.append(sell_c)

    if not buy_conditions:
        return np.zeros(n_bars, dtype=bool), np.zeros(n_bars, dtype=bool)

    # Combine conditions: Multi-indicator logical AND (Confirmation)
    final_buy = np.ones(n_bars, dtype=bool)
    final_sell = np.ones(n_bars, dtype=bool)
    for bc in buy_conditions:
        final_buy = final_buy & bc
    for sc in sell_conditions:
        final_sell = final_sell & sc

    # Fallback to trigger + trend confirmation if strict AND yields too few signals (< 5)
    if np.sum(final_buy) < 5 and len(buy_conditions) > 1:
        final_buy = buy_conditions[0] & buy_conditions[1]
        final_sell = sell_conditions[0] & sell_conditions[1]

    return final_buy, final_sell


def apply_tpsl_config(base_risk: dict, tpsl_combo: tuple) -> dict:
    """Build a specific risk config dictionary from a TP/SL combination."""
    rc = dict(base_risk)
    for mode, params in tpsl_combo:
        if mode == "atr_classic":
            rc["slType"] = "atr"
            rc["tpType"] = "atr"
            rc["slAtrMult"] = float(params.get("sl_atr", 1.5))
            rc["tpAtrMult"] = float(params.get("tp_atr", 3.0))
        elif mode == "trailing_stop":
            rc["trailingStopAtr"] = float(params.get("trail_atr", 1.0))
        elif mode == "breakeven":
            rc["breakevenAtr"] = float(params.get("be_atr", 1.0))
        elif mode == "swing_structure":
            rc["swingLookback"] = int(params.get("lookback", 20))
        elif mode == "time_exit":
            rc["maxHoldingBars"] = int(params.get("max_bars", 10))
        elif mode == "percentage":
            rc["slType"] = "pct"
            rc["tpType"] = "pct"
            rc["slPct"] = float(params.get("sl_pct", 1.0))
            rc["tpPct"] = float(params.get("tp_pct", 2.0))
        elif mode == "partial_tp":
            rc["partialTp1Atr"] = float(params.get("tp1_atr", 1.0))
            rc["partialTp2Atr"] = float(params.get("tp2_atr", 3.0))
            rc["partialClosePct"] = float(params.get("close_pct", 50.0))
        elif mode == "fixed_pips":
            rc["slType"] = "pips"
            rc["tpType"] = "pips"
            rc["slPips"] = float(params.get("sl_pips", 30.0))
            rc["tpPips"] = float(params.get("tp_pips", 60.0))
        elif mode == "smoothed_atr":
            rc["smoothedSlAtr"] = float(params.get("sl_atr_smooth", 1.5))
            rc["smoothedTpAtr"] = float(params.get("tp_atr_smooth", 3.0))
    return rc


class StrategyPipeline:
    """End-to-end algorithmic strategy discovery, validation and ranking pipeline matching MT5."""

    def __init__(self, config: dict, logger=None):
        self.config = config
        self.job_id = str(config.get("id") or config.get("job_id") or "default_job")
        self.logger = logger
        base_risk = config.get("risk") or {}
        sym = str(config.get("dataSource", {}).get("symbol") or base_risk.get("symbol") or "")
        self.risk_config = {
            "symbol": sym,
            "initialDeposit": float(base_risk.get("initialDeposit") or base_risk.get("initial_deposit") or 10000.0),
            "sizingMode": base_risk.get("sizingMode") or base_risk.get("sizing_mode") or "lots",
            "lotSize": float(base_risk.get("lotSize") or base_risk.get("lot_size") or 0.1),
            "riskPct": float(base_risk.get("riskPct") or base_risk.get("risk_pct") or 1.0),
            "riskBase": base_risk.get("riskBase") or base_risk.get("risk_base") or "initial_deposit",
            "direction": base_risk.get("direction") or "both",
            "orderType": base_risk.get("orderType") or base_risk.get("order_type") or "market",
            "maxSimultaneousTrades": int(base_risk.get("maxSimultaneousTrades") or base_risk.get("max_simultaneous_trades") or 1),
            "consecutiveLossAction": base_risk.get("consecutiveLossAction") or base_risk.get("consecutive_loss_action") or "none",
            "consecutiveLossThreshold": int(base_risk.get("consecutiveLossThreshold") or base_risk.get("consecutive_loss_threshold") or 3),
            "consecutiveLossReductionPct": float(base_risk.get("consecutiveLossReductionPct") or base_risk.get("consecutive_loss_reduction_pct") or 50.0),
            "consecutiveLossReactivation": base_risk.get("consecutiveLossReactivation") or base_risk.get("consecutive_loss_reactivation") or "none",
            "consecutiveLossCooldownBars": int(base_risk.get("consecutiveLossCooldownBars") or base_risk.get("consecutive_loss_cooldown_bars") or 20),
            "consecutiveLossCooldownDays": int(base_risk.get("consecutiveLossCooldownDays") or base_risk.get("consecutive_loss_cooldown_days") or 1),
            "consecutiveLossAutoCooldown": bool(base_risk.get("consecutiveLossAutoCooldown", True) if "consecutiveLossAutoCooldown" in base_risk else base_risk.get("consecutive_loss_auto_cooldown", True)),
            "contractSize": float(base_risk.get("contractSize") or base_risk.get("contract_size") or 100000.0),
            "pointSize": float(base_risk.get("pointSize") or base_risk.get("point_size") or 0.0001),
            "spreadPips": float(base_risk.get("spreadPips") or base_risk.get("spread_pips") or 1.0),
            "commissionPerLot": float(base_risk.get("commissionPerLot") or base_risk.get("commission_per_lot") or 7.0),
            "commissionPerSide": bool(base_risk.get("commissionPerSide", True) if "commissionPerSide" in base_risk else base_risk.get("commission_per_side", True)),
            "swapPerLotPerDay": float(base_risk.get("swapPerLotPerDay") or base_risk.get("swap_per_lot_per_day") or 0.0),
        }

        # Load active TP/SL Management modes and ranges
        self.tpsl_modes = config.get("tpslModes") or config.get("tpsl_modes") or [
            "atr_classic", "trailing_stop", "breakeven"
        ]
        self.tpsl_ranges = config.get("tpslRanges") or config.get("tpsl_ranges") or {}

        self.calculator = IndicatorCalculator()
        self.backtester = VectorBTEngine(self.risk_config)
        self.mc = MonteCarloSimulator(
            n_simulations=config.get("montecarlo", {}).get("simulations", 1000),
            ruin_threshold=config.get("montecarlo", {}).get("ruinThreshold", 50) / 100.0
        )
        self.ranker = StrategyRanker()
        self._redis_client = None

    def _get_redis(self):
        if self._redis_client is None:
            try:
                import redis
                from algoforge.config import settings
                self._redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis_client = None
        return self._redis_client

    def _is_cancelled(self) -> bool:
        """Check if job cancellation was flagged in Redis."""
        r = self._get_redis()
        if r is not None:
            try:
                val = r.get(f"cancel_job:{self.job_id}")
                if val:
                    return True
            except Exception:
                pass
        return False

    def run(self, df: pd.DataFrame, progress_callback=None) -> list[dict]:
        """Execute the full discovery pipeline with Redis-backed batching and live cancellation."""
        log = self.logger
        if log:
            log.section("Configuración del análisis")
            data_src = self.config.get("dataSource", {})
            log.config("symbol", data_src.get("symbol", "?"))
            log.config("timeframe", data_src.get("timeframe", "?"))
            log.config("rango fechas", f"{data_src.get('startDate', '?')} -> {data_src.get('endDate', '?')}")
            log.config("depósito inicial", f"${self.risk_config.get('initialDeposit', 10000.0):,.2f} USD")
            sizing_desc = f"Lote fijo ({self.risk_config.get('lotSize', 0.1)} lots)" if self.risk_config.get('sizingMode') == 'lots' else f"{self.risk_config.get('riskPct', 1.0)}% Riesgo ({'Depósito Inicial' if self.risk_config.get('riskBase') == 'initial_deposit' else 'Balance Compuesto'})"
            log.config("dimensionamiento", sizing_desc)
            log.config("operaciones simultáneas", self.risk_config.get('maxSimultaneousTrades', 1))
            log.config("barras OHLCV", len(df))

        # Check early cancellation
        if self._is_cancelled():
            if log:
                log.section("ANÁLISIS CANCELADO")
                log.info("Cancelación solicitada por el usuario antes de iniciar.")
                log.close("cancelled")
            raise JobCancelledException("Análisis cancelado por el usuario")

        # =========================================================================
        # 1. Deterministic Indicator Parameter Grid Construction
        # =========================================================================
        if progress_callback:
            progress_callback(phase="indicators", progress=5, message="Construyendo espacio de combinaciones de indicadores y TP/SL")

        selected_inds = self.config.get("indicators", ["RSI", "MACD", "EMA", "SMA"])
        ind_ranges = self.config.get("indicatorRanges", {})

        param_sets_by_indicator: dict[str, list[dict]] = {}

        def _effective_params(ind_name: str, params: dict) -> dict:
            cfg = get_indicator(ind_name)
            eff = dict(cfg.default_params) if cfg else {}
            eff.update(normalize_indicator_params(ind_name, params))
            return eff

        for ind in selected_inds:
            user_r = ind_ranges.get(ind) or {}
            catalog_r = get_catalog_default_ranges(ind)
            merged_ranges = {**catalog_r, **user_r}

            if not merged_ranges:
                param_sets_by_indicator[ind] = [{}]
                continue

            param_keys = list(merged_ranges.keys())
            param_values_lists = []
            for k in param_keys:
                r_def = merged_ranges[k]
                r_min = r_def.get("min", 1)
                r_step = r_def.get("step", 1)
                r_max = r_def.get("max", 1)
                vals = generate_param_values(r_min, r_step, r_max)
                param_values_lists.append(vals)

            p_combos = [dict(zip(param_keys, combo)) for combo in itertools.product(*param_values_lists)]
            param_sets_by_indicator[ind] = p_combos if p_combos else [{}]

        total_indicator_combos = math.prod(len(param_sets_by_indicator[ind]) for ind in selected_inds) if selected_inds else 1
        all_indicator_combinations = list(itertools.product(*[[(ind, p) for p in param_sets_by_indicator[ind]] for ind in selected_inds]))

        # =========================================================================
        # 2. Deterministic TP/SL Management Parameter Grid Construction
        # =========================================================================
        selected_tpsl_modes = list(self.tpsl_modes) if self.tpsl_modes else ["atr_classic"]
        tpsl_mode_sets: dict[str, list[dict]] = {}

        for mode in selected_tpsl_modes:
            user_r = self.tpsl_ranges.get(mode)
            if user_r:
                p_keys = list(user_r.keys())
                p_val_lists = []
                for k in p_keys:
                    r_def = user_r[k]
                    r_min = r_def.get("min", 1)
                    r_step = r_def.get("step", 1)
                    r_max = r_def.get("max", 1)
                    vals = generate_param_values(r_min, r_step, r_max)
                    p_val_lists.append(vals)

                mode_combos = [dict(zip(p_keys, combo)) for combo in itertools.product(*p_val_lists)]
            else:
                cat_r = get_tpsl_catalog_default_ranges(mode)
                def_p = {}
                for pk, r in cat_r.items():
                    r_min = float(r.get("min", 1))
                    r_max = float(r.get("max", 1))
                    mid_val = (r_min + r_max) / 2.0
                    def_p[pk] = int(mid_val) if mid_val.is_integer() else round(mid_val, 2)
                mode_combos = [def_p]

            tpsl_mode_sets[mode] = mode_combos if mode_combos else [{}]

        total_tpsl_combos = math.prod(len(tpsl_mode_sets[m]) for m in selected_tpsl_modes) if selected_tpsl_modes else 1
        all_tpsl_combinations = list(itertools.product(*[[(mode, p) for p in tpsl_mode_sets[mode]] for mode in selected_tpsl_modes]))
        if not all_tpsl_combinations:
            all_tpsl_combinations = [[("default", {})]]

        # Total Global Combinations
        total_combinations = total_indicator_combos * total_tpsl_combos

        # Save metadata to Redis for monitoring & external inspection
        r = self._get_redis()
        if r is not None:
            try:
                meta = {
                    "job_id": self.job_id,
                    "total_combinations": total_combinations,
                    "total_indicator_combos": total_indicator_combos,
                    "total_tpsl_combos": total_tpsl_combos,
                    "batch_size": 15,
                    "indicators": selected_inds,
                    "tpsl_modes": selected_tpsl_modes
                }
                r.set(f"job_combos:{self.job_id}:meta", json.dumps(meta), ex=86400)
            except Exception:
                pass

        if log:
            log.section(f"ESPACIO DE BÚSQUEDA Y PARÁMETROS ({total_combinations:,} COMBINACIONES TOTALES)")
            log.info(f"Indicadores seleccionados: {len(selected_inds)} ({total_indicator_combos:,} combinaciones de indicadores)")
            for ind in selected_inds:
                p_sets = param_sets_by_indicator[ind]
                user_r = ind_ranges.get(ind) or get_catalog_default_ranges(ind)
                ranges_desc = []
                for pk, r in user_r.items():
                    val_count = len(generate_param_values(r.get("min", 1), r.get("step", 1), r.get("max", 1)))
                    ranges_desc.append(f"{pk}: [{r.get('min')} a {r.get('max')} paso {r.get('step')}] ({val_count} valores)")
                r_str = ", ".join(ranges_desc) if ranges_desc else "Sin parámetros (serie fija)"
                log.info(f"  • {ind}: {len(p_sets)} variantes ({r_str})")

            log.info(f"Modos TP/SL Management activos: {len(selected_tpsl_modes)} ({total_tpsl_combos:,} configuraciones de salida)")
            for mode in selected_tpsl_modes:
                p_sets = tpsl_mode_sets[mode]
                user_r = self.tpsl_ranges.get(mode)
                ranges_desc = []
                if user_r:
                    for pk, r in user_r.items():
                        val_count = len(generate_param_values(r.get("min", 1), r.get("step", 1), r.get("max", 1)))
                        ranges_desc.append(f"{pk}: [{r.get('min')} a {r.get('max')} paso {r.get('step')}] ({val_count} valores)")
                else:
                    ranges_desc.append(f"Valores base canónicos ({p_sets[0]})")
                r_str = ", ".join(ranges_desc)
                log.info(f"  • {mode}: {len(p_sets)} variantes ({r_str})")

            log.info(f"Total combinaciones deterministas a evaluar sobre el dataset: {total_combinations:,} ({total_indicator_combos:,} indicadores x {total_tpsl_combos:,} TP/SL)")
            log.info("Ejecución optimizada por lotes de 15 con almacenamiento en Redis y control de cancelación")

        # =========================================================================
        # 3. Exhaustive Grid Evaluation over Full Dataset in Batches of 15
        # =========================================================================
        if progress_callback:
            progress_callback(phase="indicators", progress=10, message=f"Evaluando {total_combinations:,} combinaciones (lotes de 15)")

        if log:
            log.section("EJECUCIÓN POR LOTES DE 15 COMBINACIONES SOBRE TODO EL DATASET")

        indicator_cache: dict[tuple, np.ndarray | pd.Series] = {}
        raw_atr = IndicatorCalculator.calculate_single(df, "ATR")
        atr_arr = np.nan_to_num(np.asarray(raw_atr, dtype=float)) if raw_atr is not None else None

        # Bounded candidate collection: keep top 50 to avoid memory growth
        MAX_CANDIDATES_IN_MEMORY = 50
        valid_combos_with_trades: list[dict] = []
        combo_idx = 0
        BATCH_SIZE = 15
        log_step = max(1, total_combinations // 200)
        was_cancelled_by_user = False

        for ind_combo in all_indicator_combinations:
            # Check cancellation between indicator setups
            if self._is_cancelled():
                was_cancelled_by_user = True
                if log:
                    log.section("DETENCIÓN DE ANÁLISIS POR EL USUARIO")
                    log.info(f"Análisis detenido a petición del usuario en la combinación #{combo_idx:,} de {total_combinations:,}.")
                    log.info(f"Se compilarán las mejores estrategias analizadas hasta este momento ({len(valid_combos_with_trades)} candidatas).")
                break

            ind_dict = {ind_name: params for ind_name, params in ind_combo}
            ind_arrays = {}

            # Calculate or fetch cached indicator series
            for ind_name, raw_params in ind_combo:
                eff = _effective_params(ind_name, raw_params)
                cache_key = (ind_name, tuple(sorted(eff.items())))
                if cache_key not in indicator_cache:
                    indicator_cache[cache_key] = IndicatorCalculator.calculate_single(df, ind_name, eff)
                ind_arrays[ind_name] = indicator_cache[cache_key]

            # Generate trade signals for this indicator combination
            entries, exits = generate_signals_for_combination(df, ind_arrays, ind_dict)
            has_signals = (np.sum(entries) > 0)

            # Format indicator description string
            ind_desc_parts = []
            for ind_name, raw_params in ind_combo:
                p_str = ", ".join(f"{k}={v}" for k, v in raw_params.items()) if raw_params else "default"
                ind_desc_parts.append(f"{ind_name}({p_str})")
            ind_desc = ", ".join(ind_desc_parts)

            if not has_signals:
                combo_idx += len(all_tpsl_combinations)
                if log and (combo_idx % log_step == 0 or combo_idx >= total_combinations or combo_idx <= 20):
                    log.info(f"[{combo_idx}/{total_combinations}] {ind_desc} -> 0 señales en dataset (0 operaciones)")
                continue

            # Process TP/SL combinations in discrete chunks of BATCH_SIZE (15)
            for batch_start in range(0, len(all_tpsl_combinations), BATCH_SIZE):
                # Check cancellation between chunks of 15
                if self._is_cancelled():
                    was_cancelled_by_user = True
                    if log:
                        log.section("DETENCIÓN DE ANÁLISIS POR EL USUARIO")
                        log.info(f"Análisis detenido a petición del usuario en el lote #{combo_idx // BATCH_SIZE + 1}.")
                        log.info(f"Se compilarán las mejores estrategias analizadas hasta este momento ({len(valid_combos_with_trades)} candidatas).")
                    break

                tpsl_batch = all_tpsl_combinations[batch_start:batch_start + BATCH_SIZE]

                for tpsl_combo in tpsl_batch:
                    combo_idx += 1
                    specific_risk = apply_tpsl_config(self.risk_config, tpsl_combo)

                    tpsl_desc_parts = []
                    for mode, p in tpsl_combo:
                        if mode == "default":
                            continue
                        p_str = ", ".join(f"{k}={v}" for k, v in p.items()) if p else "activo"
                        tpsl_desc_parts.append(f"{mode}({p_str})")
                    tpsl_desc = ", ".join(tpsl_desc_parts) if tpsl_desc_parts else "Default"
                    full_combo_desc = f"{ind_desc} | TP/SL: {tpsl_desc}"

                    backtester = VectorBTEngine(specific_risk)
                    bt = backtester.backtest(df, entries, exits, atr_array=atr_arr)
                    win_rate = float(bt.win_rate)
                    n_trades = int(bt.n_trades)
                    total_return = float(bt.total_return)
                    profit_factor = float(bt.profit_factor) if not np.isnan(bt.profit_factor) else 0.0
                    sharpe = float(bt.sharpe_ratio) if not np.isnan(bt.sharpe_ratio) else 0.0
                    max_dd = float(bt.max_drawdown)

                    if n_trades > 0:
                        score = sharpe * 0.35 + min(3.0, max(0.0, profit_factor - 1.0)) * 0.25 + (total_return / 100.0) * 0.20 + (win_rate / 100.0) * 0.20
                        if n_trades < 10:
                            score -= 2.0
                        elif n_trades > 400:
                            score -= min(2.0, (n_trades - 400) / 100.0)

                        this_combo_configs = [{"name": ind_name, "params": _effective_params(ind_name, raw_p), "var_name": ind_name} for ind_name, raw_p in ind_combo]

                        valid_combos_with_trades.append({
                            "combo_idx": combo_idx,
                            "ind_combo": ind_combo,
                            "tpsl_combo": tpsl_combo,
                            "desc": full_combo_desc,
                            "score": score,
                            "sharpe": sharpe,
                            "win_rate": win_rate,
                            "n_trades": n_trades,
                            "return": total_return,
                            "profit_factor": profit_factor,
                            "max_drawdown": max_dd,
                            "entries": entries,
                            "exits": exits,
                            "backtest": bt,
                            "risk_config": specific_risk,
                            "indicator_config": this_combo_configs
                        })

                        # Prune memory if candidate list exceeds limit
                        if len(valid_combos_with_trades) > MAX_CANDIDATES_IN_MEMORY * 2:
                            valid_combos_with_trades.sort(key=lambda x: x["score"], reverse=True)
                            valid_combos_with_trades = valid_combos_with_trades[:MAX_CANDIDATES_IN_MEMORY]

                    if log and (combo_idx % log_step == 0 or combo_idx == total_combinations or combo_idx <= 20):
                        log.info(
                            f"[{combo_idx}/{total_combinations}] {full_combo_desc} -> "
                            f"WinR: {win_rate:.1f}%, Trades: {n_trades}, Retorno: {total_return:+.2f}%, "
                            f"PF: {profit_factor:.2f}, Sharpe: {sharpe:.2f}, DD: {max_dd:.1f}%"
                        )

                # Batch progress update to client & Redis
                sub_pct = int(100 * (combo_idx / max(1, total_combinations)))
                pct = 10 + int(50 * (combo_idx / max(1, total_combinations)))
                batch_msg = f"[{combo_idx:,}/{total_combinations:,}] {full_combo_desc}"

                if progress_callback and (combo_idx % (BATCH_SIZE * 2) == 0 or combo_idx == total_combinations):
                    progress_callback(
                        phase="indicators",
                        progress=pct,
                        message=batch_msg,
                        sub_progress=sub_pct,
                        sub_current=combo_idx,
                        sub_total=total_combinations,
                        valid_candidates=len(valid_combos_with_trades)
                    )

                r = self._get_redis()
                if r is not None and (combo_idx % BATCH_SIZE == 0 or combo_idx == total_combinations):
                    try:
                        r.set(f"job_combos:{self.job_id}:progress", json.dumps({
                            "current": combo_idx,
                            "total": total_combinations,
                            "candidates": len(valid_combos_with_trades),
                            "sub_progress": sub_pct,
                            "message": batch_msg
                        }), ex=86400)
                    except Exception:
                        pass

                if was_cancelled_by_user:
                    break

            if was_cancelled_by_user:
                break

        # =========================================================================
        # 4. Check for Zero Results / No Trades Condition
        # =========================================================================
        if not valid_combos_with_trades:
            if was_cancelled_by_user:
                if log:
                    log.section("RESULTADO: CANCELACIÓN SIN OPERACIONES")
                    log.info("El análisis se detuvo antes de registrar operaciones válidas.")
                    log.close("cancelled")
                raise JobCancelledException("Análisis cancelado por el usuario (sin operaciones)")

            if log:
                log.section("RESULTADO: NINGUNA OPERACIÓN GENERADA")
                log.info("Ninguna combinación de indicadores y TP/SL generó operaciones sobre el dataset.")
                log.info("No se calificaron estrategias candidatas.")
                log.close("completed_no_trades")

            if progress_callback:
                progress_callback(phase="done", progress=100, message="Análisis completado: No se generaron operaciones")

            return []

        # Sort valid combinations by performance score
        valid_combos_with_trades.sort(key=lambda x: x["score"], reverse=True)

        if log:
            log.section(f"TOP 10 MEJORES COMBINACIONES DESCUBIERTAS (de {total_combinations:,})")
            for rank_i, cr in enumerate(valid_combos_with_trades[:10], 1):
                log.info(
                    f"  #{rank_i} {cr['desc']} -> "
                    f"Sharpe: {cr['sharpe']:.2f}, Retorno: {cr['return']:+.2f}%, "
                    f"WinR: {cr['win_rate']:.1f}%, Trades: {cr['n_trades']}, "
                    f"PF: {cr['profit_factor']:.2f}, DD: {cr['max_drawdown']:.1f}%"
                )

        # =========================================================================
        # 5. Candidate Strategies Creation from Optimal Grid Combinations
        # =========================================================================
        gen_cfg = self.config.get("genetic", {})
        top_target = int(gen_cfg.get("topStrategiesCount") or self.config.get("topStrategiesCount") or 20)

        gp_strategies = []
        for i, cr in enumerate(valid_combos_with_trades[:top_target], 1):
            ind_names_str = ", ".join(f"{ind_name}({', '.join(f'{k}={v}' for k, v in raw_p.items())})" if raw_p else ind_name for ind_name, raw_p in cr["ind_combo"])
            gp_strategies.append({
                "id": f"strategy_combo_{i}",
                "tree": f"ComboStrategy({ind_names_str})",
                "fitness": cr["score"],
                "entries": cr["entries"],
                "exits": cr["exits"],
                "backtest": cr["backtest"],
                "indicator_config": cr["indicator_config"],
                "risk_config": cr["risk_config"]
            })

        # =========================================================================
        # 6. RL Agent (if enabled)
        # =========================================================================
        rl_cfg = self.config.get("rl", {})
        if rl_cfg.get("enabled", False):
            if progress_callback:
                progress_callback(phase="rl", progress=60, message="Entrenando agente RL y exportando ONNX")
            best_risk = valid_combos_with_trades[0]["risk_config"]
            trainer = RLTrainer(
                algorithm=rl_cfg.get("algorithm", "ppo"),
                total_timesteps=rl_cfg.get("timesteps", 10000),
                learning_rate=rl_cfg.get("learningRate", 0.0003)
            )
            # Active indicator dictionary
            best_ind_dict = {ic["name"]: indicator_cache.get((ic["name"], tuple(sorted(ic["params"].items())))) for ic in valid_combos_with_trades[0]["indicator_config"]}
            _, rl_info = trainer.train(
                df=df,
                indicators=best_ind_dict,
                job_id=self.job_id,
                strategy_id=f"rl_{rl_cfg.get('algorithm', 'ppo')}"
            )
            bt_rl = VectorBTEngine(best_risk).backtest(df, rl_info["entries"], rl_info["exits"])
            if bt_rl.n_trades > 0:
                gp_strategies.append({
                    "id": f"rl_agent_{rl_cfg.get('algorithm', 'ppo')}",
                    "tree": f"RL_Agent({rl_cfg.get('algorithm', 'ppo').upper()})",
                    "fitness": bt_rl.sharpe_ratio,
                    "entries": rl_info["entries"],
                    "exits": rl_info["exits"],
                    "backtest": bt_rl,
                    "is_rl": True,
                    "onnx_filename": rl_info.get("onnx_filename"),
                    "onnx_path": rl_info.get("onnx_path"),
                    "zip_path": rl_info.get("zip_path"),
                    "window_size": rl_info.get("window_size", 20),
                    "n_features": rl_info.get("n_features", 5 + len(best_ind_dict)),
                    "risk_config": best_risk,
                    "indicator_config": valid_combos_with_trades[0]["indicator_config"]
                })

        # =========================================================================
        # 7. Backtesting, Robustness & Monte Carlo Validation
        # =========================================================================
        if progress_callback:
            progress_callback(phase="backtest", progress=75, message="Validando rendimiento y robustez Monte Carlo")

        if log:
            log.section("Backtesting y Validación Monte Carlo de Estrategias Finalistas")
            log.info(f"{len(gp_strategies)} mejores combinaciones seleccionadas para ranking final")

        candidate_results = []
        for i, strat in enumerate(gp_strategies):
            strat_risk = strat.get("risk_config", self.risk_config)
            bt = strat.get("backtest")
            if bt is None or bt.n_trades == 0:
                bt = VectorBTEngine(strat_risk).backtest(df, strat["entries"], strat["exits"], atr_array=atr_arr)

            if bt.n_trades == 0:
                continue

            mc_method = self.config.get("montecarlo", {}).get("method", "permutation")
            mc_res = self.mc.simulate(bt.trade_pnls, method=mc_method)

            candidate_results.append({
                "id": strat["id"],
                "strategy_tree": strat["tree"],
                "is_rl": strat.get("is_rl", False),
                "job_id": self.job_id,
                "onnx_filename": strat.get("onnx_filename", f"AlgoForge_Job_{self.job_id}.onnx"),
                "onnx_path": strat.get("onnx_path", ""),
                "zip_path": strat.get("zip_path", ""),
                "window_size": strat.get("window_size", 20),
                "n_features": strat.get("n_features", 5),
                "total_return_pct": float(bt.total_return),
                "total_net_profit": float(bt.total_net_profit),
                "gross_profit": float(bt.gross_profit),
                "gross_loss": float(bt.gross_loss),
                "expected_payoff": float(bt.expected_payoff),
                "sharpe_ratio": float(bt.sharpe_ratio) if not np.isnan(bt.sharpe_ratio) else 0.0,
                "max_drawdown_pct": float(bt.max_drawdown) if not np.isnan(bt.max_drawdown) else 0.0,
                "win_rate": float(bt.win_rate) if not np.isnan(bt.win_rate) else 0.0,
                "profit_factor": float(bt.profit_factor) if not np.isnan(bt.profit_factor) else 0.0,
                "n_trades": int(bt.n_trades),
                "consecutive_wins_max": int(bt.consecutive_wins_max),
                "consecutive_wins_max_cash": float(bt.consecutive_wins_max_cash),
                "consecutive_losses_max": int(bt.consecutive_losses_max),
                "consecutive_losses_max_cash": float(bt.consecutive_losses_max_cash),
                "consecutive_wins_avg": float(bt.consecutive_wins_avg),
                "consecutive_losses_avg": float(bt.consecutive_losses_avg),
                "recovery_factor": float(bt.recovery_factor),
                "mc_robustness": float(mc_res.robustness_score),
                "mc_prob_ruin": float(mc_res.probability_of_ruin),
                "mc_95_drawdown": float(mc_res.confidence_95_drawdown),
                "equity_curve": bt.equity_curve,
                "trade_log": bt.trade_log,
                "indicator_config": strat.get("indicator_config", []),
                "risk_config": strat_risk,
                "entry_rules": {"tree": strat["tree"]},
                "exit_rules": {"rule": "sl_tp_or_signal"}
            })

        if not candidate_results:
            if log:
                log.section("RESULTADO: NINGUNA ESTRATEGIA CALIFICADA")
                log.info("Ninguna estrategia candidata generó operaciones.")
                log.close("completed_no_trades")
            if progress_callback:
                progress_callback(phase="done", progress=100, message="Análisis completado: No se generaron operaciones")
            return []

        # =========================================================================
        # 8. Ranking & Output Selection
        # =========================================================================
        if progress_callback:
            progress_callback(phase="ranking", progress=90, message="Compilando ranking final de estrategias")

        ranked_strategies = self.ranker.rank(candidate_results)[:top_target]

        if log:
            log.section(f"RANKING FINAL: TOP {len(ranked_strategies)} ESTRATEGIAS SELECCIONADAS")
            for s in ranked_strategies:
                log.info(
                    f"#{s['rank']} Score: {s['total_score']:.1f} | Ret: {s['total_return_pct']:+.2f}% | "
                    f"Trades: {s['n_trades']} | WinRate: {s['win_rate']:.1f}% | "
                    f"PF: {s['profit_factor']:.2f} | Sharpe: {s['sharpe_ratio']:.2f} | DD: {s['max_drawdown_pct']:.1f}%"
                )
                log.config("  árbol", s["strategy_tree"])
            log.close("completed")

        if progress_callback:
            progress_callback(phase="done", progress=100, message="Análisis completado exitosamente")

        return ranked_strategies
