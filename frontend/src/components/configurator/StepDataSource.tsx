import React, { useEffect, useState, useMemo } from 'react';
import { FileSpreadsheet, Calendar, Sparkles, CheckCircle2 } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import Select from '../common/Select';
import { getDatasets } from '../../services/api';
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

  useEffect(() => {
    // Force CSV source
    updateDataSource({ source: 'csv' });
    
    const loadData = async () => {
      try {
        const dsets = await getDatasets();
        setDatasets(dsets);

        if (dsets.length > 0) {
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

  const [selectedSource, setSelectedSource] = useState<string>('all');

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

  const handleSelectDataset = (id: string) => {
    const selected = datasets.find(d => d.id === id);
    if (selected) {
      const sDate = normalizeDate(selected.startDate || selected.start_date);
      const eDate = normalizeDate(selected.endDate || selected.end_date);
      const sourceVal = selected.source === 'dukascopy' ? 'dukascopy' : selected.source === 'yfinance' ? 'yfinance' : 'csv';
      updateDataSource({
        symbol: selected.symbol,
        timeframe: selected.timeframe,
        startDate: sDate || ds.startDate,
        endDate: eDate || ds.endDate,
        source: sourceVal
      });
    }
  };

  const applyPreset = (preset: 'full' | '1y' | '2y' | '6m' | '2025_present') => {
    if (activeDataset) {
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
    }
  };

  const filteredDatasets = useMemo(() => {
    if (selectedSource === 'all') return datasets;
    if (selectedSource === 'csv') return datasets.filter(d => d.source !== 'dukascopy' && d.source !== 'yfinance');
    return datasets.filter(d => d.source === selectedSource);
  }, [datasets, selectedSource]);

  const csvOptions = filteredDatasets.map(d => {
    const sDate = normalizeDate(d.startDate || d.start_date);
    const eDate = normalizeDate(d.endDate || d.end_date);
    const dateRangeStr = sDate && eDate ? ` [${sDate} → ${eDate}]` : '';
    const srcLabel = d.source === 'dukascopy' ? 'Dukascopy' : d.source === 'yfinance' ? 'Yahoo' : 'MT5/CSV';
    return {
      label: `[${srcLabel}] ${d.symbol} (${d.timeframe}) - ${d.rowCount || d.row_count || 0} bars${dateRangeStr}`,
      value: d.id
    };
  });

  const isInvalidDates = Boolean(ds.startDate && ds.endDate && new Date(ds.startDate) >= new Date(ds.endDate));

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Data Source & Historical Range</h2>
      <p className={styles.stepSubtitle}>
        Selecciona la fuente de datos y luego el dataset descargado en Data Manager que deseas usar para el descubrimiento de estrategias.
      </p>

      <div className={styles.tabsContainer}>
        <div className={`${styles.tab} ${styles.tabActive} flex items-center justify-center gap-2`}>
          <FileSpreadsheet size={16} />
          <span>📁 Datasets Caché ({datasets.length})</span>
        </div>
      </div>

      <div className={styles.formGrid}>
        <div>
          <Select
            label="Data Source Provider"
            options={[
              { label: 'All Sources', value: 'all' },
              { label: '🏛️ Dukascopy (Institutional)', value: 'dukascopy' },
              { label: '🌐 Yahoo Finance', value: 'yfinance' },
              { label: '📁 Custom Data / MT5 CSV', value: 'csv' }
            ]}
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            tooltipTitle="Filtro de Fuente"
            tooltip="Filtra los datasets descargados por su proveedor de origen."
          />
        </div>

        <div>
          <Select 
            label="Select Downloaded Dataset *"
            options={
              csvOptions.length > 0
                ? [{ label: '-- Choose a dataset --', value: '' }, ...csvOptions]
                : [{ label: `No datasets for this source. Download in Data Manager.`, value: '' }]
            }
            value={datasets.find(d => d.symbol === ds.symbol && d.timeframe === ds.timeframe)?.id || activeDataset?.id || ''}
            onChange={(e) => handleSelectDataset(e.target.value)}
            tooltipTitle="Dataset Caché"
            tooltip="Selecciona uno de los activos históricos que ya descargaste en el Data Manager."
          />
          {csvOptions.length === 0 && (
            <p className="text-xs text-amber mt-1">
              Tip: Ve a <strong>Data Manager</strong> para descargar activos o subir CSVs.
            </p>
          )}
        </div>

        <div>
          <Input 
            type="date"
            label="Start Date * (Obligatorio)"
            value={ds.startDate}
            min={activeStart || undefined}
            max={activeEnd || undefined}
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
            min={activeStart || undefined}
            max={activeEnd || undefined}
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

      {activeDataset && (
        <div className={styles.rangeBanner}>
          <div className={styles.rangeBannerHeader}>
            <div className={styles.rangeBannerText}>
              <Calendar size={16} className="text-cyan" />
              <span>
                Rango disponible en dataset: <strong className="text-cyan">{activeStart || 'N/A'}</strong> al <strong className="text-cyan">{activeEnd || 'N/A'}</strong> ({activeBars.toLocaleString()} velas).
              </span>
            </div>
            <div className={styles.rangeBannerBadge}>
              <CheckCircle2 size={14} />
              <span>Sincronizado</span>
            </div>
          </div>

          <div className={styles.presetBar}>
            <span className={styles.presetBarTitle}>
              <Sparkles size={13} className="text-cyan" />
              Presets de Rango:
            </span>
            <button
              type="button"
              className={styles.presetBtnPrimary}
              onClick={() => applyPreset('full')}
            >
              Rango Completo
            </button>
            <button
              type="button"
              className={styles.presetBtn}
              onClick={() => applyPreset('1y')}
            >
              Último 1 Año
            </button>
            <button
              type="button"
              className={styles.presetBtn}
              onClick={() => applyPreset('2y')}
            >
              Últimos 2 Años
            </button>
            <button
              type="button"
              className={styles.presetBtn}
              onClick={() => applyPreset('6m')}
            >
              Últimos 6 Meses
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

