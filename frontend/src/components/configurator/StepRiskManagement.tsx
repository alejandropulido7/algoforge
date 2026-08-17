import React from 'react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import { ShieldCheck, Scale, Target, Percent, Sliders, Layers, ArrowLeftRight, TrendingUp, TrendingDown } from 'lucide-react';
import styles from '../../styles/pages.module.css';

export const StepRiskManagement: React.FC = () => {
  const { config, updateRisk } = useJobStore();
  const risk = config.risk || {
    initialDeposit: 10000,
    sizingMode: 'lots',
    lotSize: 0.1,
    riskPct: 1.0,
    direction: 'both',
    slType: 'pips',
    slPips: 50.0,
    slAtrMult: 1.5,
    tpType: 'pips',
    tpPips: 100.0,
    tpAtrMult: 3.0,
    contractSize: 100000,
    pointSize: 0.0001,
  };

  const currentDir = risk.direction || 'both';

  return (
    <div className={styles.stepContainer}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={22} color="var(--color-accent-cyan)" />
          Risk & Money Management
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Configure trade direction, position sizing, Stop Loss, Take Profit, and contract parameters matching MT5 execution.
        </p>
      </div>

      {/* Trade Direction Selector Banner */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <ArrowLeftRight size={18} color="var(--color-accent-cyan)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            Allowed Trade Direction
          </h3>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Select whether the generated strategies should seek buy setups, short setups, or both market directions.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
          <button
            type="button"
            onClick={() => updateRisk({ direction: 'both' })}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '0.375rem',
              padding: '0.875rem 1rem',
              borderRadius: '6px',
              border: currentDir === 'both' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
              background: currentDir === 'both' ? 'rgba(0, 212, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ArrowLeftRight size={16} color={currentDir === 'both' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: currentDir === 'both' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>
                Long & Short
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              Trades both bullish buy signals and bearish sell signals.
            </span>
          </button>

          <button
            type="button"
            onClick={() => updateRisk({ direction: 'long' })}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '0.375rem',
              padding: '0.875rem 1rem',
              borderRadius: '6px',
              border: currentDir === 'long' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
              background: currentDir === 'long' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp size={16} color={currentDir === 'long' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: currentDir === 'long' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)' }}>
                Long Only (Compras)
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              Only executes buy orders, suitable for spot or trending bull markets.
            </span>
          </button>

          <button
            type="button"
            onClick={() => updateRisk({ direction: 'short' })}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: '0.375rem',
              padding: '0.875rem 1rem',
              borderRadius: '6px',
              border: currentDir === 'short' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
              background: currentDir === 'short' ? 'rgba(244, 63, 94, 0.08)' : 'rgba(255, 255, 255, 0.02)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingDown size={16} color={currentDir === 'short' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: currentDir === 'short' ? 'var(--color-accent-rose)' : 'var(--color-text-main)' }}>
                Short Only (Ventas)
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              Only executes sell short orders, ideal for hedging or bear market regimes.
            </span>
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        
        {/* Section 1: Position Sizing Mode */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Scale size={18} color="var(--color-accent-cyan)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Position Sizing
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ sizingMode: 'lots' })}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                padding: '0.625rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: 500,
                border: risk.sizingMode === 'lots' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                background: risk.sizingMode === 'lots' ? 'rgba(0, 212, 255, 0.1)' : 'transparent',
                color: risk.sizingMode === 'lots' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <Layers size={16} />
              Fixed Lots
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ sizingMode: 'risk_pct' })}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                padding: '0.625rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: 500,
                border: risk.sizingMode === 'risk_pct' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                background: risk.sizingMode === 'risk_pct' ? 'rgba(0, 212, 255, 0.1)' : 'transparent',
                color: risk.sizingMode === 'risk_pct' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <Percent size={16} />
              Risk % Equity
            </button>
          </div>

          {risk.sizingMode === 'lots' ? (
            <Input
              id="risk-lot-size"
              label="Fixed Lot Size"
              type="number"
              step="0.01"
              min="0.01"
              value={risk.lotSize}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ lotSize: parseFloat(e.target.value) || 0.01 })}
              tooltip="Fixed trading volume per position in standard lots (e.g. 0.10 lots = 10,000 units on Forex, 0.10 contract on Crypto/Indices)."
              tooltipTitle="Lot Size"
            />
          ) : (
            <Input
              id="risk-pct-size"
              label="Risk % per Trade"
              type="number"
              step="0.1"
              min="0.1"
              max="10.0"
              value={risk.riskPct}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ riskPct: parseFloat(e.target.value) || 1.0 })}
              tooltip="Percentage of account equity risked on each trade. Volume is dynamically calculated so that reaching the Stop Loss equals this loss amount."
              tooltipTitle="Risk Percentage"
            />
          )}

          <div style={{ marginTop: '0.75rem' }}>
            <Input
              id="risk-initial-deposit"
              label="Initial Deposit ($)"
              type="number"
              step="100"
              min="100"
              value={risk.initialDeposit}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ initialDeposit: parseFloat(e.target.value) || 10000 })}
              tooltip="Starting capital in USD used for backtesting and return calculations."
              tooltipTitle="Initial Deposit"
            />
          </div>
        </div>

        {/* Section 2: Stop Loss Configuration */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Target size={18} color="var(--color-accent-rose)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Stop Loss (SL)
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.375rem', marginBottom: '1rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ slType: 'pips' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.slType === 'pips' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
                background: risk.slType === 'pips' ? 'rgba(244, 63, 94, 0.1)' : 'transparent',
                color: risk.slType === 'pips' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              Fixed Pips
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ slType: 'atr' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.slType === 'atr' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
                background: risk.slType === 'atr' ? 'rgba(244, 63, 94, 0.1)' : 'transparent',
                color: risk.slType === 'atr' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              ATR Multiple
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ slType: 'none' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.slType === 'none' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
                background: risk.slType === 'none' ? 'rgba(244, 63, 94, 0.1)' : 'transparent',
                color: risk.slType === 'none' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              Signal Only
            </button>
          </div>

          {risk.slType === 'pips' && (
            <Input
              id="risk-sl-pips"
              label="Stop Loss (Pips)"
              type="number"
              step="1"
              min="1"
              value={risk.slPips}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ slPips: parseFloat(e.target.value) || 50.0 })}
              tooltip="Distance in pips from entry price for the Stop Loss order."
              tooltipTitle="Fixed Stop Loss"
            />
          )}

          {risk.slType === 'atr' && (
            <Input
              id="risk-sl-atr"
              label="SL ATR Multiplier (x ATR)"
              type="number"
              step="0.1"
              min="0.5"
              value={risk.slAtrMult}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ slAtrMult: parseFloat(e.target.value) || 1.5 })}
              tooltip="Dynamic stop loss calculated as a multiple of the current Average True Range (e.g. 1.5x ATR)."
              tooltipTitle="ATR Stop Loss"
            />
          )}

          {risk.slType === 'none' && (
            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', padding: '0.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              Positions will remain open until an opposite exit signal is generated.
            </div>
          )}
        </div>

        {/* Section 3: Take Profit Configuration */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Target size={18} color="var(--color-accent-emerald)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Take Profit (TP)
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.375rem', marginBottom: '1rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ tpType: 'pips' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.tpType === 'pips' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                background: risk.tpType === 'pips' ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                color: risk.tpType === 'pips' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              Fixed Pips
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ tpType: 'atr' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.tpType === 'atr' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                background: risk.tpType === 'atr' ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                color: risk.tpType === 'atr' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              ATR Multiple
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ tpType: 'none' })}
              style={{
                padding: '0.5rem',
                borderRadius: '6px',
                fontSize: '0.8125rem',
                fontWeight: 500,
                border: risk.tpType === 'none' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                background: risk.tpType === 'none' ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                color: risk.tpType === 'none' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              Signal Only
            </button>
          </div>

          {risk.tpType === 'pips' && (
            <Input
              id="risk-tp-pips"
              label="Take Profit (Pips)"
              type="number"
              step="1"
              min="1"
              value={risk.tpPips}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ tpPips: parseFloat(e.target.value) || 100.0 })}
              tooltip="Distance in pips from entry price for the Take Profit order."
              tooltipTitle="Fixed Take Profit"
            />
          )}

          {risk.tpType === 'atr' && (
            <Input
              id="risk-tp-atr"
              label="TP ATR Multiplier (x ATR)"
              type="number"
              step="0.1"
              min="0.5"
              value={risk.tpAtrMult}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ tpAtrMult: parseFloat(e.target.value) || 3.0 })}
              tooltip="Dynamic take profit calculated as a multiple of the current Average True Range (e.g. 3.0x ATR)."
              tooltipTitle="ATR Take Profit"
            />
          )}

          {risk.tpType === 'none' && (
            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', padding: '0.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              Positions will close only upon reaching an opposite exit signal.
            </div>
          )}
        </div>

        {/* Section 4: Contract & Point Parameters */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Sliders size={18} color="var(--color-accent-amber)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Symbol & Contract Spec
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <Input
              id="risk-contract-size"
              label="Contract Size"
              type="number"
              step="1000"
              min="1"
              value={risk.contractSize}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ contractSize: parseFloat(e.target.value) || 100000 })}
              tooltip="Units per standard lot (e.g. 100,000 for Forex EURUSD, 1 for Crypto/Indices)."
              tooltipTitle="Contract Size"
            />
            <Input
              id="risk-point-size"
              label="Point / Pip Size"
              type="number"
              step="0.00001"
              min="0.00001"
              value={risk.pointSize}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ pointSize: parseFloat(e.target.value) || 0.0001 })}
              tooltip="Minimum price increment (0.0001 for 4-digit Forex, 0.00001 for 5-digit Forex, 0.01 for Crypto/JPY/Gold)."
              tooltipTitle="Point Size"
            />
          </div>
        </div>

      </div>
    </div>
  );
};
