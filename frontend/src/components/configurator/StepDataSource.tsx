import React, { useEffect, useState, useMemo } from 'react';
import { Globe, FileSpreadsheet, Calendar, Sparkles, CheckCircle2 } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import Select from '../common/Select';
import { getDatasets, getSymbols } from '../../services/api';
import type { DataSource } from '../../types/data';
import styles from '../../styles/pages.module.css';

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

        // If in CSV mode and datasets exist, ensure valid date range is populated
        if (ds.source === 'csv' && dsets.length > 0) {
          const match = dsets.find(
            d => d.symbol.toUpperCase() === ds.symbol.toUpperCase() && d.timeframe === ds.timeframe
          ) || dsets[0];
          
          const sDate = normalizeDate(match.startDate || match.start_date);
          const eDate = normalizeDate(match.endDate || match.end_date);
          if (sDate && eDate && (!ds.startDate || !ds.endDate || ds.startDate === '2023-01-01')) {
            updateDataSource({
              symbol: match.symbol,
              timeframe: match.timeframe,
              startDate: sDate,
              endDate: eDate
            });
          }
        }
      } catch (err) {
        console.error('Failed to load datasets', err);
      }
    };
    loadData();
  }, []);

  // Find currently active dataset for CSV mode
  const activeDataset = useMemo(() => {
    if (datasets.length === 0) return undefined;
    return datasets.find(
      d => d.symbol.toUpperCase() === ds.symbol.toUpperCase() && d.timeframe === ds.timeframe
    ) || datasets.find(
      d => d.symbol.toUpperCase() === ds.symbol.toUpperCase()
    ) || datasets[0];
  }, [datasets, ds.symbol, ds.timeframe]);

  const activeStart = activeDataset ? normalizeDate(activeDataset.startDate || activeDataset.start_date) : '';
  const activeEnd = activeDataset ? normalizeDate(activeDataset.endDate || activeDataset.end_date) : '';
  const activeBars = activeDataset ? (activeDataset.rowCount || activeDataset.row_count || 0) : 0;

  const handleSwitchSource = (newSource: 'yfinance' | 'csv') => {
    if (newSource === 'csv') {
      if (datasets.length > 0) {
        const target = activeDataset || datasets[0];
        const sDate = normalizeDate(target.startDate || target.start_date);
        const eDate = normalizeDate(target.endDate || target.end_date);
        updateDataSource({
          source: 'csv',
          symbol: target.symbol,
          timeframe: target.timeframe,
          startDate: sDate || '2021-01-01',
          endDate: eDate || '2026-01-01'
        });
      } else {
        updateDataSource({ source: 'csv' });
      }
    } else {
      const today = new Date().toISOString().slice(0, 10);
      const oneYearAgo = new Date(Date.now() - 365 * 86400 * 1000).toISOString().slice(0, 10);
      updateDataSource({
        source: 'yfinance',
        symbol: ds.symbol === 'CUSTOM' ? 'BTC-USD' : ds.symbol,
        startDate: ds.startDate || oneYearAgo,
        endDate: ds.endDate || today
      });
    }
  };

  const handleSelectDataset = (id: string) => {
    const selected = datasets.find(d => d.id === id);
    if (selected) {
      const sDate = normalizeDate(selected.startDate || selected.start_date);
      const eDate = normalizeDate(selected.endDate || selected.end_date);
      updateDataSource({
        symbol: selected.symbol,
        timeframe: selected.timeframe,
        startDate: sDate || ds.startDate,
        endDate: eDate || ds.endDate,
        source: 'csv'
      });
    }
  };

  // Quick Preset Handlers
  const applyPreset = (preset: 'full' | '1y' | '2y' | '6m' | '2025_present') => {
    if (ds.source === 'csv' && activeDataset) {
      const sDate = normalizeDate(activeDataset.startDate || activeDataset.start_date);
      const eDate = normalizeDate(activeDataset.endDate || activeDataset.end_date);
      if (!eDate) return;

      const endDateObj = new Date(eDate);

      if (preset === 'full') {
        updateDataSource({ startDate: sDate, endDate: eDate });
      } else if (preset === '1y') {
        const s1y = new Date(endDateObj.getTime() - 365 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s1y < sDate ? sDate : s1y, endDate: eDate });
      } else if (preset === '2y') {
        const s2y = new Date(endDateObj.getTime() - 730 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s2y < sDate ? sDate : s2y, endDate: eDate });
      } else if (preset === '6m') {
        const s6m = new Date(endDateObj.getTime() - 180 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s6m < sDate ? sDate : s6m, endDate: eDate });
      } else if (preset === '2025_present') {
        const s2025 = '2025-01-01';
        updateDataSource({ startDate: s2025 < sDate ? sDate : s2025, endDate: eDate });
      }
    } else {
      const today = new Date().toISOString().slice(0, 10);
      const now = Date.now();
      if (preset === 'full' || preset === '2y') {
        const s2y = new Date(now - 730 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s2y, endDate: today });
      } else if (preset === '1y') {
        const s1y = new Date(now - 365 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s1y, endDate: today });
      } else if (preset === '6m') {
        const s6m = new Date(now - 180 * 86400 * 1000).toISOString().slice(0, 10);
        updateDataSource({ startDate: s6m, endDate: today });
      } else if (preset === '2025_present') {
        updateDataSource({ startDate: '2025-01-01', endDate: today });
      }
    }
  };

  const csvOptions = datasets.map(d => {
    const sDate = normalizeDate(d.startDate || d.start_date);
    const eDate = normalizeDate(d.endDate || d.end_date);
    const dateRangeStr = sDate && eDate ? ` [${sDate} → ${eDate}]` : '';
    return {
      label: `${d.symbol} (${d.timeframe}) - ${d.rowCount || d.row_count || 0} bars${dateRangeStr}`,
      value: d.id
    };
  });

  const isInvalidDates = Boolean(ds.startDate && ds.endDate && new Date(ds.startDate) >= new Date(ds.endDate));

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Data Source & Historical Range</h2>
      <p className={styles.stepSubtitle}>
        Select market provider, symbol, bar timeframe, and historical date boundaries for strategy discovery.
      </p>

      <div className={styles.tabsContainer}>
        <div 
          className={`${styles.tab} ${ds.source === 'yfinance' ? styles.tabActive : ''} flex items-center justify-center gap-2`}
          onClick={() => handleSwitchSource('yfinance')}
        >
          <Globe size={16} />
          <span>Yahoo Finance (Live Provider)</span>
        </div>
        <div 
          className={`${styles.tab} ${ds.source === 'csv' ? styles.tabActive : ''} flex items-center justify-center gap-2`}
          onClick={() => handleSwitchSource('csv')}
        >
          <FileSpreadsheet size={16} />
          <span>Custom Data / MT5 CSV ({datasets.length})</span>
        </div>
      </div>

      <div className={styles.formGrid}>
        {ds.source === 'yfinance' ? (
          <div>
            <Input 
              label="Symbol *" 
              value={ds.symbol}
              onChange={(e) => updateDataSource({ symbol: e.target.value.toUpperCase() })}
              placeholder="e.g. BTC-USD, AAPL, EURUSD=X, ^NDX"
              required
              error={!ds.symbol ? 'Symbol is required' : undefined}
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
              label="Select Uploaded Dataset (MT5 / CSV) *"
              options={
                csvOptions.length > 0
                  ? [{ label: '-- Choose a dataset --', value: '' }, ...csvOptions]
                  : [{ label: 'No datasets uploaded yet. Upload in Data Manager.', value: '' }]
              }
              value={datasets.find(d => d.symbol === ds.symbol && d.timeframe === ds.timeframe)?.id || activeDataset?.id || ''}
              onChange={(e) => handleSelectDataset(e.target.value)}
              tooltipTitle="Uploaded MT5 Dataset"
              tooltip="Selecciona uno de los archivos CSV históricos importados desde MetaTrader 5."
            />
            {csvOptions.length === 0 && (
              <p className="text-xs text-amber mt-1">
                Tip: Go to <strong>Data Manager</strong> to upload your MT5 historical CSVs.
              </p>
            )}
          </div>
        )}

        <Select 
          label="Timeframe *"
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

        <div>
          <Input 
            type="date"
            label="Start Date * (Obligatorio)"
            value={ds.startDate}
            min={ds.source === 'csv' && activeStart ? activeStart : undefined}
            max={ds.source === 'csv' && activeEnd ? activeEnd : undefined}
            onChange={(e) => updateDataSource({ startDate: e.target.value })}
            required
            error={!ds.startDate ? 'Start Date is mandatory' : undefined}
            tooltipTitle="Backtest Start Date"
            tooltip="Fecha inicial obligatoria del período de entrenamiento y backtest."
          />
        </div>

        <div>
          <Input 
            type="date"
            label="End Date * (Obligatorio)"
            value={ds.endDate}
            min={ds.source === 'csv' && activeStart ? activeStart : undefined}
            max={ds.source === 'csv' && activeEnd ? activeEnd : undefined}
            onChange={(e) => updateDataSource({ endDate: e.target.value })}
            required
            error={
              !ds.endDate 
                ? 'End Date is mandatory' 
                : isInvalidDates 
                ? 'End Date must be after Start Date' 
                : undefined
            }
            tooltipTitle="Backtest End Date"
            tooltip="Fecha final obligatoria del período histórico."
          />
        </div>
      </div>

      {/* Dataset Range Banner & Quick Presets */}
      {ds.source === 'csv' && activeDataset && (
        <div style={{
          marginTop: '1rem',
          padding: '0.85rem 1rem',
          borderRadius: '8px',
          background: 'rgba(0, 212, 255, 0.05)',
          border: '1px solid rgba(0, 212, 255, 0.25)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.6rem'
        }}>
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-sm text-primary">
              <Calendar size={16} className="text-cyan" />
              <span>
                Rango disponible en CSV: <strong className="text-cyan">{activeStart || 'N/A'}</strong> al <strong className="text-cyan">{activeEnd || 'N/A'}</strong> ({activeBars.toLocaleString()} velas).
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald">
              <CheckCircle2 size={14} />
              <span>Fechas sincronizadas con el dataset</span>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap pt-1 border-t border-border-light">
            <span className="text-xs text-secondary flex items-center gap-1">
              <Sparkles size={13} className="text-cyan" />
              Presets de Rango:
            </span>
            <button
              type="button"
              className="text-xs px-2.5 py-1 bg-cyan/15 hover:bg-cyan hover:text-black text-cyan border border-cyan/30 rounded transition font-medium"
              onClick={() => applyPreset('full')}
            >
              Rango Completo ({activeStart} → {activeEnd})
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-surface-lighter text-primary border border-border rounded transition"
              onClick={() => applyPreset('1y')}
            >
              Último 1 Año
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-surface-lighter text-primary border border-border rounded transition"
              onClick={() => applyPreset('2y')}
            >
              Últimos 2 Años
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-surface-lighter text-primary border border-border rounded transition"
              onClick={() => applyPreset('6m')}
            >
              Últimos 6 Meses
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-surface-lighter text-primary border border-border rounded transition"
              onClick={() => applyPreset('2025_present')}
            >
              Desde 2025
            </button>
          </div>
        </div>
      )}

      {/* Yahoo Finance Quick Presets */}
      {ds.source === 'yfinance' && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}>
          <span className="text-xs text-secondary flex items-center gap-1">
            <Sparkles size={13} className="text-cyan" />
            Presets de Período (Yahoo Finance):
          </span>
          <div className="flex items-center gap-1.5 flex-wrap">
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black text-primary rounded transition"
              onClick={() => applyPreset('1y')}
            >
              1 Año
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black text-primary rounded transition"
              onClick={() => applyPreset('2y')}
            >
              2 Años
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black text-primary rounded transition"
              onClick={() => applyPreset('6m')}
            >
              6 Meses
            </button>
            <button
              type="button"
              className="text-xs px-2 py-1 bg-surface-light hover:bg-cyan hover:text-black text-primary rounded transition"
              onClick={() => applyPreset('2025_present')}
            >
              Desde 2025
            </button>
          </div>
        </div>
      )}

      {isInvalidDates && (
        <div style={{ marginTop: '1rem', padding: '0.75rem', borderRadius: '6px', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', color: 'var(--color-accent-rose)', fontSize: '0.8125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Calendar size={16} />
          <span>Error de validación: La fecha final (End Date) debe ser posterior a la fecha inicial (Start Date).</span>
        </div>
      )}
    </div>
  );
};

export default StepDataSource;
