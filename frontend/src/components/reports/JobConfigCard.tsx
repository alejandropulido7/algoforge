import React, { useState } from 'react';
import { 
  Sliders, 
  Calendar, 
  Layers, 
  ShieldCheck, 
  ChevronDown, 
  ChevronUp,
  Clock
} from 'lucide-react';
import type { JobConfig } from '../../types/job';

interface JobConfigCardProps {
  config?: JobConfig;
  defaultExpanded?: boolean;
}

export const JobConfigCard: React.FC<JobConfigCardProps> = ({ config, defaultExpanded = true }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!config) return null;

  const dataSrc: any = config.dataSource || (config as any).data_source || {};
  const symbol = dataSrc.symbol || (config as any).symbol || 'EURUSD';
  const timeframe = dataSrc.timeframe || (config as any).timeframe || '1h';
  const startDate = dataSrc.startDate || dataSrc.start_date || (config as any).start_date || 'N/A';
  const endDate = dataSrc.endDate || dataSrc.end_date || (config as any).end_date || 'N/A';
  const source = dataSrc.source || 'csv';

  const indicators = config.indicators || [];
  const risk = (config as any).risk || {};
  const genetic = config.genetic || {};

  const directionLabel = 
    risk.direction === 'long' || risk.direction === 'long_only' ? 'Long Only 🟢' :
    risk.direction === 'short' || risk.direction === 'short_only' ? 'Short Only 🔴' : 
    'Long & Short 🔄';

  const orderTypeLabel = 
    risk.orderType === 'stop' ? 'Buy/Sell Stop ⏳' :
    risk.orderType === 'limit' ? 'Buy/Sell Limit 🎯' :
    'On Market ⚡';

  return (
    <div style={{
      background: 'var(--color-bg-card)',
      border: '1px solid var(--color-border)',
      borderRadius: '8px',
      marginBottom: '1.5rem',
      overflow: 'hidden'
    }}>
      {/* Header Bar */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.875rem 1.25rem',
          background: 'rgba(255, 255, 255, 0.02)',
          cursor: 'pointer',
          borderBottom: isExpanded ? '1px solid var(--color-border)' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <Sliders size={18} color="var(--color-accent-cyan)" />
          <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: 'var(--color-text-main)' }}>
            Pipeline & Strategy Configuration
          </span>
          <span style={{ 
            fontSize: '0.75rem', 
            color: 'var(--color-text-muted)', 
            background: 'rgba(255, 255, 255, 0.05)', 
            padding: '0.125rem 0.5rem', 
            borderRadius: '4px' 
          }}>
            {symbol} • {timeframe} • {orderTypeLabel} • {startDate} ➔ {endDate}
          </span>
        </div>

        <button
          type="button"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--color-text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            fontSize: '0.8125rem',
            cursor: 'pointer'
          }}
        >
          <span>{isExpanded ? 'Hide Details' : 'Show Details'}</span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Expanded Content Grid */}
      {isExpanded && (
        <div style={{
          padding: '1.25rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '1.25rem'
        }}>
          {/* Section 1: Data & Timeframe */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
              <Calendar size={15} />
              <span>Data & Timeframe</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>SYMBOL</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{symbol}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>TIMEFRAME</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{timeframe}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>SOURCE</span>
                <span style={{ color: 'var(--color-accent-amber)', textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 600 }}>{source}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>DATE RANGE</span>
                <span style={{ color: 'var(--color-text-main)', fontSize: '0.75rem' }}>{startDate} ➔ {endDate}</span>
              </div>
            </div>
          </div>

          {/* Section 2: Selected Indicators */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
              <Layers size={15} />
              <span>Evaluated Indicators ({indicators.length})</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {indicators.length > 0 ? (
                indicators.map((ind: string, i: number) => (
                  <span
                    key={i}
                    style={{
                      background: 'rgba(0, 212, 255, 0.08)',
                      border: '1px solid rgba(0, 212, 255, 0.2)',
                      color: 'var(--color-accent-cyan)',
                      fontSize: '0.6875rem',
                      fontWeight: 500,
                      padding: '0.1875rem 0.4375rem',
                      borderRadius: '4px'
                    }}
                  >
                    {ind}
                  </span>
                ))
              ) : (
                <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>None specified</span>
              )}
            </div>
          </div>

          {/* Section 3: Risk & Execution Rules */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
              <ShieldCheck size={15} />
              <span>Strategy & Trade Management</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>CAPITAL & SIZING</span>
                <span style={{ fontWeight: 600, color: 'var(--color-accent-cyan)' }}>
                  ${(risk.initialDeposit ?? 10000).toLocaleString()} • {
                    (risk.sizingMode || 'lots') === 'lots' 
                      ? `${risk.lotSize ?? 0.1} Lots` 
                      : `${risk.riskPct ?? 1.0}% Riesgo (${(risk.riskBase || 'initial_deposit') === 'initial_deposit' ? 'Fijo' : 'Compuesto'})`
                  }
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>SIMULTANEOUS TRADES</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{risk.maxSimultaneousTrades || 1} Max</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>DIRECTION</span>
                <span style={{ fontWeight: 600, color: 'var(--color-accent-emerald)' }}>{directionLabel}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>EXECUTION MODE</span>
                <span style={{ fontWeight: 600, color: 'var(--color-accent-cyan)' }}>{orderTypeLabel}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>RACHA PÉRDIDAS</span>
                <span style={{ color: risk.consecutiveLossAction !== 'none' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)', fontSize: '0.75rem', fontWeight: 500 }}>
                  {risk.consecutiveLossAction === 'reduce_risk' ? `Reducir ${risk.consecutiveLossReductionPct || 50}% tras ${risk.consecutiveLossThreshold || 3}L` :
                   risk.consecutiveLossAction === 'stop_bot' ? `Pausar tras ${risk.consecutiveLossThreshold || 3}L` : 'Normal'}
                </span>
                {risk.consecutiveLossAction === 'stop_bot' && (
                  <span style={{ display: 'block', fontSize: '0.6875rem', color: 'var(--color-accent-cyan)', marginTop: '0.125rem' }}>
                    {risk.consecutiveLossReactivation === 'cooldown_bars' ? (risk.consecutiveLossAutoCooldown ? 'Auto Cooldown IA' : `${risk.consecutiveLossCooldownBars || 20} velas cooldown`) :
                     risk.consecutiveLossReactivation === 'next_session' ? 'Reactivar prox sesión' :
                     risk.consecutiveLossReactivation === 'next_day' ? 'Reactivar prox día' :
                     risk.consecutiveLossReactivation === 'days_count' ? `Reactivar en ${risk.consecutiveLossCooldownDays || 1}d` :
                     risk.consecutiveLossReactivation === 'next_week' ? 'Reactivar prox semana' : 'Reinicio manual'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Section 4: Genetic & AI Pool */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
              <Clock size={15} />
              <span>Algoritmo Genético</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>TOP ESTRATEGIAS</span>
                <span style={{ color: 'var(--color-accent-cyan)', fontWeight: 600 }}>
                  {genetic.topStrategiesCount || 20} Estrategias
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>GENETIC POOL</span>
                <span style={{ color: 'var(--color-text-main)', fontWeight: 500 }}>
                  {genetic.populationSize || 100}p × {genetic.generations || 50}g
                </span>
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default JobConfigCard;
