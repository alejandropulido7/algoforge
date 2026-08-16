import React, { useEffect, useState } from 'react';
import { Globe, FileSpreadsheet } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import Select from '../common/Select';
import { getDatasets, getSymbols } from '../../services/api';
import type { DataSource } from '../../types/data';
import styles from '../../styles/pages.module.css';

const StepDataSource: React.FC = () => {
  const { config, updateDataSource } = useJobStore();
  const ds = config.dataSource;

  const [datasets, setDatasets] = useState<DataSource[]>([]);
  const [popularSymbols, setPopularSymbols] = useState<Array<{ symbol: string; name: string }>>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [dsets, syms] = await Promise.all([getDatasets(), getSymbols()]);
        setDatasets(dsets);
        setPopularSymbols(syms);
      } catch (err) {
        console.error('Failed to load datasets', err);
      }
    };
    loadData();
  }, []);

  const handleSelectDataset = (id: string) => {
    const selected = datasets.find(d => d.id === id);
    if (selected) {
      updateDataSource({
        symbol: selected.symbol,
        timeframe: selected.timeframe,
        startDate: selected.startDate || selected.start_date || ds.startDate,
        endDate: selected.endDate || selected.end_date || ds.endDate,
        source: 'csv'
      });
    }
  };

  const csvOptions = datasets.map(d => ({
    label: `${d.symbol} (${d.timeframe}) - ${d.rowCount || d.row_count || 0} bars [${d.source}]`,
    value: d.id
  }));

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Data Source</h2>
      <p className={styles.stepSubtitle}>Select where to get your historical market data for strategy discovery.</p>

      <div className={styles.tabsContainer}>
        <div 
          className={`${styles.tab} ${ds.source === 'yfinance' ? styles.tabActive : ''} flex items-center justify-center gap-2`}
          onClick={() => updateDataSource({ source: 'yfinance' })}
        >
          <Globe size={16} />
          <span>Yahoo Finance (Live Provider)</span>
        </div>
        <div 
          className={`${styles.tab} ${ds.source === 'csv' ? styles.tabActive : ''} flex items-center justify-center gap-2`}
          onClick={() => updateDataSource({ source: 'csv' })}
        >
          <FileSpreadsheet size={16} />
          <span>Custom Data / MT5 CSV ({datasets.length})</span>
        </div>
      </div>

      <div className={styles.formGrid}>
        {ds.source === 'yfinance' ? (
          <div>
            <Input 
              label="Symbol" 
              value={ds.symbol}
              onChange={(e) => updateDataSource({ symbol: e.target.value.toUpperCase() })}
              placeholder="e.g. BTC-USD, AAPL, EURUSD=X, ^NDX"
              tooltipTitle="Trading Asset / Symbol"
              tooltip="Ticker del activo financiero a descargar desde Yahoo Finance (ej. BTC-USD para cripto, EURUSD=X para forex, AAPL para acciones, ^NDX para NASDAQ)."
            />
            {popularSymbols.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {popularSymbols.slice(0, 5).map(s => (
                  <button
                    key={s.symbol}
                    type="button"
                    className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black rounded transition"
                    onClick={() => updateDataSource({ symbol: s.symbol })}
                  >
                    {s.symbol}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            <Select 
              label="Select Uploaded Dataset (MT5 / CSV)"
              options={
                csvOptions.length > 0
                  ? [{ label: '-- Choose a dataset --', value: '' }, ...csvOptions]
                  : [{ label: 'No datasets uploaded yet. Upload in Data Manager.', value: '' }]
              }
              value={datasets.find(d => d.symbol === ds.symbol && d.timeframe === ds.timeframe)?.id || ''}
              onChange={(e) => handleSelectDataset(e.target.value)}
              tooltipTitle="Uploaded MT5 Dataset"
              tooltip="Selecciona uno de los archivos CSV históricos previamente importados desde MetaTrader 5."
            />
            {csvOptions.length === 0 && (
              <p className="text-xs text-amber mt-1">
                Tip: Go to <strong>Data Manager</strong> to upload your MT5 historical CSVs.
              </p>
            )}
          </div>
        )}

        <Select 
          label="Timeframe"
          value={ds.timeframe}
          onChange={(e) => updateDataSource({ timeframe: e.target.value })}
          options={[
            {label: '1 Minute (M1)', value: '1m'},
            {label: '5 Minutes (M5)', value: '5m'},
            {label: '15 Minutes (M15)', value: '15m'},
            {label: '30 Minutes (M30)', value: '30m'},
            {label: '1 Hour (H1)', value: '1h'},
            {label: '4 Hours (H4)', value: '4h'},
            {label: '1 Day (D1)', value: '1d'},
            {label: '1 Week (W1)', value: '1w'}
          ]}
          tooltipTitle="Bar Timeframe (Temporalidad)"
          tooltip="Duración de cada vela japonesa para el cálculo de indicadores y ejecución de señales."
        />

        <Input 
          type="date"
          label="Start Date"
          value={ds.startDate}
          onChange={(e) => updateDataSource({ startDate: e.target.value })}
          tooltipTitle="Backtest Start Date"
          tooltip="Fecha inicial del período de entrenamiento y backtest."
        />

        <Input 
          type="date"
          label="End Date"
          value={ds.endDate}
          onChange={(e) => updateDataSource({ endDate: e.target.value })}
          tooltipTitle="Backtest End Date"
          tooltip="Fecha final del período histórico."
        />
      </div>
    </div>
  );
};

export default StepDataSource;
