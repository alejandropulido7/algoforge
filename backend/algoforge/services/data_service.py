import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
import re
import io
import urllib.request
import lzma
import struct
import concurrent.futures
from datetime import datetime, timedelta, date

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_storage")
os.makedirs(STORAGE_DIR, exist_ok=True)
INDEX_FILE = os.path.join(STORAGE_DIR, "datasets_index.json")

class DataService:
    """Service to fetch (Yahoo / Dukascopy), upload, parse MT5 CSVs, and cache OHLCV market data."""

    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "1h",
        "1d": "1d",
        "1w": "1wk"
    }

    @staticmethod
    def _normalize_date_str(val: str) -> str:
        if not val or str(val).strip() in ["N/A", "nan", "None", ""]:
            return ""
        s = str(val).strip().replace(".", "-").replace("/", "-")
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
        if m:
            y, mth, d = m.groups()
            return f"{int(y):04d}-{int(mth):02d}-{int(d):02d}"
        m2 = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})", s)
        if m2:
            d, mth, y = m2.groups()
            return f"{int(y):04d}-{int(mth):02d}-{int(d):02d}"
        try:
            dt = pd.to_datetime(s, errors="coerce")
            if pd.notnull(dt):
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
        return s[:10]

    @classmethod
    def _read_index(cls) -> list[dict]:
        if os.path.exists(INDEX_FILE):
            try:
                with open(INDEX_FILE, "r") as f:
                    data = json.load(f)
                    for item in data:
                        if "start_date" in item:
                            item["start_date"] = cls._normalize_date_str(item["start_date"])
                        if "end_date" in item:
                            item["end_date"] = cls._normalize_date_str(item["end_date"])
                    return data
            except Exception:
                return []
        return []

    @staticmethod
    def _write_index(index: list[dict]):
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f, indent=2)

    @staticmethod
    def _get_dukascopy_point(symbol: str) -> float:
        s = symbol.upper().replace("-", "").replace("/", "").replace("_", "")
        if any(k in s for k in ["JPY", "XAU", "GOLD", "30", "100", "500", "40", "OIL", "BRENT"]):
            return 1000.0
        elif any(k in s for k in ["BTC", "ETH", "CRYPTO"]):
            return 100.0
        elif "XAG" in s:
            return 10000.0
        return 100000.0

    @staticmethod
    def _map_dukascopy_instrument(symbol: str) -> str:
        s = symbol.upper().replace("/", "").replace("-", "").replace("=", "").replace("^", "").replace("_", "")
        mapping = {
            "EURUSD": "EUR/USD",
            "GBPUSD": "GBP/USD",
            "USDJPY": "USD/JPY",
            "AUDUSD": "AUD/USD",
            "USDCAD": "USD/CAD",
            "USDCHF": "USD/CHF",
            "NZDUSD": "NZD/USD",
            "EURGBP": "EUR/GBP",
            "EURJPY": "EUR/JPY",
            "GBPJPY": "GBP/JPY",
            "XAUUSD": "XAU/USD",
            "GOLD": "XAU/USD",
            "XAGUSD": "XAG/USD",
            "SILVER": "XAG/USD",
            "US30": "USA30.IDX/USD",
            "DJ30": "USA30.IDX/USD",
            "US500": "USA500.IDX/USD",
            "SP500": "USA500.IDX/USD",
            "NAS100": "USATECH.IDX/USD",
            "USTECH": "USATECH.IDX/USD",
            "GER40": "DEU.IDX/EUR",
            "DAX40": "DEU.IDX/EUR",
            "UK100": "GBR.IDX/GBP",
            "USOIL": "LIGHT.CMD/USD",
            "BRENT": "BRENT.CMD/USD",
            "BTCUSD": "BTC/USD",
            "ETHUSD": "ETH/USD"
        }
        if s in mapping:
            return mapping[s]
        if len(s) == 6:
            return f"{s[:3]}/{s[3:]}"
        return s

    def _fetch_dukascopy(
        self,
        symbol: str = "EURUSD",
        timeframe: str = "1h",
        start: str | None = None,
        end: str | None = None
    ) -> pd.DataFrame:
        """Download historical candles from Dukascopy API and format as OHLCV DataFrame."""
        try:
            import dukascopy_python as duka
        except ImportError:
            duka = None

        instrument = self._map_dukascopy_instrument(symbol)
        clean_sym = symbol.upper().replace("/", "").replace("-", "").replace("=", "").replace("^", "").replace("_", "")

        start_str = start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        end_str = end or datetime.now().strftime("%Y-%m-%d")

        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d")
            end_dt = datetime.strptime(end_str, "%Y-%m-%d")
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(days=1)
        except Exception:
            start_dt = datetime.now() - timedelta(days=365)
            end_dt = datetime.now()

        tf_map = {
            "1m": "1MIN",
            "5m": "5MIN",
            "15m": "15MIN",
            "30m": "30MIN",
            "1h": "1HOUR",
            "4h": "4HOUR",
            "1d": "1DAY",
            "1w": "1WEEK"
        }
        interval_code = tf_map.get(timeframe.lower(), "1HOUR")

        if duka is not None:
            try:
                df = duka.fetch(
                    instrument=instrument,
                    interval=interval_code,
                    offer_side=duka.OFFER_SIDE_BID,
                    start=start_dt,
                    end=end_dt,
                    limit=30000
                )
                if df is not None and len(df) > 0:
                    df = df.reset_index()
                    rename_cols = {}
                    for c in df.columns:
                        cl = c.lower()
                        if "time" in cl or "date" in cl:
                            rename_cols[c] = "Timestamp"
                        elif cl == "open":
                            rename_cols[c] = "Open"
                        elif cl == "high":
                            rename_cols[c] = "High"
                        elif cl == "low":
                            rename_cols[c] = "Low"
                        elif cl == "close":
                            rename_cols[c] = "Close"
                        elif cl in ["volume", "vol"]:
                            rename_cols[c] = "Volume"
                    df = df.rename(columns=rename_cols)
                    if "Timestamp" in df.columns:
                        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                    cols_to_keep = [c for c in ["Timestamp", "Open", "High", "Low", "Close", "Volume"] if c in df.columns]
                    df = df[cols_to_keep]

                    self._save_to_index(
                        symbol=clean_sym,
                        timeframe=timeframe,
                        df=df,
                        source="dukascopy",
                        name=f"{clean_sym} ({timeframe}) [Dukascopy]"
                    )
                    return df
            except Exception as e:
                print(f"[Dukascopy API fetch error]: {e}")

        return pd.DataFrame()

    def fetch_ohlcv(
        self,
        symbol: str = "BTC-USD",
        timeframe: str = "1d",
        start: str | None = None,
        end: str | None = None,
        source: str = "yfinance"
    ) -> pd.DataFrame:
        """Fetch OHLCV historical data as a pandas DataFrame."""
        if source == "dukascopy":
            df_duk = self._fetch_dukascopy(symbol=symbol, timeframe=timeframe, start=start, end=end)
            if df_duk is not None and len(df_duk) > 5:
                return df_duk

        if source == "csv":
            index = self._read_index()
            match = next((d for d in index if d["symbol"].upper() == symbol.upper() and d["timeframe"] == timeframe), None)
            if not match:
                match = next((d for d in index if d["symbol"].upper() == symbol.upper() or d["id"] == symbol), None)
            if match:
                raw_fp = match.get("filepath", "")
                csv_path = raw_fp if (raw_fp and os.path.exists(raw_fp)) else os.path.join(STORAGE_DIR, os.path.basename(raw_fp))
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                    if "Timestamp" in df.columns:
                        ts_clean = df["Timestamp"].astype(str).str.replace(".", "-", regex=False)
                        ts = pd.to_datetime(ts_clean, errors="coerce")
                        mask = pd.Series(True, index=df.index)
                        if start:
                            mask = mask & (ts >= pd.to_datetime(start))
                        if end:
                            mask = mask & (ts <= (pd.to_datetime(end) + pd.Timedelta(days=1)))
                        df_filtered = df[mask].reset_index(drop=True)
                        if len(df_filtered) > 5:
                            return df_filtered
                    return df
                except Exception as e:
                    print(f"[CSV load/filter error]: {e}")

        if source == "yfinance":
            try:
                interval = self.TIMEFRAME_MAP.get(timeframe, "1d")
                start_date = start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                end_date = end or datetime.now().strftime("%Y-%m-%d")
                
                df = yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    progress=False
                )
                if df is not None and len(df) > 5:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df = df.reset_index()
                    col_map = {c: str(c).capitalize() for c in df.columns}
                    df = df.rename(columns=col_map)
                    if 'Date' in df.columns:
                        df = df.rename(columns={'Date': 'Timestamp'})
                    elif 'Datetime' in df.columns:
                        df = df.rename(columns={'Datetime': 'Timestamp'})

                    self._save_to_index(
                        symbol=symbol.upper(),
                        timeframe=timeframe,
                        df=df,
                        source="yfinance",
                        name=f"{symbol.upper()} ({timeframe})"
                    )
                    return df
            except Exception as e:
                print(f"[yfinance error]: {e}")

        # Synthetic fallback
        dates = pd.date_range(start=start or "2023-01-01", periods=200, freq='D')
        np.random.seed(42)
        price = 100.0 + np.cumsum(np.random.randn(200) * 1.5)
        high = price + np.abs(np.random.randn(200) * 1.2)
        low = price - np.abs(np.random.randn(200) * 1.2)
        df_mock = pd.DataFrame({
            "Timestamp": [str(d)[:10] for d in dates],
            "Open": np.round(price - np.random.randn(200) * 0.3, 2),
            "High": np.round(high, 2),
            "Low": np.round(low, 2),
            "Close": np.round(price, 2),
            "Volume": np.random.randint(1000, 50000, size=200)
        })
        return df_mock

    def _save_to_index(self, symbol: str, timeframe: str, df: pd.DataFrame, source: str, name: str) -> dict:
        clean_sym = symbol.upper().replace("-", "_").replace("=", "_").replace("^", "_").replace(".", "_")
        dataset_id = f"{source}_{clean_sym}_{timeframe}".lower()
        csv_filename = f"{dataset_id}.csv"
        csv_path = os.path.join(STORAGE_DIR, csv_filename)
        df.to_csv(csv_path, index=False)

        start_date = self._normalize_date_str(str(df.iloc[0].get("Timestamp", df.iloc[0].get("Date", "N/A"))))
        end_date = self._normalize_date_str(str(df.iloc[-1].get("Timestamp", df.iloc[-1].get("Date", "N/A"))))

        record = {
            "id": dataset_id,
            "symbol": symbol.upper(),
            "name": name,
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "row_count": len(df),
            "source": source,
            "filepath": csv_path,
            "created_at": datetime.now().isoformat()
        }

        index = self._read_index()
        index = [d for d in index if d["id"] != dataset_id]
        index.insert(0, record)
        self._write_index(index)
        return record

    def parse_mt5_csv(self, file_content: bytes, filename: str) -> tuple[pd.DataFrame, str, str]:
        """
        Parse MT5 CSV export files.
        Handles:
        1. Tab-separated, Comma-separated, or Semicolon-separated.
        2. MT5 format: <DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>
        3. Standard headers: Date, Time, Open, High, Low, Close, Volume.
        """
        text = file_content.decode("utf-8", errors="ignore")
        sample_line = text.splitlines()[0] if text.splitlines() else ""
        
        # Detect delimiter
        delimiter = "\t" if "\t" in sample_line else (";" if ";" in sample_line else ",")
        df = pd.read_csv(io.StringIO(text), sep=delimiter)

        # Normalize column headers
        clean_cols = {}
        for c in df.columns:
            cleaned = re.sub(r"[<>\s]", "", str(c)).upper()
            clean_cols[c] = cleaned
        df = df.rename(columns=clean_cols)

        # Merge Date and Time into Timestamp if separate
        if "DATE" in df.columns and "TIME" in df.columns:
            df["Timestamp"] = df["DATE"].astype(str) + " " + df["TIME"].astype(str)
        elif "DATE" in df.columns:
            df["Timestamp"] = df["DATE"].astype(str)
        elif "TIME" in df.columns:
            df["Timestamp"] = df["TIME"].astype(str)
        elif "TIMESTAMP" in df.columns:
            df["Timestamp"] = df["TIMESTAMP"].astype(str)
        elif "DATETIME" in df.columns:
            df["Timestamp"] = df["DATETIME"].astype(str)
        else:
            df["Timestamp"] = df.iloc[:, 0].astype(str)

        rename_map = {}
        for col in df.columns:
            uc = col.upper()
            if uc == "OPEN": rename_map[col] = "Open"
            elif uc == "HIGH": rename_map[col] = "High"
            elif uc == "LOW": rename_map[col] = "Low"
            elif uc == "CLOSE": rename_map[col] = "Close"
            elif uc in ["VOL", "VOLUME", "TICKVOL"]: rename_map[col] = "Volume"

        df = df.rename(columns=rename_map)

        if "Volume" not in df.columns:
            df["Volume"] = 1000

        cols_to_keep = [c for c in ["Timestamp", "Open", "High", "Low", "Close", "Volume"] if c in df.columns]
        df = df[cols_to_keep]

        symbol = "CUSTOM"
        timeframe = "1d"

        # Regex to detect timeframe token
        tf_match = re.search(r"[-_\s]?(M1|M5|M15|M30|H1|H4|D1|W1|MN1|1m|5m|15m|30m|1h|4h|1d|1w)[-_\s.]?", filename, re.IGNORECASE)
        if tf_match:
            raw_tf = tf_match.group(1).upper()
            tf_map = {
                "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
                "H1": "1h", "H4": "4h", "D1": "1d", "W1": "1w", "MN1": "1M",
                "1M": "1m", "5M": "5m", "15M": "15m", "30M": "30m",
                "1H": "1h", "4H": "4h", "1D": "1d", "1W": "1w"
            }
            timeframe = tf_map.get(raw_tf, "1d")
            base_sym = filename[:tf_match.start()].strip(" _-.")
            if base_sym:
                symbol = base_sym.upper()
        else:
            base_sym = os.path.splitext(filename)[0].strip()
            if base_sym:
                symbol = base_sym.upper()

        return df, symbol, timeframe

    def upload_csv(self, file_content: bytes, user_id: str, filename: str) -> dict:
        """Process and save uploaded CSV to local datasets."""
        try:
            df, detected_symbol, detected_timeframe = self.parse_mt5_csv(file_content, filename)
            record = self._save_to_index(
                symbol=detected_symbol,
                timeframe=detected_timeframe,
                df=df,
                source="mt5_csv",
                name=f"{detected_symbol} ({detected_timeframe}) - {filename}"
            )
            return {
                "success": True,
                "dataset": record,
                "row_count": len(df),
                "columns": list(df.columns),
                "symbol": detected_symbol,
                "timeframe": detected_timeframe
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_datasets(self) -> list[dict]:
        """List all available stored datasets."""
        return self._read_index()

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset from storage."""
        index = self._read_index()
        target = next((d for d in index if d["id"] == dataset_id), None)
        if target:
            if os.path.exists(target.get("filepath", "")):
                try:
                    os.remove(target["filepath"])
                except Exception:
                    pass
            index = [d for d in index if d["id"] != dataset_id]
            self._write_index(index)
            return True
        return False

    @staticmethod
    def list_symbols(provider: str | None = None) -> list[dict]:
        """Return predefined list of active multi-market symbols filtered by provider."""
        all_symbols = [
            # Dukascopy Institutional Catalogs
            {"symbol": "EURUSD", "name": "EUR / USD (Euro / US Dollar)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "GBPUSD", "name": "GBP / USD (British Pound)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "USDJPY", "name": "USD / JPY (Japanese Yen)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "AUDUSD", "name": "AUD / USD (Australian Dollar)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "USDCAD", "name": "USD / CAD (Canadian Dollar)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "USDCHF", "name": "USD / CHF (Swiss Franc)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "NZDUSD", "name": "NZD / USD (New Zealand Dollar)", "type": "forex", "provider": "dukascopy", "category": "Forex Majors"},
            {"symbol": "EURGBP", "name": "EUR / GBP (Euro / British Pound)", "type": "forex", "provider": "dukascopy", "category": "Forex Minors"},
            {"symbol": "EURJPY", "name": "EUR / JPY (Euro / Japanese Yen)", "type": "forex", "provider": "dukascopy", "category": "Forex Minors"},
            {"symbol": "GBPJPY", "name": "GBP / JPY (British Pound / Yen)", "type": "forex", "provider": "dukascopy", "category": "Forex Minors"},
            {"symbol": "XAUUSD", "name": "XAU / USD (Gold Spot)", "type": "metal", "provider": "dukascopy", "category": "Metals & Commodities"},
            {"symbol": "XAGUSD", "name": "XAG / USD (Silver Spot)", "type": "metal", "provider": "dukascopy", "category": "Metals & Commodities"},
            {"symbol": "USOIL", "name": "WTI Light Crude Oil", "type": "commodity", "provider": "dukascopy", "category": "Metals & Commodities"},
            {"symbol": "BRENT", "name": "Brent Crude Oil", "type": "commodity", "provider": "dukascopy", "category": "Metals & Commodities"},
            {"symbol": "US30", "name": "US 30 (Wall Street 30 / Dow Jones)", "type": "index", "provider": "dukascopy", "category": "Indices"},
            {"symbol": "US500", "name": "US 500 (S&P 500 Index)", "type": "index", "provider": "dukascopy", "category": "Indices"},
            {"symbol": "NAS100", "name": "NAS 100 (US Tech 100 / Nasdaq)", "type": "index", "provider": "dukascopy", "category": "Indices"},
            {"symbol": "GER40", "name": "GER 40 (Germany DAX 40)", "type": "index", "provider": "dukascopy", "category": "Indices"},
            {"symbol": "UK100", "name": "UK 100 (FTSE 100 Index)", "type": "index", "provider": "dukascopy", "category": "Indices"},
            {"symbol": "BTCUSD", "name": "BTC / USD (Bitcoin)", "type": "crypto", "provider": "dukascopy", "category": "Cryptocurrency"},
            {"symbol": "ETHUSD", "name": "ETH / USD (Ethereum)", "type": "crypto", "provider": "dukascopy", "category": "Cryptocurrency"},

            # Yahoo Finance Catalogs
            {"symbol": "BTC-USD", "name": "Bitcoin / USD", "type": "crypto", "provider": "yfinance", "category": "Cryptocurrency"},
            {"symbol": "ETH-USD", "name": "Ethereum / USD", "type": "crypto", "provider": "yfinance", "category": "Cryptocurrency"},
            {"symbol": "SOL-USD", "name": "Solana / USD", "type": "crypto", "provider": "yfinance", "category": "Cryptocurrency"},
            {"symbol": "EURUSD=X", "name": "EUR / USD", "type": "forex", "provider": "yfinance", "category": "Forex"},
            {"symbol": "GBPUSD=X", "name": "GBP / USD", "type": "forex", "provider": "yfinance", "category": "Forex"},
            {"symbol": "USDJPY=X", "name": "USD / JPY", "type": "forex", "provider": "yfinance", "category": "Forex"},
            {"symbol": "AUDUSD=X", "name": "AUD / USD", "type": "forex", "provider": "yfinance", "category": "Forex"},
            {"symbol": "USDCAD=X", "name": "USD / CAD", "type": "forex", "provider": "yfinance", "category": "Forex"},
            {"symbol": "^NDX", "name": "NASDAQ 100", "type": "index", "provider": "yfinance", "category": "Indices"},
            {"symbol": "^GSPC", "name": "S&P 500", "type": "index", "provider": "yfinance", "category": "Indices"},
            {"symbol": "^DJI", "name": "Dow Jones Industrial Average", "type": "index", "provider": "yfinance", "category": "Indices"},
            {"symbol": "^RUT", "name": "Russell 2000", "type": "index", "provider": "yfinance", "category": "Indices"},
            {"symbol": "^VIX", "name": "CBOE Volatility Index", "type": "index", "provider": "yfinance", "category": "Indices"},
            {"symbol": "GC=F", "name": "Gold Futures (COMEX)", "type": "commodity", "provider": "yfinance", "category": "Commodities"},
            {"symbol": "SI=F", "name": "Silver Futures (COMEX)", "type": "commodity", "provider": "yfinance", "category": "Commodities"},
            {"symbol": "CL=F", "name": "Crude Oil WTI Futures", "type": "commodity", "provider": "yfinance", "category": "Commodities"},
            {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "type": "stock", "provider": "yfinance", "category": "Stocks"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock", "provider": "yfinance", "category": "Stocks"}
        ]
        if provider:
            return [s for s in all_symbols if s.get("provider") == provider]
        return all_symbols

data_service = DataService()
