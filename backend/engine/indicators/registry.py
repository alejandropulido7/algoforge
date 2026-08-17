from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re

class IndicatorCategory(str, Enum):
    MOMENTUM = "momentum"
    TREND = "trend"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OTHERS = "others"

@dataclass
class IndicatorConfig:
    name: str
    category: IndicatorCategory
    func_name: str
    default_params: dict[str, Any] = field(default_factory=dict)
    param_ranges: dict[str, tuple[float, float]] = field(default_factory=dict)
    description: str = ""

INDICATOR_REGISTRY: dict[str, IndicatorConfig] = {
    # === MOMENTUM (11) ===
    "RSI": IndicatorConfig(
        name="RSI",
        category=IndicatorCategory.MOMENTUM,
        func_name="rsi",
        default_params={"window": 14},
        param_ranges={"window": (5, 50)},
        description="Relative Strength Index (RSI)"
    ),
    "STOCHASTIC": IndicatorConfig(
        name="Stochastic",
        category=IndicatorCategory.MOMENTUM,
        func_name="stoch",
        default_params={"window": 14, "smooth_window": 3},
        param_ranges={"window": (5, 30), "smooth_window": (2, 10)},
        description="Stochastic Oscillator (%K)"
    ),
    "STOCHRSI": IndicatorConfig(
        name="StochRSI",
        category=IndicatorCategory.MOMENTUM,
        func_name="stochrsi",
        default_params={"window": 14, "smooth1": 3, "smooth2": 3},
        param_ranges={"window": (5, 30), "smooth1": (2, 10), "smooth2": (2, 10)},
        description="Stochastic RSI"
    ),
    "TSI": IndicatorConfig(
        name="TSI",
        category=IndicatorCategory.MOMENTUM,
        func_name="tsi",
        default_params={"window_slow": 25, "window_fast": 13},
        param_ranges={"window_slow": (15, 50), "window_fast": (5, 20)},
        description="True Strength Index"
    ),
    "ULTIMATE OSCILLATOR": IndicatorConfig(
        name="Ultimate Oscillator",
        category=IndicatorCategory.MOMENTUM,
        func_name="ultimate",
        default_params={"window1": 7, "window2": 14, "window3": 28},
        param_ranges={"window1": (3, 15), "window2": (10, 30), "window3": (20, 50)},
        description="Ultimate Oscillator"
    ),
    "WILLIAMS %R": IndicatorConfig(
        name="Williams %R",
        category=IndicatorCategory.MOMENTUM,
        func_name="willr",
        default_params={"lbp": 14},
        param_ranges={"lbp": (5, 30)},
        description="Williams Percent Range"
    ),
    "AWESOME OSCILLATOR": IndicatorConfig(
        name="Awesome Oscillator",
        category=IndicatorCategory.MOMENTUM,
        func_name="ao",
        default_params={"window1": 5, "window2": 34},
        param_ranges={"window1": (3, 15), "window2": (20, 60)},
        description="Awesome Oscillator (AO)"
    ),
    "KAMA": IndicatorConfig(
        name="KAMA",
        category=IndicatorCategory.MOMENTUM,
        func_name="kama",
        default_params={"window": 10, "pow1": 2, "pow2": 30},
        param_ranges={"window": (5, 30)},
        description="Kaufman's Adaptive Moving Average"
    ),
    "ROC": IndicatorConfig(
        name="ROC",
        category=IndicatorCategory.MOMENTUM,
        func_name="roc",
        default_params={"window": 12},
        param_ranges={"window": (5, 30)},
        description="Rate of Change (ROC)"
    ),
    "PPO": IndicatorConfig(
        name="PPO",
        category=IndicatorCategory.MOMENTUM,
        func_name="ppo",
        default_params={"window_slow": 26, "window_fast": 12, "window_sign": 9},
        param_ranges={"window_slow": (20, 50), "window_fast": (5, 20), "window_sign": (5, 15)},
        description="Percentage Price Oscillator"
    ),
    "PVO": IndicatorConfig(
        name="PVO",
        category=IndicatorCategory.MOMENTUM,
        func_name="pvo",
        default_params={"window_slow": 26, "window_fast": 12, "window_sign": 9},
        param_ranges={"window_slow": (20, 50), "window_fast": (5, 20), "window_sign": (5, 15)},
        description="Percentage Volume Oscillator"
    ),

    # === TREND (15) ===
    "MACD": IndicatorConfig(
        name="MACD",
        category=IndicatorCategory.TREND,
        func_name="macd",
        default_params={"window_slow": 26, "window_fast": 12, "window_sign": 9},
        param_ranges={"window_slow": (20, 50), "window_fast": (5, 20), "window_sign": (5, 15)},
        description="Moving Average Convergence Divergence"
    ),
    "SMA": IndicatorConfig(
        name="SMA",
        category=IndicatorCategory.TREND,
        func_name="sma",
        default_params={"window": 20},
        param_ranges={"window": (5, 200)},
        description="Simple Moving Average"
    ),
    "EMA": IndicatorConfig(
        name="EMA",
        category=IndicatorCategory.TREND,
        func_name="ema",
        default_params={"window": 20},
        param_ranges={"window": (5, 200)},
        description="Exponential Moving Average"
    ),
    "WMA": IndicatorConfig(
        name="WMA",
        category=IndicatorCategory.TREND,
        func_name="wma",
        default_params={"window": 20},
        param_ranges={"window": (5, 100)},
        description="Weighted Moving Average"
    ),
    "HMA": IndicatorConfig(
        name="HMA",
        category=IndicatorCategory.TREND,
        func_name="hma",
        default_params={"window": 20},
        param_ranges={"window": (5, 100)},
        description="Hull Moving Average"
    ),
    "ADX": IndicatorConfig(
        name="ADX",
        category=IndicatorCategory.TREND,
        func_name="adx",
        default_params={"window": 14},
        param_ranges={"window": (7, 30)},
        description="Average Directional Movement Index"
    ),
    "AROON": IndicatorConfig(
        name="Aroon",
        category=IndicatorCategory.TREND,
        func_name="aroon",
        default_params={"window": 25},
        param_ranges={"window": (10, 50)},
        description="Aroon Oscillator"
    ),
    "CCI": IndicatorConfig(
        name="CCI",
        category=IndicatorCategory.TREND,
        func_name="cci",
        default_params={"window": 20},
        param_ranges={"window": (10, 50)},
        description="Commodity Channel Index"
    ),
    "PSAR": IndicatorConfig(
        name="PSAR",
        category=IndicatorCategory.TREND,
        func_name="psar",
        default_params={"step": 0.02, "max_step": 0.2},
        param_ranges={"step": (0.01, 0.05), "max_step": (0.1, 0.5)},
        description="Parabolic Stop and Reverse"
    ),
    "ICHIMOKU": IndicatorConfig(
        name="Ichimoku",
        category=IndicatorCategory.TREND,
        func_name="ichimoku",
        default_params={"window1": 9, "window2": 26, "window3": 52},
        param_ranges={"window1": (5, 15), "window2": (15, 40), "window3": (30, 80)},
        description="Ichimoku Kinko Hyo (Kijun-sen Base Line)"
    ),
    "KST": IndicatorConfig(
        name="KST",
        category=IndicatorCategory.TREND,
        func_name="kst",
        default_params={},
        param_ranges={},
        description="Know Sure Thing (KST) Oscillator"
    ),
    "DPO": IndicatorConfig(
        name="DPO",
        category=IndicatorCategory.TREND,
        func_name="dpo",
        default_params={"window": 20},
        param_ranges={"window": (10, 50)},
        description="Detrended Price Oscillator"
    ),
    "TRIX": IndicatorConfig(
        name="TRIX",
        category=IndicatorCategory.TREND,
        func_name="trix",
        default_params={"window": 15},
        param_ranges={"window": (5, 30)},
        description="Triple Exponential Moving Average Oscillator"
    ),
    "MASS INDEX": IndicatorConfig(
        name="Mass Index",
        category=IndicatorCategory.TREND,
        func_name="mass_index",
        default_params={"window_fast": 9, "window_slow": 25},
        param_ranges={"window_fast": (5, 15), "window_slow": (15, 40)},
        description="Mass Index"
    ),
    "VORTEX": IndicatorConfig(
        name="Vortex",
        category=IndicatorCategory.TREND,
        func_name="vortex",
        default_params={"window": 14},
        param_ranges={"window": (7, 30)},
        description="Vortex Indicator (VI+)"
    ),
    "STC": IndicatorConfig(
        name="STC",
        category=IndicatorCategory.TREND,
        func_name="stc",
        default_params={"window_slow": 50, "window_fast": 23, "cycle": 10},
        param_ranges={"window_slow": (30, 80), "window_fast": (10, 35), "cycle": (5, 20)},
        description="Schaff Trend Cycle"
    ),

    # === VOLATILITY (5) ===
    "ATR": IndicatorConfig(
        name="ATR",
        category=IndicatorCategory.VOLATILITY,
        func_name="atr",
        default_params={"window": 14},
        param_ranges={"window": (7, 30)},
        description="Average True Range"
    ),
    "BOLLINGER BANDS": IndicatorConfig(
        name="Bollinger Bands",
        category=IndicatorCategory.VOLATILITY,
        func_name="bbands",
        default_params={"window": 20, "window_dev": 2.0},
        param_ranges={"window": (10, 50), "window_dev": (1.0, 3.0)},
        description="Bollinger Bands (%B / Bandwidth)"
    ),
    "KELTNER CHANNEL": IndicatorConfig(
        name="Keltner Channel",
        category=IndicatorCategory.VOLATILITY,
        func_name="kc",
        default_params={"window": 20, "window_atr": 10, "multiplier": 2.0},
        param_ranges={"window": (10, 40), "multiplier": (1.0, 3.0)},
        description="Keltner Channels"
    ),
    "DONCHIAN CHANNEL": IndicatorConfig(
        name="Donchian Channel",
        category=IndicatorCategory.VOLATILITY,
        func_name="dc",
        default_params={"window": 20},
        param_ranges={"window": (10, 40)},
        description="Donchian Channel"
    ),
    "ULCER INDEX": IndicatorConfig(
        name="Ulcer Index",
        category=IndicatorCategory.VOLATILITY,
        func_name="ulcer",
        default_params={"window": 14},
        param_ranges={"window": (7, 30)},
        description="Ulcer Index (Drawdown Risk Indicator)"
    ),

    # === VOLUME (9) ===
    "OBV": IndicatorConfig(
        name="OBV",
        category=IndicatorCategory.VOLUME,
        func_name="obv",
        default_params={},
        param_ranges={},
        description="On-Balance Volume"
    ),
    "VWAP": IndicatorConfig(
        name="VWAP",
        category=IndicatorCategory.VOLUME,
        func_name="vwap",
        default_params={"window": 14},
        param_ranges={"window": (5, 50)},
        description="Volume Weighted Average Price"
    ),
    "MFI": IndicatorConfig(
        name="MFI",
        category=IndicatorCategory.VOLUME,
        func_name="mfi",
        default_params={"window": 14},
        param_ranges={"window": (7, 30)},
        description="Money Flow Index"
    ),
    "ADI": IndicatorConfig(
        name="ADI",
        category=IndicatorCategory.VOLUME,
        func_name="adi",
        default_params={},
        param_ranges={},
        description="Accumulation / Distribution Index"
    ),
    "CMF": IndicatorConfig(
        name="CMF",
        category=IndicatorCategory.VOLUME,
        func_name="cmf",
        default_params={"window": 20},
        param_ranges={"window": (10, 40)},
        description="Chaikin Money Flow"
    ),
    "FORCE INDEX": IndicatorConfig(
        name="Force Index",
        category=IndicatorCategory.VOLUME,
        func_name="force_index",
        default_params={"window": 13},
        param_ranges={"window": (5, 30)},
        description="Force Index"
    ),
    "EASE OF MOVEMENT": IndicatorConfig(
        name="Ease of Movement",
        category=IndicatorCategory.VOLUME,
        func_name="eom",
        default_params={"window": 14},
        param_ranges={"window": (5, 30)},
        description="Ease of Movement (EoM)"
    ),
    "NVI": IndicatorConfig(
        name="NVI",
        category=IndicatorCategory.VOLUME,
        func_name="nvi",
        default_params={},
        param_ranges={},
        description="Negative Volume Index"
    ),
    "VPT": IndicatorConfig(
        name="VPT",
        category=IndicatorCategory.VOLUME,
        func_name="vpt",
        default_params={},
        param_ranges={},
        description="Volume-Price Trend"
    ),

    # === RETURNS & OTHERS (3) ===
    "DAILY RETURN": IndicatorConfig(
        name="Daily Return",
        category=IndicatorCategory.OTHERS,
        func_name="daily_return",
        default_params={},
        param_ranges={},
        description="Daily Return Percentage"
    ),
    "DAILY LOG RETURN": IndicatorConfig(
        name="Daily Log Return",
        category=IndicatorCategory.OTHERS,
        func_name="daily_log_return",
        default_params={},
        param_ranges={},
        description="Daily Logarithmic Return"
    ),
    "CUMULATIVE RETURN": IndicatorConfig(
        name="Cumulative Return",
        category=IndicatorCategory.OTHERS,
        func_name="cum_return",
        default_params={},
        param_ranges={},
        description="Cumulative Return Percentage"
    ),
}

def normalize_key(name: str) -> str:
    return re.sub(r"[\s_\-%]", "", str(name)).upper()

_NORMALIZED_MAP = {normalize_key(k): v for k, v in INDICATOR_REGISTRY.items()}
_ALIAS_MAP = {
    "STOCH": "STOCHASTIC",
    "WILLR": "WILLIAMS %R",
    "WILLIAMS": "WILLIAMS %R",
    "BBANDS": "BOLLINGER BANDS",
    "BOLLINGER": "BOLLINGER BANDS",
    "KC": "KELTNER CHANNEL",
    "DC": "DONCHIAN CHANNEL",
    "AO": "AWESOME OSCILLATOR",
    "PARABOLIC SAR": "PSAR",
    "SAR": "PSAR",
    "EOM": "EASE OF MOVEMENT",
    "ACC DIST": "ADI",
    "ACCUMULATION DISTRIBUTION": "ADI",
}
for alias, target in _ALIAS_MAP.items():
    if target in INDICATOR_REGISTRY:
        _NORMALIZED_MAP[normalize_key(alias)] = INDICATOR_REGISTRY[target]

def get_indicator(name: str) -> IndicatorConfig | None:
    """Retrieve indicator config using case-insensitive, symbol-agnostic fuzzy matching."""
    norm = normalize_key(name)
    if norm in _NORMALIZED_MAP:
        return _NORMALIZED_MAP[norm]
    return INDICATOR_REGISTRY.get(name.upper()) or INDICATOR_REGISTRY.get(name)
