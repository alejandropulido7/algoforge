import React from 'react';
import { Database, Sliders, Dna, ShieldCheck, Scale } from 'lucide-react';
import { useJobStore } from '../../store/jobStore';
import styles from '../../styles/pages.module.css';

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

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Review Configuration</h2>
      <p className={styles.stepSubtitle}>Verify your pipeline settings before starting the generation job.</p>

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
            <h4 style={{ margin: 0 }}>Strategia & Gestión de Riesgo</h4>
          </div>
          <ul>
            <li><span>Enfoque:</span> <strong style={{ color: 'var(--color-accent-amber)' }}>{
              risk.strategyApproach === 'break_retest' ? 'Break & Retest' :
              risk.strategyApproach === 'fakeout' ? 'Fakeout (Reversión)' :
              risk.strategyApproach === 'breakout' ? 'Breakout Directo' :
              risk.strategyApproach === 'reversion' ? 'Reversión Tendencia' :
              risk.strategyApproach === 'pullback' ? 'Pullback Dinámico' : 'Cualquiera (Auto)'
            }</strong></li>
            <li><span>Direction:</span> <strong>{risk.direction === 'long' ? 'Long Only' : (risk.direction === 'short' ? 'Short Only' : 'Long & Short')}</strong></li>
            <li><span>Order Mode:</span> <strong>{risk.orderType === 'stop' ? 'Buy/Sell Stop' : (risk.orderType === 'limit' ? 'Buy/Sell Limit' : 'On Market')}</strong></li>
            {risk.orderType !== 'market' && (
              <li><span>Pending Timeout:</span> <strong>{risk.pendingTimeoutBars || 3} velas ({risk.pendingOffsetPips || 5} pips)</strong></li>
            )}
            <li><span>Holding Limit:</span> <strong>{risk.maxHoldingBars ? `${risk.maxHoldingBars} velas` : 'Disabled (SL/TP Only)'}</strong></li>
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
            <li><span>Sizing Mode:</span> <strong>{risk.sizingMode === 'lots' ? `${risk.lotSize} Fixed Lots` : `${risk.riskPct}% Risk / Trade`}</strong></li>
            <li><span>Stop Loss:</span> <strong>{risk.slType === 'pips' ? `${risk.slPips} Pips` : (risk.slType === 'atr' ? `${risk.slAtrMult}x ATR` : 'Signal Only')}</strong></li>
            <li><span>Take Profit:</span> <strong>{risk.tpType === 'pips' ? `${risk.tpPips} Pips` : (risk.tpType === 'atr' ? `${risk.tpAtrMult}x ATR` : 'Signal Only')}</strong></li>
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
