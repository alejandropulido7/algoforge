import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Zap, RefreshCw, Rocket, Trash2, Database, AlertCircle, CheckCircle2 } from 'lucide-react';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Spinner from '../components/common/Spinner';
import Badge from '../components/common/Badge';
import { uploadCSV, fetchOHLCV, getDatasets, deleteDataset, getSymbols } from '../services/api';
import { useJobStore } from '../store/jobStore';
import type { DataSource } from '../types/data';
import styles from '../styles/pages.module.css';

const DataManager: React.FC = () => {
  const navigate = useNavigate();
  const { updateDataSource } = useJobStore();

  const [symbol, setSymbol] = useState('BTC-USD');
  const [timeframe, setTimeframe] = useState('1d');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  
  const [datasets, setDatasets] = useState<DataSource[]>([]);
  const [symbols, setSymbols] = useState<Array<{ symbol: string; name: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dsets, syms] = await Promise.all([getDatasets(), getSymbols()]);
      setDatasets(dsets);
      setSymbols(syms);
    } catch (err: any) {
      console.error('Error loading data manager items:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setNotification(null);
    try {
      const res = await uploadCSV(file);
      setNotification({
        type: 'success',
        message: `Successfully uploaded ${file.name}! Detected ${res.row_count} bars (Symbol: ${res.symbol}, Timeframe: ${res.timeframe}).`
      });
      await loadData();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: `Upload failed: ${err.message || 'Could not parse CSV file'}`
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    setUploading(true);
    setNotification(null);
    try {
      const res = await uploadCSV(file);
      setNotification({
        type: 'success',
        message: `Successfully imported ${file.name} (${res.row_count} bars, ${res.symbol} [${res.timeframe}]).`
      });
      await loadData();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: `Import failed: ${err.message || 'Invalid file format'}`
      });
    } finally {
      setUploading(false);
    }
  };

  const handleFetch = async () => {
    if (!symbol) return;
    setFetching(true);
    setNotification(null);
    try {
      const res = await fetchOHLCV({
        symbol: symbol.toUpperCase(),
        timeframe,
        startDate,
        endDate,
        source: 'yfinance'
      });
      setNotification({
        type: 'success',
        message: `Fetched ${res.row_count} bars for ${symbol.toUpperCase()} (${timeframe}) from Yahoo Finance.`
      });
      await loadData();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: `Fetch failed: ${err.message || 'Provider request failed'}`
      });
    } finally {
      setFetching(false);
    }
  };

  const handleDelete = async (datasetId: string) => {
    try {
      await deleteDataset(datasetId);
      setDatasets(prev => prev.filter(d => d.id !== datasetId));
    } catch (err: any) {
      alert('Failed to delete dataset: ' + err.message);
    }
  };

  const handleUseInStrategy = (dataset: DataSource) => {
    updateDataSource({
      symbol: dataset.symbol,
      timeframe: dataset.timeframe,
      startDate: dataset.startDate || dataset.start_date || '2023-01-01',
      endDate: dataset.endDate || dataset.end_date || '2024-01-01',
      source: dataset.source === 'yfinance' ? 'yfinance' : 'csv'
    });
    navigate('/jobs/new');
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <h2>Data Manager</h2>
          <p className={styles.subtitle}>Upload MetaTrader 5 CSVs or fetch live market data from providers.</p>
        </div>
      </div>

      {notification && (
        <div 
          className={`p-4 mb-6 rounded border flex items-center gap-3 ${
            notification.type === 'success' 
              ? 'bg-emerald/10 border-emerald text-emerald' 
              : 'bg-rose/10 border-rose text-rose'
          }`}
        >
          {notification.type === 'success' ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
          <span>{notification.message}</span>
        </div>
      )}

      <div className={styles.dataGrid}>
        {/* Upload Custom Data */}
        <div className={styles.uploadCard}>
          <div className="flex items-center gap-2 mb-2">
            <UploadCloud size={20} className="text-cyan" />
            <h3 className={styles.cardTitle} style={{ margin: 0 }}>Upload Custom Data (MetaTrader 5 / CSV)</h3>
          </div>
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".csv,.txt,.tsv" 
            style={{ display: 'none' }} 
          />

          <div 
            className={styles.dropzone}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{ cursor: 'pointer' }}
          >
            {uploading ? (
              <div className="flex flex-col items-center gap-3">
                <Spinner size="lg" />
                <p>Parsing and indexing OHLCV bars...</p>
              </div>
            ) : (
              <>
                <UploadCloud size={48} className="text-cyan mb-2" strokeWidth={1.5} />
                <p className="font-semibold text-primary">Click to Browse or Drag & Drop MT5 CSV</p>
                <span className={styles.dropzoneHint}>
                  Supports MT5 History Center exports (e.g. <code>EURUSD_H1.csv</code>, <code>NAS100_M15.csv</code>, tabs or commas).
                </span>
                <Button variant="secondary" className="mt-4" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                  Select File from Computer
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Fetch from Live Provider */}
        <div className={styles.fetchCard}>
          <div className="flex items-center gap-2 mb-2">
            <Database size={20} className="text-cyan" />
            <h3 className={styles.cardTitle} style={{ margin: 0 }}>Fetch Live Provider Data</h3>
          </div>
          <div className={styles.formGrid}>
            <div>
              <Input 
                label="Symbol" 
                placeholder="e.g. BTC-USD, EURUSD=X, AAPL" 
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
              />
              {symbols.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {symbols.slice(0, 5).map(s => (
                    <button
                      key={s.symbol}
                      type="button"
                      className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black rounded transition"
                      onClick={() => setSymbol(s.symbol)}
                    >
                      {s.symbol}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <Select 
              label="Timeframe"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              options={[
                {label: '1 Minute (1m)', value: '1m'},
                {label: '5 Minutes (5m)', value: '5m'},
                {label: '15 Minutes (15m)', value: '15m'},
                {label: '1 Hour (1h)', value: '1h'},
                {label: '1 Day (1d)', value: '1d'},
                {label: '1 Week (1w)', value: '1w'}
              ]}
            />

            <Input 
              type="date"
              label="Start Date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />

            <Input 
              type="date"
              label="End Date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />

            <div style={{gridColumn: '1 / -1'}}>
              <Button 
                variant="primary" 
                className="w-full flex items-center justify-center gap-2"
                onClick={handleFetch}
                disabled={fetching}
              >
                {fetching ? (
                  <>
                    <Spinner size="sm" /> 
                    <span>Fetching Market Data...</span>
                  </>
                ) : (
                  <>
                    <Zap size={16} />
                    <span>Fetch from Provider & Cache</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Available Datasets Table */}
      <div className={styles.tableCard}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <Database size={18} className="text-cyan" />
            <h3 className={styles.tableTitle} style={{ margin: 0 }}>Available Datasets ({datasets.length})</h3>
          </div>
          <Button variant="ghost" size="sm" onClick={loadData} className="flex items-center gap-1">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </Button>
        </div>

        {loading ? (
          <div className="py-12 flex justify-center"><Spinner size="lg" /></div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Source</th>
                  <th>Timeframe</th>
                  <th>Date Range</th>
                  <th>Bars (Rows)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasets.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-secondary">
                      No datasets available yet. Upload a MetaTrader 5 CSV above or fetch data from Yahoo Finance.
                    </td>
                  </tr>
                ) : (
                  datasets.map(d => (
                    <tr key={d.id}>
                      <td className="font-bold text-primary">{d.symbol}</td>
                      <td>
                        <Badge variant={d.source === 'mt5_csv' ? 'success' : 'info'}>
                          {d.source === 'mt5_csv' ? 'MT5 CSV' : d.source.toUpperCase()}
                        </Badge>
                      </td>
                      <td>
                        <span className="font-mono text-cyan">{d.timeframe}</span>
                      </td>
                      <td className="text-xs text-secondary">
                        {d.startDate || d.start_date || 'N/A'} → {d.endDate || d.end_date || 'N/A'}
                      </td>
                      <td className="font-mono">{d.rowCount || d.row_count || 0}</td>
                      <td>
                        <div className="flex gap-2">
                          <Button 
                            variant="primary" 
                            size="sm"
                            onClick={() => handleUseInStrategy(d)}
                            className="flex items-center gap-1"
                          >
                            <Rocket size={14} />
                            <span>Build Strategy</span>
                          </Button>
                          <Button 
                            variant="danger" 
                            size="sm"
                            onClick={() => handleDelete(d.id)}
                            className="flex items-center gap-1"
                          >
                            <Trash2 size={14} />
                            <span>Delete</span>
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataManager;
