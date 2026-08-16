import pandas as pd
import numpy as np
from .registry import INDICATOR_REGISTRY, get_indicator

class IndicatorCalculator:
    """Calculates technical indicators on standard OHLCV DataFrames using the 'ta' package."""

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

        try:
            # 1. Momentum
            if func_name == 'rsi':
                l = int(effective_params.get('length', 14))
                from ta.momentum import RSIIndicator
                return RSIIndicator(close=close, window=l).rsi()

            elif func_name == 'macd':
                f = int(effective_params.get('fast', 12))
                s = int(effective_params.get('slow', 26))
                sig = int(effective_params.get('signal', 9))
                from ta.trend import MACD
                macd_ind = MACD(close=close, window_fast=f, window_slow=s, window_sign=sig)
                return macd_ind.macd_diff()

            elif func_name == 'stoch':
                k = int(effective_params.get('k', 14))
                d = int(effective_params.get('d', 3))
                from ta.momentum import StochasticOscillator
                return StochasticOscillator(high=high, low=low, close=close, window=k, smooth_window=d).stoch()

            elif func_name == 'willr':
                l = int(effective_params.get('length', 14))
                from ta.momentum import WilliamsRIndicator
                return WilliamsRIndicator(high=high, low=low, close=close, lbp=l).williams_r()

            elif func_name == 'cci':
                l = int(effective_params.get('length', 20))
                from ta.trend import CCIIndicator
                return CCIIndicator(high=high, low=low, close=close, window=l).cci()

            elif func_name == 'roc':
                l = int(effective_params.get('length', 10))
                from ta.momentum import ROCIndicator
                return ROCIndicator(close=close, window=l).roc()

            elif func_name == 'ao':
                w1 = int(effective_params.get('window1', 5))
                w2 = int(effective_params.get('window2', 34))
                from ta.momentum import AwesomeOscillatorIndicator
                return AwesomeOscillatorIndicator(high=high, low=low, window1=w1, window2=w2).awesome_oscillator()

            # 2. Trend
            elif func_name == 'sma':
                l = int(effective_params.get('length', 20))
                from ta.trend import SMAIndicator
                return SMAIndicator(close=close, window=l).sma_indicator()

            elif func_name == 'ema':
                l = int(effective_params.get('length', 20))
                from ta.trend import EMAIndicator
                return EMAIndicator(close=close, window=l).ema_indicator()

            elif func_name == 'adx':
                l = int(effective_params.get('length', 14))
                from ta.trend import ADXIndicator
                return ADXIndicator(high=high, low=low, close=close, window=l).adx()

            elif func_name == 'aroon':
                l = int(effective_params.get('length', 25))
                from ta.trend import AroonIndicator
                return AroonIndicator(high=high, low=low, window=l).aroon_indicator()

            elif func_name == 'psar':
                af0 = float(effective_params.get('af0', 0.02))
                max_af = float(effective_params.get('max_af', 0.2))
                from ta.trend import PSARIndicator
                return PSARIndicator(high=high, low=low, close=close, step=af0, max_step=max_af).psar()

            elif func_name == 'trix':
                l = int(effective_params.get('length', 15))
                from ta.trend import TRIXIndicator
                return TRIXIndicator(close=close, window=l).trix()

            # 3. Volatility
            elif func_name == 'bbands':
                l = int(effective_params.get('length', 20))
                std = float(effective_params.get('std', 2.0))
                from ta.volatility import BollingerBands
                bb = BollingerBands(close=close, window=l, window_dev=std)
                return bb.bollinger_pband()

            elif func_name == 'atr':
                l = int(effective_params.get('length', 14))
                from ta.volatility import AverageTrueRange
                return AverageTrueRange(high=high, low=low, close=close, window=l).average_true_range()

            elif func_name == 'kc':
                l = int(effective_params.get('length', 20))
                from ta.volatility import KeltnerChannel
                return KeltnerChannel(high=high, low=low, close=close, window=l).keltner_channel_pband()

            elif func_name == 'dc':
                l = int(effective_params.get('length', 20))
                from ta.volatility import DonchianChannel
                return DonchianChannel(high=high, low=low, close=close, window=l).donchian_channel_pband()

            # 4. Volume
            elif func_name == 'obv':
                from ta.volume import OnBalanceVolumeIndicator
                return OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()

            elif func_name == 'mfi':
                l = int(effective_params.get('length', 14))
                from ta.volume import MFIIndicator
                return MFIIndicator(high=high, low=low, close=close, volume=volume, window=l).money_flow_index()

            elif func_name == 'vwap':
                w = int(effective_params.get('window', 14))
                from ta.volume import VolumeWeightedAveragePrice
                return VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume, window=w).volume_weighted_average_price()

            # 5. Overlap
            elif func_name == 'wma':
                from ta.trend import WMAIndicator
                l = int(effective_params.get('length', 20))
                return WMAIndicator(close=close, window=l).wma()

            elif func_name == 'hma':
                l = int(effective_params.get('length', 20))
                # Hull Moving Average calculation
                wma_half = close.rolling(window=max(1, l // 2)).mean()
                wma_full = close.rolling(window=l).mean()
                diff = 2 * wma_half - wma_full
                hma = diff.rolling(window=int(np.sqrt(l))).mean()
                return hma

        except Exception as err:
            print(f"[Indicator calculation fallback for {indicator_name}]: {err}")
            l = int(effective_params.get('length', 14))
            return close.rolling(window=max(2, l)).mean()

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
                    arr = val.bfill().fillna(0).to_numpy()
                    results[name] = np.nan_to_num(arr)
                elif isinstance(val, np.ndarray):
                    results[name] = np.nan_to_num(val)
        return results

calculate_single = IndicatorCalculator.calculate_single
calculate_all = IndicatorCalculator.calculate_all
