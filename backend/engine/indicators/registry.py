from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re

class IndicatorCategory(str, Enum):
    MOMENTUM = "momentum"
    TREND = "trend"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OVERLAP = "overlap"

@dataclass
class IndicatorConfig:
    name: str
    category: IndicatorCategory
    func_name: str
    default_params: dict[str, Any] = field(default_factory=dict)
    param_ranges: dict[str, tuple[float, float]] = field(default_factory=dict)
    description: str = ""

INDICATOR_REGISTRY: dict[str, IndicatorConfig] = {
    # Momentum
    "RSI": IndicatorConfig(
        name="RSI",
        category=IndicatorCategory.MOMENTUM,
        func_name="rsi",
        default_params={"length": 14},
        param_ranges={"length": (5, 50)},
        description="Relative Strength Index"
    ),
    "MACD": IndicatorConfig(
        name="MACD",
        category=IndicatorCategory.MOMENTUM,
        func_name="macd",
        default_params={"fast": 12, "slow": 26, "signal": 9},
        param_ranges={"fast": (5, 20), "slow": (20, 50), "signal": (5, 15)},
        description="Moving Average Convergence Divergence"
    ),
    "STOCHASTIC": IndicatorConfig(
        name="Stochastic",
        category=IndicatorCategory.MOMENTUM,
        func_name="stoch",
        default_params={"k": 14, "d": 3, "smooth_k": 3},
        param_ranges={"k": (5, 25), "d": (2, 10)},
        description="Stochastic Oscillator"
    ),
    "WILLIAMS %R": IndicatorConfig(
        name="Williams %R",
        category=IndicatorCategory.MOMENTUM,
        func_name="willr",
        default_params={"length": 14},
        param_ranges={"length": (5, 30)},
        description="Williams Percent Range"
    ),
    "CCI": IndicatorConfig(
        name="CCI",
        category=IndicatorCategory.MOMENTUM,
        func_name="cci",
        default_params={"length": 20},
        param_ranges={"length": (10, 50)},
        description="Commodity Channel Index"
    ),
    "ROC": IndicatorConfig(
        name="ROC",
        category=IndicatorCategory.MOMENTUM,
        func_name="roc",
        default_params={"length": 10},
        param_ranges={"length": (5, 30)},
        description="Rate of Change"
    ),
    "AWESOME OSCILLATOR": IndicatorConfig(
        name="Awesome Oscillator",
        category=IndicatorCategory.MOMENTUM,
        func_name="ao",
        default_params={"window1": 5, "window2": 34},
        param_ranges={"window1": (3, 10), "window2": (20, 50)},
        description="Awesome Oscillator"
    ),

    # Trend
    "ADX": IndicatorConfig(
        name="ADX",
        category=IndicatorCategory.TREND,
        func_name="adx",
        default_params={"length": 14},
        param_ranges={"length": (7, 30)},
        description="Average Directional Movement Index"
    ),
    "AROON": IndicatorConfig(
        name="Aroon",
        category=IndicatorCategory.TREND,
        func_name="aroon",
        default_params={"length": 25},
        param_ranges={"length": (10, 50)},
        description="Aroon Oscillator"
    ),
    "PSAR": IndicatorConfig(
        name="PSAR",
        category=IndicatorCategory.TREND,
        func_name="psar",
        default_params={"af0": 0.02, "max_af": 0.2},
        param_ranges={"af0": (0.01, 0.05), "max_af": (0.1, 0.5)},
        description="Parabolic Stop and Reverse"
    ),
    "TRIX": IndicatorConfig(
        name="TRIX",
        category=IndicatorCategory.TREND,
        func_name="trix",
        default_params={"length": 15},
        param_ranges={"length": (5, 30)},
        description="Triple Exponential Moving Average Oscillator"
    ),

    # Volatility
    "BOLLINGER BANDS": IndicatorConfig(
        name="Bollinger Bands",
        category=IndicatorCategory.VOLATILITY,
        func_name="bbands",
        default_params={"length": 20, "std": 2.0},
        param_ranges={"length": (10, 50), "std": (1.0, 3.0)},
        description="Bollinger Bands"
    ),
    "ATR": IndicatorConfig(
        name="ATR",
        category=IndicatorCategory.VOLATILITY,
        func_name="atr",
        default_params={"length": 14},
        param_ranges={"length": (7, 30)},
        description="Average True Range"
    ),
    "KELTNER CHANNEL": IndicatorConfig(
        name="Keltner Channel",
        category=IndicatorCategory.VOLATILITY,
        func_name="kc",
        default_params={"length": 20, "scalar": 2},
        param_ranges={"length": (10, 40), "scalar": (1.0, 3.0)},
        description="Keltner Channels"
    ),
    "DONCHIAN CHANNEL": IndicatorConfig(
        name="Donchian Channel",
        category=IndicatorCategory.VOLATILITY,
        func_name="dc",
        default_params={"length": 20},
        param_ranges={"length": (10, 40)},
        description="Donchian Channel"
    ),

    # Volume
    "OBV": IndicatorConfig(
        name="OBV",
        category=IndicatorCategory.VOLUME,
        func_name="obv",
        default_params={},
        param_ranges={},
        description="On Balance Volume"
    ),
    "MFI": IndicatorConfig(
        name="MFI",
        category=IndicatorCategory.VOLUME,
        func_name="mfi",
        default_params={"length": 14},
        param_ranges={"length": (7, 30)},
        description="Money Flow Index"
    ),
    "VWAP": IndicatorConfig(
        name="VWAP",
        category=IndicatorCategory.VOLUME,
        func_name="vwap",
        default_params={"window": 14},
        param_ranges={"window": (5, 50)},
        description="Volume Weighted Average Price"
    ),

    # Overlap
    "SMA": IndicatorConfig(
        name="SMA",
        category=IndicatorCategory.OVERLAP,
        func_name="sma",
        default_params={"length": 20},
        param_ranges={"length": (5, 200)},
        description="Simple Moving Average"
    ),
    "EMA": IndicatorConfig(
        name="EMA",
        category=IndicatorCategory.OVERLAP,
        func_name="ema",
        default_params={"length": 20},
        param_ranges={"length": (5, 200)},
        description="Exponential Moving Average"
    ),
    "HMA": IndicatorConfig(
        name="HMA",
        category=IndicatorCategory.OVERLAP,
        func_name="hma",
        default_params={"length": 20},
        param_ranges={"length": (5, 100)},
        description="Hull Moving Average"
    ),
    "WMA": IndicatorConfig(
        name="WMA",
        category=IndicatorCategory.OVERLAP,
        func_name="wma",
        default_params={"length": 20},
        param_ranges={"length": (5, 100)},
        description="Weighted Moving Average"
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
}
for alias, target in _ALIAS_MAP.items():
    if target in INDICATOR_REGISTRY:
        _NORMALIZED_MAP[normalize_key(alias)] = INDICATOR_REGISTRY[target]

def get_indicator(name: str) -> IndicatorConfig | None:
    """Retrieve indicator config using case-insensitive, symbol-agnostic fuzzy matching."""
    norm = normalize_key(name)
    if norm in _NORMALIZED_MAP:
        return _NORMALIZED_MAP[norm]
    # Direct lookup
    return INDICATOR_REGISTRY.get(name.upper()) or INDICATOR_REGISTRY.get(name)
