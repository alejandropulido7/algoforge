export interface DataSource {
  id: string;
  symbol: string;
  name?: string;
  timeframe: string;
  startDate?: string;
  endDate?: string;
  start_date?: string;
  end_date?: string;
  rowCount?: number;
  row_count?: number;
  source: 'yfinance' | 'csv' | 'mt5_csv' | string;
  createdAt?: string;
  created_at?: string;
}

export interface OHLCVBar {
  time: number | string;
  Timestamp?: string;
  Date?: string;
  open: number;
  Open?: number;
  high: number;
  High?: number;
  low: number;
  Low?: number;
  close: number;
  Close?: number;
  volume?: number;
  Volume?: number;
}
