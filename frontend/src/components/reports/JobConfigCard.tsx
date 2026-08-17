import React, { useState } from 'react';
import { 
  Sliders, 
  Calendar, 
  Layers, 
  ShieldCheck, 
  Dna, 
  ChevronDown, 
  ChevronUp
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
  const rl = config.rl || {};
  const mc = config.montecarlo || {};

  const directionLabel = 
    risk.direction === 'long' || risk.direction === 'long_only' ? 'Long Only 🟢' :
    risk.direction === 'short' || risk.direction === 'short_only' ? 'Short Only 🔴' : 
    'Long & Short 🔄';

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
            {symbol} • {timeframe} • {startDate} ➔ {endDate}
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
                indicators.map((ind, i) => (
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
              <span>Risk & Trade Management</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>DIRECTION</span>
                <span style={{ fontWeight: 600, color: 'var(--color-accent-emerald)' }}>{directionLabel}</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>RISK / TRADE</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{risk.riskPct || 1}%</span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>STOP LOSS</span>
                <span style={{ color: 'var(--color-accent-rose)', fontWeight: 600 }}>
                  {risk.slAtrMult ? `${risk.slAtrMult}x ATR` : `${risk.slPips || 50} pips`}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>TAKE PROFIT</span>
                <span style={{ color: 'var(--color-accent-emerald)', fontWeight: 600 }}>
                  {risk.tpAtrMult ? `${risk.tpAtrMult}x ATR` : `${risk.tpPips || 100} pips`}
                </span>
              </div>
            </div>
          </div>

          {/* Section 4: AI & Exploration Parameters */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.75rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
              <Dna size={15} />
              <span>AI Search & Monte Carlo</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>GENETIC POOL</span>
                <span style={{ color: 'var(--color-text-main)', fontWeight: 500 }}>
                  {genetic.populationSize || 100} pop × {genetic.generations || 50} gen
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>DEEP RL (PPO)</span>
                <span style={{ color: rl.enabled ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)', fontWeight: 500 }}>
                  {rl.enabled ? `${rl.algorithm?.toUpperCase() || 'PPO'} (${rl.timesteps || 100000} steps)` : 'Disabled'}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>MONTE CARLO</span>
                <span style={{ color: 'var(--color-text-main)', fontWeight: 500 }}>
                  {mc.simulations || 1000} sims ({mc.method || 'Permutation'})
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--color-text-muted)', display: 'block', fontSize: '0.6875rem' }}>RUIN THRESHOLD</span>
                <span style={{ color: 'var(--color-accent-rose)', fontWeight: 500 }}>
                  {mc.ruinThreshold || 20}%
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
