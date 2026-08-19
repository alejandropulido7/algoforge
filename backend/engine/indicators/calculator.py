import pandas as pd
import numpy as np
from .registry import INDICATOR_REGISTRY, get_indicator

class IndicatorCalculator:
    """Calculates 40+ technical indicators on standard OHLCV DataFrames using the 'ta' package."""

    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to Open, High, Low, Close, Volume."""
        col_map = {}
        for c in df.columns:
            cl = str(c).lower()
            if cl == 'open': col_map[c] = 'Open'
            elif cl == 'high': col_map[c] = 'High'
            elif cl == 'low': col_map[c] = 'Low'
            elif cl == 'close': col_map[c] = 'Close'
            elif cl in ['volume', 'vol', 'tickvol', 'tick_volume']: col_map[c] = 'Volume'
        df_norm = df.rename(columns=col_map).copy()
        if 'Close' not in df_norm.columns and len(df_norm.columns) > 0:
            df_norm['Close'] = df_norm.iloc[:, 0]
        if 'High' not in df_norm.columns:
            df_norm['High'] = df_norm['Close']
        if 'Low' not in df_norm.columns:
            df_norm['Low'] = df_norm['Close']
        if 'Open' not in df_norm.columns:
            df_norm['Open'] = df_norm['Close']
        if 'Volume' not in df_norm.columns:
            df_norm['Volume'] = pd.Series(np.ones(len(df_norm)) * 1000.0, index=df_norm.index)
        return df_norm

    @classmethod
    def calculate_single(cls, df: pd.DataFrame, indicator_name: str, params: dict | None = None) -> np.ndarray | pd.Series | None:
        """Calculate one indicator by name and parameters using the 'ta' library."""
        df_norm = cls.normalize_columns(df)
        ind_cfg = get_indicator(indicator_name)
        func_name = ind_cfg.func_name if ind_cfg else indicator_name.lower().replace(" ", "").replace("%", "")
        effective_params = dict(ind_cfg.default_params) if ind_cfg else {}
        if params:
            effective_params.update(params)

        close = df_norm['Close']
        high = df_norm['High']
        low = df_norm['Low']
        volume = df_norm['Volume']

        # Raw price series (no transformation). Parity: the MQL5 exporter
        # reads them from CopyClose/CopyOpen/CopyHigh/CopyLow/CopyTickVolume.
        if func_name in ("close", "open", "high", "low", "volume", "tick_volume"):
            col = {"close": "Close", "open": "Open", "high": "High", "low": "Low",
                   "volume": "Volume", "tick_volume": "Volume"}[func_name]
            return df_norm[col]

        try:
            # === 1. MOMENTUM ===
            if func_name == 'rsi':
                w = int(effective_params.get('window', 14))
                from ta.momentum import RSIIndicator
                return RSIIndicator(close=close, window=w).rsi()

            elif func_name == 'stoch':
                w = int(effective_params.get('window', 14))
                s = int(effective_params.get('smooth_window', 3))
                from ta.momentum import StochasticOscillator
                return StochasticOscillator(high=high, low=low, close=close, window=w, smooth_window=s).stoch()

            elif func_name == 'stochrsi':
                w = int(effective_params.get('window', 14))
                s1 = int(effective_params.get('smooth1', 3))
                s2 = int(effective_params.get('smooth2', 3))
                from ta.momentum import StochRSIIndicator
                return StochRSIIndicator(close=close, window=w, smooth1=s1, smooth2=s2).stochrsi()

            elif func_name == 'tsi':
                ws = int(effective_params.get('window_slow', 25))
                wf = int(effective_params.get('window_fast', 13))
                from ta.momentum import TSIIndicator
                return TSIIndicator(close=close, window_slow=ws, window_fast=wf).tsi()

            elif func_name == 'ultimate':
                w1 = int(effective_params.get('window1', 7))
                w2 = int(effective_params.get('window2', 14))
                w3 = int(effective_params.get('window3', 28))
                from ta.momentum import UltimateOscillator
                return UltimateOscillator(high=high, low=low, close=close, window1=w1, window2=w2, window3=w3).ultimate_oscillator()

            elif func_name == 'willr':
                l = int(effective_params.get('lbp', effective_params.get('window', 14)))
                from ta.momentum import WilliamsRIndicator
                return WilliamsRIndicator(high=high, low=low, close=close, lbp=l).williams_r()

            elif func_name == 'ao':
                w1 = int(effective_params.get('window1', 5))
                w2 = int(effective_params.get('window2', 34))
                from ta.momentum import AwesomeOscillatorIndicator
                return AwesomeOscillatorIndicator(high=high, low=low, window1=w1, window2=w2).awesome_oscillator()

            elif func_name == 'kama':
                w = int(effective_params.get('window', 10))
                p1 = int(effective_params.get('pow1', 2))
                p2 = int(effective_params.get('pow2', 30))
                from ta.momentum import KAMAIndicator
                return KAMAIndicator(close=close, window=w, pow1=p1, pow2=p2).kama()

            elif func_name == 'roc':
                w = int(effective_params.get('window', 12))
                from ta.momentum import ROCIndicator
                return ROCIndicator(close=close, window=w).roc()

            elif func_name == 'ppo':
                ws = int(effective_params.get('window_slow', 26))
                wf = int(effective_params.get('window_fast', 12))
                w_sign = int(effective_params.get('window_sign', 9))
                from ta.momentum import PercentagePriceOscillator
                return PercentagePriceOscillator(close=close, window_slow=ws, window_fast=wf, window_sign=w_sign).ppo()

            elif func_name == 'pvo':
                ws = int(effective_params.get('window_slow', 26))
                wf = int(effective_params.get('window_fast', 12))
                w_sign = int(effective_params.get('window_sign', 9))
                from ta.momentum import PercentageVolumeOscillator
                return PercentageVolumeOscillator(volume=volume, window_slow=ws, window_fast=wf, window_sign=w_sign).pvo()

            # === 2. TREND ===
            elif func_name == 'macd':
                ws = int(effective_params.get('window_slow', 26))
                wf = int(effective_params.get('window_fast', 12))
                w_sign = int(effective_params.get('window_sign', 9))
                from ta.trend import MACD
                return MACD(close=close, window_slow=ws, window_fast=wf, window_sign=w_sign).macd_diff()

            elif func_name == 'sma':
                w = int(effective_params.get('window', effective_params.get('length', 20)))
                from ta.trend import SMAIndicator
                return SMAIndicator(close=close, window=w).sma_indicator()

            elif func_name == 'ema':
                w = int(effective_params.get('window', effective_params.get('length', 20)))
                from ta.trend import EMAIndicator
                return EMAIndicator(close=close, window=w).ema_indicator()

            elif func_name == 'wma':
                w = int(effective_params.get('window', effective_params.get('length', 20)))
                from ta.trend import WMAIndicator
                return WMAIndicator(close=close, window=w).wma()

            elif func_name == 'hma':
                w = int(effective_params.get('window', effective_params.get('length', 20)))
                wma_half = close.rolling(window=max(1, w // 2)).mean()
                wma_full = close.rolling(window=w).mean()
                diff = 2 * wma_half - wma_full
                return diff.rolling(window=int(np.sqrt(w))).mean()

            elif func_name == 'adx':
                w = int(effective_params.get('window', effective_params.get('length', 14)))
                from ta.trend import ADXIndicator
                return ADXIndicator(high=high, low=low, close=close, window=w).adx()

            elif func_name == 'aroon':
                w = int(effective_params.get('window', effective_params.get('length', 25)))
                from ta.trend import AroonIndicator
                return AroonIndicator(high=high, low=low, window=w).aroon_indicator()

            elif func_name == 'cci':
                w = int(effective_params.get('window', effective_params.get('length', 20)))
                from ta.trend import CCIIndicator
                return CCIIndicator(high=high, low=low, close=close, window=w).cci()

            elif func_name == 'psar':
                step = float(effective_params.get('step', effective_params.get('af0', 0.02)))
                max_step = float(effective_params.get('max_step', effective_params.get('max_af', 0.2)))
                from ta.trend import PSARIndicator
                return PSARIndicator(high=high, low=low, close=close, step=step, max_step=max_step).psar()

            elif func_name == 'ichimoku':
                w1 = int(effective_params.get('window1', 9))
                w2 = int(effective_params.get('window2', 26))
                w3 = int(effective_params.get('window3', 52))
                from ta.trend import IchimokuIndicator
                return IchimokuIndicator(high=high, low=low, window1=w1, window2=w2, window3=w3).ichimoku_base_line()

            elif func_name == 'kst':
                from ta.trend import KSTIndicator
                return KSTIndicator(close=close).kst()

            elif func_name == 'dpo':
                w = int(effective_params.get('window', 20))
                from ta.trend import DPOIndicator
                return DPOIndicator(close=close, window=w).dpo()

            elif func_name == 'trix':
                w = int(effective_params.get('window', 15))
                from ta.trend import TRIXIndicator
                return TRIXIndicator(close=close, window=w).trix()

            elif func_name == 'mass_index':
                wf = int(effective_params.get('window_fast', 9))
                ws = int(effective_params.get('window_slow', 25))
                from ta.trend import MassIndex
                return MassIndex(high=high, low=low, window_fast=wf, window_slow=ws).mass_index()

            elif func_name == 'vortex':
                w = int(effective_params.get('window', 14))
                from ta.trend import VortexIndicator
                return VortexIndicator(high=high, low=low, close=close, window=w).vortex_indicator_pos()

            elif func_name == 'stc':
                ws = int(effective_params.get('window_slow', 50))
                wf = int(effective_params.get('window_fast', 23))
                cycle = int(effective_params.get('cycle', 10))
                from ta.trend import STCIndicator
                return STCIndicator(close=close, window_slow=ws, window_fast=wf, cycle=cycle).stc()

            # === 3. VOLATILITY ===
            elif func_name == 'atr':
                w = int(effective_params.get('window', 14))
                from ta.volatility import AverageTrueRange
                return AverageTrueRange(high=high, low=low, close=close, window=w).average_true_range()

            elif func_name == 'bbands':
                w = int(effective_params.get('window', 20))
                std = float(effective_params.get('window_dev', effective_params.get('std', 2.0)))
                from ta.volatility import BollingerBands
                return BollingerBands(close=close, window=w, window_dev=std).bollinger_pband()

            elif func_name == 'kc':
                w = int(effective_params.get('window', 20))
                w_atr = int(effective_params.get('window_atr', 10))
                mult = float(effective_params.get('multiplier', effective_params.get('scalar', 2.0)))
                from ta.volatility import KeltnerChannel
                return KeltnerChannel(high=high, low=low, close=close, window=w, window_atr=w_atr, multiplier=mult).keltner_channel_pband()

            elif func_name == 'dc':
                w = int(effective_params.get('window', 20))
                from ta.volatility import DonchianChannel
                return DonchianChannel(high=high, low=low, close=close, window=w).donchian_channel_pband()

            elif func_name == 'ulcer':
                w = int(effective_params.get('window', 14))
                from ta.volatility import UlcerIndex
                return UlcerIndex(close=close, window=w).ulcer_index()

            # === 4. VOLUME ===
            elif func_name == 'obv':
                from ta.volume import OnBalanceVolumeIndicator
                return OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()

            elif func_name == 'vwap':
                w = int(effective_params.get('window', 14))
                from ta.volume import VolumeWeightedAveragePrice
                return VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume, window=w).volume_weighted_average_price()

            elif func_name == 'mfi':
                w = int(effective_params.get('window', 14))
                from ta.volume import MFIIndicator
                return MFIIndicator(high=high, low=low, close=close, volume=volume, window=w).money_flow_index()

            elif func_name == 'adi':
                from ta.volume import AccDistIndexIndicator
                return AccDistIndexIndicator(high=high, low=low, close=close, volume=volume).acc_dist_index()

            elif func_name == 'cmf':
                w = int(effective_params.get('window', 20))
                from ta.volume import ChaikinMoneyFlowIndicator
                return ChaikinMoneyFlowIndicator(high=high, low=low, close=close, volume=volume, window=w).chaikin_money_flow()

            elif func_name == 'force_index':
                w = int(effective_params.get('window', 13))
                from ta.volume import ForceIndexIndicator
                return ForceIndexIndicator(close=close, volume=volume, window=w).force_index()

            elif func_name == 'eom':
                w = int(effective_params.get('window', 14))
                from ta.volume import EaseOfMovementIndicator
                return EaseOfMovementIndicator(high=high, low=low, volume=volume, window=w).ease_of_movement()

            elif func_name == 'nvi':
                from ta.volume import NegativeVolumeIndexIndicator
                return NegativeVolumeIndexIndicator(close=close, volume=volume).negative_volume_index()

            elif func_name == 'vpt':
                from ta.volume import VolumePriceTrendIndicator
                return VolumePriceTrendIndicator(close=close, volume=volume).volume_price_trend()

            # === 5. RETURNS & OTHERS ===
            elif func_name == 'daily_return':
                from ta.others import DailyReturnIndicator
                return DailyReturnIndicator(close=close).daily_return()

            elif func_name == 'daily_log_return':
                from ta.others import DailyLogReturnIndicator
                return DailyLogReturnIndicator(close=close).daily_log_return()

            elif func_name == 'cum_return':
                from ta.others import CumulativeReturnIndicator
                return CumulativeReturnIndicator(close=close).cumulative_return()

        except Exception as err:
            print(f"[Indicator calculation fallback for {indicator_name}]: {err}")
            return close.rolling(window=14).mean()

        return close.rolling(window=14).mean()

    @classmethod
    def calculate_all(cls, df: pd.DataFrame, selected_indicators: list) -> dict[str, np.ndarray]:
        """Calculate all selected indicators, returning clean 1D numpy arrays."""
        df_norm = cls.normalize_columns(df)
        results = {}
        for item in selected_indicators:
            if isinstance(item, str):
                name = item
                params = {}
            elif isinstance(item, dict):
                name = item.get("name", "")
                params = item.get("params", {})
            else:
                continue

            val = cls.calculate_single(df_norm, name, params)
            if val is not None:
                if isinstance(val, (pd.Series, pd.DataFrame)):
                    # NOTE: warmup values are NaN in the ta library. We fill with
                    # 0 (like an MT5 buffer that has no value yet) instead of
                    # bfill(), which used FUTURE data (lookahead bias) to fabricate
                    # indicator values at the start of the dataset.
                    arr = val.fillna(0).to_numpy()
                    results[name] = np.nan_to_num(arr)
                elif isinstance(val, np.ndarray):
                    results[name] = np.nan_to_num(val)
        return results

calculate_single = IndicatorCalculator.calculate_single
calculate_all = IndicatorCalculator.calculate_all
