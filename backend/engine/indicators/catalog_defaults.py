"""
Default indicator parameter ranges matching frontend/src/data/indicatorsCatalog.ts
Used for deterministic grid search when frontend ranges are omitted.
"""

INDICATOR_CATALOG_DEFAULTS: dict[str, dict[str, dict[str, float]]] = {
    # === 1. MOMENTUM ===
    "RSI": {
        "period": {"min": 5, "step": 1, "max": 30},
        "oversold": {"min": 20, "step": 1, "max": 35},
        "overbought": {"min": 65, "step": 1, "max": 80},
    },
    "STOCHASTIC": {
        "period": {"min": 5, "step": 1, "max": 25},
        "oversold": {"min": 15, "step": 1, "max": 30},
        "overbought": {"min": 70, "step": 1, "max": 85},
    },
    "STOCHRSI": {
        "period": {"min": 7, "step": 1, "max": 21},
        "oversold": {"min": 15, "step": 1, "max": 30},
        "overbought": {"min": 70, "step": 1, "max": 85},
    },
    "TSI": {
        "period": {"min": 10, "step": 1, "max": 30},
        "oversold": {"min": -35, "step": 5, "max": -15},
        "overbought": {"min": 15, "step": 5, "max": 35},
    },
    "ULTIMATEOSCILLATOR": {
        "period": {"min": 7, "step": 1, "max": 21},
        "oversold": {"min": 25, "step": 1, "max": 35},
        "overbought": {"min": 65, "step": 1, "max": 75},
    },
    "WILLIAMSR": {
        "period": {"min": 5, "step": 1, "max": 30},
        "oversold": {"min": -90, "step": 5, "max": -75},
        "overbought": {"min": -25, "step": 5, "max": -10},
    },
    "AO": {
        "period": {"min": 3, "step": 1, "max": 10},
    },
    "KAMA": {
        "period": {"min": 5, "step": 1, "max": 25},
    },
    "ROC": {
        "period": {"min": 5, "step": 1, "max": 30},
        "oversold": {"min": -5, "step": 1, "max": -1},
        "overbought": {"min": 1, "step": 1, "max": 5},
    },
    "PPO": {
        "fast": {"min": 8, "step": 1, "max": 16},
        "slow": {"min": 20, "step": 1, "max": 35},
        "signal": {"min": 5, "step": 1, "max": 12},
    },
    "PVO": {
        "fast": {"min": 8, "step": 1, "max": 16},
        "slow": {"min": 20, "step": 1, "max": 35},
        "signal": {"min": 5, "step": 1, "max": 12},
    },

    # === 2. TREND ===
    "MACD": {
        "fast": {"min": 8, "step": 1, "max": 16},
        "slow": {"min": 20, "step": 1, "max": 35},
        "signal": {"min": 5, "step": 1, "max": 12},
    },
    "EMA": {
        "period": {"min": 5, "step": 5, "max": 200},
    },
    "SMA": {
        "period": {"min": 5, "step": 5, "max": 200},
    },
    "WMA": {
        "period": {"min": 5, "step": 5, "max": 100},
    },
    "HMA": {
        "period": {"min": 5, "step": 5, "max": 100},
    },
    "ADX": {
        "period": {"min": 7, "step": 1, "max": 30},
        "threshold": {"min": 20, "step": 5, "max": 40},
    },
    "AROON": {
        "period": {"min": 10, "step": 1, "max": 40},
        "threshold": {"min": 50, "step": 10, "max": 90},
    },
    "CCI": {
        "period": {"min": 10, "step": 1, "max": 35},
        "oversold": {"min": -150, "step": 25, "max": -50},
        "overbought": {"min": 50, "step": 25, "max": 150},
    },
    "PSAR": {
        "step": {"min": 0.01, "step": 0.01, "max": 0.05},
        "max_step": {"min": 0.1, "step": 0.05, "max": 0.3},
    },
    "ICHIMOKU": {
        "tenkan": {"min": 7, "step": 1, "max": 12},
        "kijun": {"min": 20, "step": 2, "max": 32},
        "senkou": {"min": 44, "step": 4, "max": 60},
    },
    "KST": {
        "signal": {"min": 5, "step": 1, "max": 15},
    },
    "DPO": {
        "period": {"min": 10, "step": 2, "max": 30},
    },
    "TRIX": {
        "period": {"min": 5, "step": 1, "max": 25},
    },
    "MASSINDEX": {
        "fast": {"min": 5, "step": 1, "max": 12},
        "slow": {"min": 15, "step": 2, "max": 35},
    },
    "VORTEX": {
        "period": {"min": 7, "step": 1, "max": 28},
    },
    "STC": {
        "fast": {"min": 15, "step": 2, "max": 30},
        "slow": {"min": 35, "step": 5, "max": 65},
        "cycle": {"min": 5, "step": 1, "max": 15},
    },

    # === 3. VOLATILITY ===
    "ATR": {
        "period": {"min": 7, "step": 1, "max": 30},
    },
    "BOLLINGER": {
        "period": {"min": 10, "step": 5, "max": 50},
        "deviation": {"min": 1.5, "step": 0.5, "max": 3.0},
    },
    "BOLLINGER BANDS": {
        "period": {"min": 10, "step": 5, "max": 50},
        "deviation": {"min": 1.5, "step": 0.5, "max": 3.0},
    },
    "KELTNER": {
        "period": {"min": 10, "step": 2, "max": 30},
        "multiplier": {"min": 1.0, "step": 0.5, "max": 3.0},
    },
    "DONCHIAN": {
        "period": {"min": 10, "step": 2, "max": 40},
    },
    "ULCER": {
        "period": {"min": 7, "step": 1, "max": 28},
    },

    # === 4. VOLUME ===
    "OBV": {},
    "VWAP": {
        "period": {"min": 5, "step": 5, "max": 50},
    },
    "MFI": {
        "period": {"min": 7, "step": 1, "max": 28},
        "oversold": {"min": 15, "step": 5, "max": 30},
        "overbought": {"min": 70, "step": 5, "max": 85},
    },
    "ADI": {},
    "CMF": {
        "period": {"min": 10, "step": 2, "max": 35},
    },
    "FORCEINDEX": {
        "period": {"min": 5, "step": 2, "max": 25},
    },
    "EASEOFMOVEMENT": {
        "period": {"min": 7, "step": 1, "max": 25},
    },
    "NVI": {},
    "VPT": {},

    # === 5. RAW & PRICE ===
    "CLOSE": {},
    "OPEN": {},
    "HIGH": {},
    "LOW": {},
    "VOLUME": {},
}

def get_catalog_default_ranges(ind_name: str) -> dict[str, dict[str, float]]:
    """Retrieve default ranges for an indicator using fuzzy matching."""
    import re
    norm = re.sub(r"[\s_\-%]", "", ind_name).upper()
    for k, v in INDICATOR_CATALOG_DEFAULTS.items():
        if re.sub(r"[\s_\-%]", "", k).upper() == norm:
            return v
    return INDICATOR_CATALOG_DEFAULTS.get(ind_name.upper(), {})


TPSL_CATALOG_DEFAULTS: dict[str, dict[str, dict[str, float]]] = {
    "atr_classic": {
        "sl_atr": {"min": 0.5, "step": 0.1, "max": 3.0},
        "tp_atr": {"min": 0.5, "step": 0.1, "max": 6.0},
    },
    "trailing_stop": {
        "trail_atr": {"min": 0.5, "step": 0.1, "max": 2.5},
    },
    "swing_structure": {
        "lookback": {"min": 10, "step": 5, "max": 50},
    },
    "time_exit": {
        "max_bars": {"min": 5, "step": 1, "max": 12},
    },
    "percentage": {
        "sl_pct": {"min": 0.2, "step": 0.1, "max": 2.0},
        "tp_pct": {"min": 0.5, "step": 0.1, "max": 4.0},
    },
    "partial_tp": {
        "tp1_atr": {"min": 0.5, "step": 0.1, "max": 2.0},
        "tp2_atr": {"min": 2.0, "step": 0.1, "max": 6.0},
        "close_pct": {"min": 30, "step": 10, "max": 70},
    },
    "breakeven": {
        "be_atr": {"min": 0.5, "step": 0.1, "max": 2.0},
    },
    "fixed_pips": {
        "sl_pips": {"min": 10, "step": 5, "max": 50},
        "tp_pips": {"min": 20, "step": 5, "max": 100},
    },
    "smoothed_atr": {
        "sl_atr_smooth": {"min": 0.5, "step": 0.1, "max": 3.0},
        "tp_atr_smooth": {"min": 1.0, "step": 0.1, "max": 6.0},
    },
}

def get_tpsl_catalog_default_ranges(mode_id: str) -> dict[str, dict[str, float]]:
    """Retrieve default parameter ranges for a TP/SL mode."""
    import re
    norm = re.sub(r"[\s_\-%]", "", str(mode_id)).lower()
    for k, v in TPSL_CATALOG_DEFAULTS.items():
        if re.sub(r"[\s_\-%]", "", k).lower() == norm:
            return v
    return TPSL_CATALOG_DEFAULTS.get(str(mode_id).lower(), {})

