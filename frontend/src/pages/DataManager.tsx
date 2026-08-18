import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, Zap, RefreshCw, Rocket, Trash2, Database, AlertCircle, CheckCircle2, Search, ChevronDown } from 'lucide-react';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Spinner from '../components/common/Spinner';
import Badge from '../components/common/Badge';
import { uploadCSV, fetchOHLCV, getDatasets, deleteDataset, getSymbols, type SymbolItem } from '../services/api';
import { useJobStore } from '../store/jobStore';
import type { DataSource } from '../types/data';
import styles from '../styles/pages.module.css';

const DataManager: React.FC = () => {
  const navigate = useNavigate();
  const { updateDataSource } = useJobStore();

  const [provider, setProvider] = useState<'yfinance' | 'dukascopy'>('dukascopy');
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('1h');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  
  const [datasets, setDatasets] = useState<DataSource[]>([]);
  const [symbols, setSymbols] = useState<SymbolItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const providerSymbols = useMemo(() => {
    return symbols.filter(s => s.provider === provider);
  }, [symbols, provider]);

  const filteredSymbols = useMemo(() => {
    if (!searchQuery.trim()) return providerSymbols;
    const q = searchQuery.toLowerCase();
    return providerSymbols.filter(s => 
      s.symbol.toLowerCase().includes(q) || 
      s.name.toLowerCase().includes(q) || 
      (s.category && s.category.toLowerCase().includes(q))
    );
  }, [providerSymbols, searchQuery]);

  const groupedSymbols = useMemo(() => {
    const groups: Record<string, SymbolItem[]> = {};
    filteredSymbols.forEach(s => {
      const cat = s.category || 'General';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(s);
    });
    return groups;
  }, [filteredSymbols]);

  const handleSelectSymbol = (sym: string) => {
    setSymbol(sym.toUpperCase());
    setSearchQuery('');
    setIsDropdownOpen(false);
  };

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
        source: provider
      });
      const providerName = provider === 'dukascopy' ? 'Dukascopy (Institutional Feed)' : 'Yahoo Finance';
      setNotification({
        type: 'success',
        message: `Descargadas ${res.row_count} barras para ${symbol.toUpperCase()} (${timeframe}) desde ${providerName}.`
      });
      await loadData();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: `Fetch fallido: ${err.message || 'Error consultando al proveedor'}`
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

  const normalizeDate = (val?: string): string => {
    if (!val) return '';
    const clean = val.replace(/\./g, '-').replace(/\//g, '-').trim();
    const matchIso = clean.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (matchIso) {
      const [, y, m, d] = matchIso;
      return `${y.padStart(4, '0')}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
    }
    const matchDmy = clean.match(/^(\d{1,2})-(\d{1,2})-(\d{4})/);
    if (matchDmy) {
      const [, d, m, y] = matchDmy;
      return `${y.padStart(4, '0')}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
    }
    const parsed = new Date(clean);
    if (!isNaN(parsed.getTime())) {
      return parsed.toISOString().slice(0, 10);
    }
    return clean.slice(0, 10);
  };

  const handleUseInStrategy = (dataset: DataSource) => {
    const sDate = normalizeDate(dataset.startDate || dataset.start_date);
    const eDate = normalizeDate(dataset.endDate || dataset.end_date);
    const sourceVal = dataset.source === 'dukascopy' ? 'dukascopy' : dataset.source === 'yfinance' ? 'yfinance' : 'csv';
    updateDataSource({
      symbol: dataset.symbol,
      timeframe: dataset.timeframe,
      startDate: sDate || '2023-01-01',
      endDate: eDate || '2024-01-01',
      source: sourceVal
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
          <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
            <div className="flex items-center gap-2">
              <Database size={20} className="text-cyan" />
              <h3 className={styles.cardTitle} style={{ margin: 0 }}>Fetch Live / Institutional Data</h3>
            </div>
            {/* Provider Switcher */}
            <div className="flex gap-1 bg-surface-dark p-1 rounded border border-border">
              <button
                type="button"
                className={`text-xs px-3 py-1 rounded transition font-medium ${provider === 'dukascopy' ? 'bg-cyan text-black font-bold' : 'text-secondary hover:text-primary'}`}
                onClick={() => {
                  setProvider('dukascopy');
                  setSymbol('XAUUSD');
                  setTimeframe('1h');
                }}
              >
                🏛️ Dukascopy (Tick-Quality)
              </button>
              <button
                type="button"
                className={`text-xs px-3 py-1 rounded transition font-medium ${provider === 'yfinance' ? 'bg-cyan text-black font-bold' : 'text-secondary hover:text-primary'}`}
                onClick={() => {
                  setProvider('yfinance');
                  setSymbol('BTC-USD');
                  setTimeframe('1d');
                }}
              >
                🌐 Yahoo Finance
              </button>
            </div>
          </div>

          <div className={styles.formGrid}>
            <div ref={dropdownRef} style={{ position: 'relative' }}>
              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.35rem' }}>
                Asset / Symbol ({provider === 'dukascopy' ? 'Dukascopy' : 'Yahoo Finance'}) *
              </label>
              <div 
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'var(--color-bg-tertiary)',
                  border: isDropdownOpen ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  borderRadius: '6px',
                  padding: '0.45rem 0.75rem',
                  cursor: 'pointer',
                  transition: 'border-color 0.15s ease'
                }}
                onClick={() => setIsDropdownOpen(prev => !prev)}
              >
                <Search size={15} className="text-secondary" style={{ marginRight: '0.5rem', flexShrink: 0 }} />
                <input 
                  type="text"
                  value={isDropdownOpen ? searchQuery : symbol}
                  placeholder={isDropdownOpen ? 'Buscar por símbolo o nombre (ej. Gold, Nasdaq, EURUSD)...' : 'Selecciona o escribe un símbolo...'}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    if (!isDropdownOpen) setIsDropdownOpen(true);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchQuery.trim()) {
                      handleSelectSymbol(searchQuery.trim());
                    }
                  }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--color-text-primary)',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    width: '100%'
                  }}
                />
                <ChevronDown size={16} className="text-secondary" style={{ marginLeft: '0.5rem', flexShrink: 0 }} />
              </div>

              {/* Custom Dropdown Menu with Categories */}
              {isDropdownOpen && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  marginTop: '4px',
                  maxHeight: '300px',
                  overflowY: 'auto',
                  background: 'var(--color-bg-secondary)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                  zIndex: 100,
                  padding: '0.5rem'
                }}>
                  {searchQuery.trim() && (
                    <div 
                      style={{
                        padding: '0.5rem 0.75rem',
                        background: 'rgba(0, 212, 255, 0.08)',
                        borderRadius: '6px',
                        marginBottom: '0.5rem',
                        cursor: 'pointer',
                        fontSize: '0.8125rem',
                        color: 'var(--color-accent-cyan)',
                        fontWeight: 600
                      }}
                      onClick={() => handleSelectSymbol(searchQuery.trim())}
                    >
                      Usar ticker personalizado: "{searchQuery.toUpperCase()}"
                    </div>
                  )}

                  {Object.keys(groupedSymbols).length === 0 ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '0.8125rem' }}>
                      No se encontraron activos predefinidos. Presiona Enter para usar "{searchQuery.toUpperCase()}".
                    </div>
                  ) : (
                    Object.entries(groupedSymbols).map(([category, syms]) => (
                      <div key={category} style={{ marginBottom: '0.5rem' }}>
                        <div style={{
                          fontSize: '0.6875rem',
                          textTransform: 'uppercase',
                          fontWeight: 700,
                          letterSpacing: '0.05em',
                          color: 'var(--color-text-tertiary)',
                          padding: '0.25rem 0.5rem'
                        }}>
                          {category}
                        </div>
                        {syms.map(s => {
                          const isSelected = symbol.toUpperCase() === s.symbol.toUpperCase();
                          return (
                            <div
                              key={s.symbol}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '0.4rem 0.6rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                background: isSelected ? 'rgba(0, 212, 255, 0.12)' : 'transparent',
                                color: isSelected ? 'var(--color-accent-cyan)' : 'var(--color-text-primary)',
                                fontSize: '0.8125rem',
                                transition: 'background 0.1s ease'
                              }}
                              onMouseEnter={(e) => {
                                if (!isSelected) e.currentTarget.style.background = 'var(--color-bg-tertiary)';
                              }}
                              onMouseLeave={(e) => {
                                if (!isSelected) e.currentTarget.style.background = 'transparent';
                              }}
                              onClick={() => handleSelectSymbol(s.symbol)}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <strong style={{ fontFamily: 'monospace', color: isSelected ? 'var(--color-accent-cyan)' : 'var(--color-text-primary)' }}>
                                  {s.symbol}
                                </strong>
                                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                                  {s.name}
                                </span>
                              </div>
                              <span style={{
                                fontSize: '0.6875rem',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                background: 'var(--color-bg-primary)',
                                border: '1px solid var(--color-border)',
                                color: 'var(--color-text-tertiary)'
                              }}>
                                {s.type.toUpperCase()}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    ))
                  )}
                </div>
              )}

              {providerSymbols.length > 0 && (
                <div className={styles.chipList} style={{ marginTop: '0.5rem' }}>
                  {providerSymbols.slice(0, 6).map(s => (
                    <button
                      key={s.symbol}
                      type="button"
                      className={`${styles.symbolChip} ${symbol.toUpperCase() === s.symbol.toUpperCase() ? styles.symbolChipActive : ''}`}
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
              options={
                provider === 'dukascopy'
                  ? [
                      { label: '1 Minute (1m) — M1 Institucional', value: '1m' },
                      { label: '5 Minutes (5m)', value: '5m' },
                      { label: '15 Minutes (15m)', value: '15m' },
                      { label: '30 Minutes (30m)', value: '30m' },
                      { label: '1 Hour (1h)', value: '1h' },
                      { label: '4 Hours (4h)', value: '4h' },
                      { label: '1 Day (1d)', value: '1d' }
                    ]
                  : [
                      { label: '1 Minute (1m) [Máx 7 días]', value: '1m' },
                      { label: '5 Minutes (5m) [Máx 60 días]', value: '5m' },
                      { label: '15 Minutes (15m) [Máx 60 días]', value: '15m' },
                      { label: '30 Minutes (30m) [Máx 60 días]', value: '30m' },
                      { label: '1 Hour (1h) [Máx 730 días]', value: '1h' },
                      { label: '1 Day (1d) [Historial Completo]', value: '1d' },
                      { label: '1 Week (1w) [Historial Completo]', value: '1w' }
                    ]
              }
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
