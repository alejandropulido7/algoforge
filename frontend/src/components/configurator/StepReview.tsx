import React, { useMemo } from 'react';
import { Database, Sliders, Dna, ShieldCheck, Scale, Cpu, Clock, AlertCircle } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import { INDICATORS_CATALOG } from '../../data/indicatorsCatalog';
import styles from '../../styles/pages.module.css';

function calculateParamSteps(min: number, step: number, max: number): number {
  if (!step || step <= 0 || max < min) return 1;
  return Math.floor((max - min) / step + 1e-9) + 1;
}

const StepReview: React.FC = () => {
  const { config } = useJobStore();
  const risk = config.risk || {
    initialDeposit: 10000,
    sizingMode: 'lots',
    lotSize: 0.1,
    riskPct: 1.0,
    slType: 'pips',
    slPips: 50.0,
    slAtrMult: 1.5,
    tpType: 'pips',
    tpPips: 100.0,
    tpAtrMult: 3.0,
    contractSize: 100000,
    pointSize: 0.0001,
  };

  // Calculate combinations math
  const { totalIndicatorCombos, totalTpslCombos, totalCombos, estimatedTime } = useMemo(() => {
    // 1. Indicators
    const indList = config.indicators || [];
    let indCombos = 1;
    if (indList.length > 0) {
      for (const indId of indList) {
        const catItem = INDICATORS_CATALOG.find(c => c.id === indId || c.name.toLowerCase() === indId.toLowerCase());
        const userRanges = config.indicatorRanges?.[indId] || {};
        let variantsForInd = 1;

        if (catItem && catItem.params.length > 0) {
          for (const p of catItem.params) {
            const r = userRanges[p.key] || {};
            const pMin = r.min !== undefined ? r.min : p.defaultMin;
            const pStep = r.step !== undefined ? r.step : p.defaultStep;
            const pMax = r.max !== undefined ? r.max : p.defaultMax;
            const steps = calculateParamSteps(pMin, pStep, pMax);
            variantsForInd *= Math.max(1, steps);
          }
        }
        indCombos *= variantsForInd;
      }
    }

    // 2. TP/SL Management
    const tpslModes = config.tpslModes || ['atr_classic'];
    let tpslCombos = 1;
    if (tpslModes.length > 0) {
      for (const modeId of tpslModes) {
        const userRanges = config.tpslRanges?.[modeId];
        let modeVariants = 1;
        if (userRanges && Object.keys(userRanges).length > 0) {
          for (const pk of Object.keys(userRanges)) {
            const r = userRanges[pk];
            const steps = calculateParamSteps(r.min, r.step, r.max);
            modeVariants *= Math.max(1, steps);
          }
        } else {
          // Canonical default 1 value
          modeVariants = 1;
        }
        tpslCombos *= modeVariants;
      }
    }

    const total = indCombos * tpslCombos;

    let timeStr = '~10 - 20 segundos';
    if (total < 100) {
      timeStr = '~5 - 15 segundos';
    } else if (total < 500) {
      timeStr = '~15 - 30 segundos';
    } else if (total < 2000) {
      timeStr = '~30s - 1.5 minutos';
    } else if (total < 10000) {
      timeStr = '~1.5 - 3.5 minutos';
    } else if (total < 50000) {
      timeStr = '~3.5 - 8 minutos';
    } else {
      timeStr = '~8 - 20 minutos';
    }

    return {
      totalIndicatorCombos: indCombos,
      totalTpslCombos: tpslCombos,
      totalCombos: total,
      estimatedTime: timeStr
    };
  }, [config.indicators, config.indicatorRanges, config.tpslModes, config.tpslRanges]);

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Revisión del Análisis</h2>
      <p className={styles.stepSubtitle}>Verifica la configuración del pipeline antes de iniciar la búsqueda de estrategias.</p>

      {/* Prominent Combinations Metric Card */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(19, 24, 41, 0.95) 100%)',
        border: '1px solid rgba(0, 212, 255, 0.25)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.75rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.25)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              background: 'rgba(0, 212, 255, 0.15)',
              padding: '0.625rem',
              borderRadius: '8px',
              color: 'var(--color-accent-cyan)'
            }}>
              <Cpu size={24} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                Espacio Total de Combinaciones a Evaluar
              </h3>
              <p style={{ margin: '0.25rem 0 0', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                Se ejecutará un ciclo determinista exhaustivo sobre todo el dataset
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem 0.875rem', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
            <Clock size={16} className="text-amber" />
            <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>Tiempo Estimado:</span>
            <strong style={{ fontSize: '0.875rem', color: 'var(--color-accent-amber)' }}>{estimatedTime}</strong>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          padding: '1rem',
          background: 'rgba(0,0,0,0.25)',
          borderRadius: '8px',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Combinaciones de Indicadores
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-accent-cyan)', marginTop: '0.25rem' }}>
              {totalIndicatorCombos.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.125rem' }}>
              {config.indicators.length} indicadores seleccionados
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Variantes TP/SL Management
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-accent-emerald)', marginTop: '0.25rem' }}>
              {totalTpslCombos.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.125rem' }}>
              {(config.tpslModes || []).length} modos de salida activos
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Total Combinaciones a Evaluar
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-accent-cyan)', marginTop: '0.125rem' }}>
              {totalCombos.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.125rem' }}>
              Lotes de 15 con persistencia Redis
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.875rem', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
          <AlertCircle size={15} style={{ color: 'var(--color-accent-amber)', flexShrink: 0 }} />
          <span>
            <strong>Nota informativa:</strong> A mayor cantidad de combinaciones (rangos amplios y pasos pequeños), mayor será la precisión y exploración del mercado, pero requerirá mayor tiempo de procesamiento.
          </span>
        </div>
      </div>

      <div className={styles.reviewGrid}>
        <div className={styles.reviewCard}>
          <div className="flex items-center gap-2 mb-3 text-cyan">
            <Database size={18} />
            <h4 style={{ margin: 0 }}>Data Source</h4>
          </div>
          <ul>
            <li><span>Source:</span> <strong>{config.dataSource.source}</strong></li>
            <li><span>Symbol:</span> <strong>{config.dataSource.symbol}</strong></li>
            <li><span>Timeframe:</span> <strong>{config.dataSource.timeframe}</strong></li>
            <li><span>Period:</span> <strong>{config.dataSource.startDate} to {config.dataSource.endDate}</strong></li>
          </ul>
        </div>

        <div className={styles.reviewCard}>
          <div className="flex items-center gap-2 mb-3 text-cyan">
            <Sliders size={18} />
            <h4 style={{ margin: 0 }}>Indicators</h4>
          </div>
          <ul>
            <li><span>Selected:</span> <strong>{config.indicators.length} indicators</strong></li>
          </ul>
          <div className={styles.tagList}>
            {config.indicators.map(ind => (
              <span key={ind} className={styles.tag}>{ind}</span>
            ))}
          </div>
        </div>

        <div className={styles.reviewCard}>
          <div className="flex items-center gap-2 mb-3 text-cyan">
            <Scale size={18} />
            <h4 style={{ margin: 0 }}>Strategy Config & Ejecución</h4>
          </div>
          <ul>
            <li><span>Depósito Inicial:</span> <strong style={{ color: 'var(--color-accent-cyan)' }}>${(risk.initialDeposit ?? 10000).toLocaleString()} USD</strong></li>
            <li><span>Dimensionamiento:</span> <strong>{
              (risk.sizingMode || 'lots') === 'lots' 
                ? `Lote Fijo (${risk.lotSize ?? 0.1} lots)` 
                : `${risk.riskPct ?? 1.0}% Riesgo (${(risk.riskBase || 'initial_deposit') === 'initial_deposit' ? 'Depósito Inicial Fijo' : 'Balance Compuesto'})`
            }</strong></li>
            <li><span>Dirección:</span> <strong>{risk.direction === 'long' ? 'Long Only' : (risk.direction === 'short' ? 'Short Only' : 'Long & Short')}</strong></li>
            <li><span>Tipo de Orden:</span> <strong>{risk.orderType === 'stop' ? 'Buy/Sell Stop' : (risk.orderType === 'limit' ? 'Buy/Sell Limit' : 'A Mercado')}</strong></li>
            <li><span>Operaciones Simultáneas:</span> <strong>{risk.maxSimultaneousTrades || 1} Max</strong></li>
            <li><span>Racha Pérdidas:</span> <strong>{
              risk.consecutiveLossAction === 'reduce_risk' ? `Reducir ${risk.consecutiveLossReductionPct || 50}% tras ${risk.consecutiveLossThreshold || 3} pérdidas` :
              risk.consecutiveLossAction === 'stop_bot' ? `Pausar tras ${risk.consecutiveLossThreshold || 3} pérdidas` : 'Normal (Sin pausa)'
            }</strong></li>
            {risk.consecutiveLossAction === 'stop_bot' && (
              <li><span>Reactivación:</span> <strong style={{ color: 'var(--color-accent-cyan)' }}>{
                risk.consecutiveLossReactivation === 'cooldown_bars' ? (risk.consecutiveLossAutoCooldown ? 'Por Velas (Optimizado por IA)' : `Por Velas (${risk.consecutiveLossCooldownBars || 20} velas cooldown)`) :
                risk.consecutiveLossReactivation === 'next_session' ? 'Siguiente Sesión de Trading' :
                risk.consecutiveLossReactivation === 'next_day' ? 'Al Siguiente Día (00:00)' :
                risk.consecutiveLossReactivation === 'days_count' ? `Tras ${risk.consecutiveLossCooldownDays || 1} días de espera` :
                risk.consecutiveLossReactivation === 'next_week' ? 'A la Siguiente Semana (Lunes)' : 'Manual (Permanente)'
              }</strong></li>
            )}
            <li><span>TP/SL Management:</span> <strong style={{ color: 'var(--color-accent-cyan)' }}>{(config.tpslModes || []).length} Modos de Salida Activos</strong></li>
            <li><span>Spread / Comisión:</span> <strong>{risk.spreadPips || 0} pips / ${risk.commissionPerLot || 0} lot</strong></li>
          </ul>
        </div>

        <div className={styles.reviewCard}>
          <div className="flex items-center gap-2 mb-3 text-cyan">
            <Dna size={18} />
            <h4 style={{ margin: 0 }}>Genetic Programming</h4>
          </div>
          <ul>
            <li><span>Top Estrategias:</span> <strong style={{ color: 'var(--color-accent-cyan)' }}>{config.genetic.topStrategiesCount || 20} Estrategias</strong></li>
            <li><span>Population:</span> <strong>{config.genetic.populationSize}</strong></li>
            <li><span>Generations:</span> <strong>{config.genetic.generations}</strong></li>
            <li><span>Crossover:</span> <strong>{config.genetic.crossoverProb}</strong></li>
            <li><span>Mutation:</span> <strong>{config.genetic.mutationProb}</strong></li>
          </ul>
        </div>

        <div className={styles.reviewCard}>
          <div className="flex items-center gap-2 mb-3 text-cyan">
            <ShieldCheck size={18} />
            <h4 style={{ margin: 0 }}>Advanced & Validation</h4>
          </div>
          <ul>
            <li><span>RL Optimizer:</span> <strong>{config.rl.enabled ? config.rl.algorithm.toUpperCase() : 'Disabled'}</strong></li>
            <li><span>Monte Carlo Sims:</span> <strong>{config.montecarlo.simulations}</strong></li>
            <li><span>MC Method:</span> <strong>{config.montecarlo.method}</strong></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default StepReview;
