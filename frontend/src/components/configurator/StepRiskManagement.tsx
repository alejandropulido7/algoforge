import React from 'react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import { TPSLManagementSection } from './TPSLManagementSection';
import { 
  Scale, 
  Sliders, 
  Layers, 
  ArrowLeftRight, 
  TrendingUp, 
  TrendingDown, 
  Clock,
  Zap,
  ArrowUpRight,
  ArrowDownLeft,
  Timer,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Percent,
  DollarSign
} from 'lucide-react';
import styles from '../../styles/pages.module.css';

export const StepRiskManagement: React.FC = () => {
  const { config, updateRisk } = useJobStore();
  const risk = config.risk || {
    direction: 'both',
    orderType: 'market',
    maxSimultaneousTrades: 1,
    consecutiveLossAction: 'none',
    consecutiveLossThreshold: 3,
    consecutiveLossReductionPct: 50,
    consecutiveLossReactivation: 'none',
    consecutiveLossCooldownBars: 20,
    consecutiveLossCooldownDays: 1,
    consecutiveLossAutoCooldown: true,
    contractSize: 100000,
    pointSize: 0.0001,
    spreadPips: 1.0,
    commissionPerLot: 7.0,
    commissionPerSide: true,
    swapPerLotPerDay: 0.0,
  };

  const currentDir = risk.direction || 'both';
  const currentOrderType = risk.orderType || 'market';
  const currentLossAction = risk.consecutiveLossAction || 'none';

  return (
    <div className={styles.stepContainer} style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={22} color="var(--color-accent-cyan)" />
          Strategy Config & Gestión de Ejecución
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Configura la dirección operativa permitida, el modo de ejecución de órdenes, operaciones simultáneas, protección contra rachas perdedoras y costos de MT5.
        </p>
      </div>

      {/* 1. Direction and Order Execution Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* Trade Direction Selector */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <ArrowLeftRight size={18} color="var(--color-accent-cyan)" />
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Dirección de Operaciones Permitida
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Define si el algoritmo busca compras (Long), ventas en corto (Short), o ambas direcciones.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ direction: 'both' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentDir === 'both' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                background: currentDir === 'both' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <ArrowLeftRight size={16} color={currentDir === 'both' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentDir === 'both' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>
                Long & Short
              </span>
            </button>

            <button
              type="button"
              onClick={() => updateRisk({ direction: 'long' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentDir === 'long' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                background: currentDir === 'long' ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <TrendingUp size={16} color={currentDir === 'long' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentDir === 'long' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)' }}>
                Long Only
              </span>
            </button>

            <button
              type="button"
              onClick={() => updateRisk({ direction: 'short' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentDir === 'short' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
                background: currentDir === 'short' ? 'rgba(244, 63, 94, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <TrendingDown size={16} color={currentDir === 'short' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentDir === 'short' ? 'var(--color-accent-rose)' : 'var(--color-text-main)' }}>
                Short Only
              </span>
            </button>
          </div>
        </div>

        {/* Order Execution Type Selector */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Zap size={18} color="var(--color-accent-amber)" />
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Tipo de Entrada / Órdenes
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Mecanismo de ejecución testeado en el backtest y exportado a MT5.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ orderType: 'market' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentOrderType === 'market' ? '1px solid var(--color-accent-amber)' : '1px solid var(--color-border)',
                background: currentOrderType === 'market' ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <Zap size={16} color={currentOrderType === 'market' ? 'var(--color-accent-amber)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentOrderType === 'market' ? 'var(--color-accent-amber)' : 'var(--color-text-main)' }}>
                A Mercado
              </span>
            </button>

            <button
              type="button"
              onClick={() => updateRisk({ orderType: 'stop' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentOrderType === 'stop' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                background: currentOrderType === 'stop' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <ArrowUpRight size={16} color={currentOrderType === 'stop' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentOrderType === 'stop' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>
                Buy/Sell Stop
              </span>
            </button>

            <button
              type="button"
              onClick={() => updateRisk({ orderType: 'limit' })}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.75rem 0.5rem',
                borderRadius: '6px',
                border: currentOrderType === 'limit' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                background: currentOrderType === 'limit' ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'center'
              }}
            >
              <ArrowDownLeft size={16} color={currentOrderType === 'limit' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)'} />
              <span style={{ fontWeight: 600, fontSize: '0.75rem', color: currentOrderType === 'limit' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)' }}>
                Buy/Sell Limit
              </span>
            </button>
          </div>
        </div>

      </div>

      {/* 2. Capital, Sizing & Simultaneous Trades Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* Card 1: Capital Inicial y Dimensionamiento de Posición */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <DollarSign size={18} color="var(--color-accent-cyan)" />
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Capital & Dimensionamiento de Posición
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
            Define el depósito inicial y si el tamaño de posición se calcula por lotaje fijo o porcentaje de riesgo.
          </p>

          {/* Depósito Inicial */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
              Depósito Inicial ($ USD)
            </label>
            <input
              type="number"
              min="100"
              step="100"
              value={risk.initialDeposit ?? 10000}
              onChange={(e) => updateRisk({ initialDeposit: Math.max(10, Number(e.target.value) || 10000) })}
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid var(--color-border)',
                background: 'var(--color-bg-tertiary)',
                color: 'var(--color-text-main)',
                fontSize: '0.875rem'
              }}
            />
          </div>

          {/* Selector de Modo de Dimensionamiento */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.375rem' }}>
              Modo de Cálculo de Tamaño
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <button
                type="button"
                onClick={() => updateRisk({ sizingMode: 'lots' })}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.375rem',
                  padding: '0.625rem 0.5rem',
                  borderRadius: '6px',
                  border: (risk.sizingMode || 'lots') === 'lots' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  background: (risk.sizingMode || 'lots') === 'lots' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  color: (risk.sizingMode || 'lots') === 'lots' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)',
                  fontWeight: 600,
                  fontSize: '0.75rem'
                }}
              >
                <Layers size={14} />
                <span>Lote Fijo</span>
              </button>

              <button
                type="button"
                onClick={() => updateRisk({ sizingMode: 'risk_pct' })}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.375rem',
                  padding: '0.625rem 0.5rem',
                  borderRadius: '6px',
                  border: risk.sizingMode === 'risk_pct' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                  background: risk.sizingMode === 'risk_pct' ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  color: risk.sizingMode === 'risk_pct' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)',
                  fontWeight: 600,
                  fontSize: '0.75rem'
                }}
              >
                <Percent size={14} />
                <span>% de Riesgo</span>
              </button>
            </div>
          </div>

          {/* Conditional Input based on sizing mode */}
          {(risk.sizingMode || 'lots') === 'lots' ? (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                Lote por Operación
              </label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={risk.lotSize ?? 0.1}
                onChange={(e) => updateRisk({ lotSize: Math.max(0.01, Number(e.target.value) || 0.1) })}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-main)',
                  fontSize: '0.875rem'
                }}
              />
              <span style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)', marginTop: '0.25rem', display: 'block' }}>
                Volumen constante por trade (ej. 0.10 lotes estándar = 10,000 unidades).
              </span>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                  % de Riesgo por Operación
                </label>
                <input
                  type="number"
                  min="0.1"
                  max="100"
                  step="0.1"
                  value={risk.riskPct ?? 1.0}
                  onChange={(e) => updateRisk({ riskPct: Math.max(0.1, Number(e.target.value) || 1.0) })}
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem',
                    borderRadius: '6px',
                    border: '1px solid var(--color-border)',
                    background: 'var(--color-bg-tertiary)',
                    color: 'var(--color-text-main)',
                    fontSize: '0.875rem'
                  }}
                />
              </div>

              {/* Base del Porcentaje de Riesgo */}
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.375rem' }}>
                  Base de Cálculo del Porcentaje de Riesgo
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <button
                    type="button"
                    onClick={() => updateRisk({ riskBase: 'initial_deposit' })}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '0.25rem',
                      padding: '0.625rem 0.5rem',
                      borderRadius: '6px',
                      border: (risk.riskBase || 'initial_deposit') === 'initial_deposit' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                      background: (risk.riskBase || 'initial_deposit') === 'initial_deposit' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                      cursor: 'pointer',
                      textAlign: 'center'
                    }}
                  >
                    <span style={{ fontWeight: 600, fontSize: '0.75rem', color: (risk.riskBase || 'initial_deposit') === 'initial_deposit' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>
                      Depósito Inicial
                    </span>
                    <span style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>
                      Monto fijo por trade
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => updateRisk({ riskBase: 'balance' })}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '0.25rem',
                      padding: '0.625rem 0.5rem',
                      borderRadius: '6px',
                      border: risk.riskBase === 'balance' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                      background: risk.riskBase === 'balance' ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                      cursor: 'pointer',
                      textAlign: 'center'
                    }}
                  >
                    <span style={{ fontWeight: 600, fontSize: '0.75rem', color: risk.riskBase === 'balance' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)' }}>
                      Balance (Compuesto)
                    </span>
                    <span style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>
                      Interés compuesto
                    </span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Card 2: Operaciones Simultáneas */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <Layers size={18} color="var(--color-accent-cyan)" />
              <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
                Operaciones Simultáneas
              </h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
              Establece cuántas operaciones simultáneas puede abrir el bot al mismo tiempo si la condición de entrada se sigue cumpliendo en nuevas velas. (1 = Operación única por estrategia).
            </p>

            <div style={{ maxWidth: '280px', marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                Max Operaciones Simultáneas
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={risk.maxSimultaneousTrades || 1}
                onChange={(e) => updateRisk({ maxSimultaneousTrades: Number(e.target.value) || 1 })}
                style={{
                  width: '100%',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-main)',
                  fontSize: '0.875rem'
                }}
              />
            </div>
          </div>

          <div style={{
            background: 'rgba(0, 212, 255, 0.04)',
            border: '1px solid rgba(0, 212, 255, 0.15)',
            borderRadius: '6px',
            padding: '0.75rem',
            fontSize: '0.75rem',
            color: 'var(--color-text-muted)'
          }}>
            💡 <strong>Nota:</strong> Si se permite más de 1 posición simultánea, cada trade gestionará su propio Stop Loss y Take Profit independiente según el precio de apertura de su respectiva vela.
          </div>
        </div>

      </div>

      {/* 3. TP/SL Management Section */}
      <TPSLManagementSection />

      {/* 4. Consecutive Losses Protection (Kill Switch & Risk Reduction) */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <AlertTriangle size={18} color="var(--color-accent-rose)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            Protección de Pérdidas Consecutivas (Drawdown Kill-Switch)
          </h3>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Protege tu cuenta activando una reducción dinámica de lotaje o pausando las operaciones del bot tras acumular X pérdidas seguidas.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
          <button
            type="button"
            onClick={() => updateRisk({ consecutiveLossAction: 'none' })}
            style={{
              padding: '0.75rem',
              borderRadius: '6px',
              border: currentLossAction === 'none' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
              background: currentLossAction === 'none' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
              color: currentLossAction === 'none' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
              fontWeight: 500,
              fontSize: '0.8125rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
          >
            <RotateCcw size={15} />
            Sin Restricción (Normal)
          </button>

          <button
            type="button"
            onClick={() => updateRisk({ consecutiveLossAction: 'reduce_risk' })}
            style={{
              padding: '0.75rem',
              borderRadius: '6px',
              border: currentLossAction === 'reduce_risk' ? '1px solid var(--color-accent-amber)' : '1px solid var(--color-border)',
              background: currentLossAction === 'reduce_risk' ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
              color: currentLossAction === 'reduce_risk' ? 'var(--color-accent-amber)' : 'var(--color-text-muted)',
              fontWeight: 500,
              fontSize: '0.8125rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
          >
            <Percent size={15} />
            Reducir Riesgo tras X Pérdidas
          </button>

          <button
            type="button"
            onClick={() => updateRisk({ consecutiveLossAction: 'stop_bot' })}
            style={{
              padding: '0.75rem',
              borderRadius: '6px',
              border: currentLossAction === 'stop_bot' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
              background: currentLossAction === 'stop_bot' ? 'rgba(244, 63, 94, 0.08)' : 'transparent',
              color: currentLossAction === 'stop_bot' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)',
              fontWeight: 500,
              fontSize: '0.8125rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
          >
            <AlertTriangle size={15} />
            Detener Bot tras X Pérdidas
          </button>
        </div>

        {currentLossAction !== 'none' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px' }}>
            <Input
              id="risk-consec-threshold"
              label="Umbral de Pérdidas Consecutivas (X)"
              type="number"
              step="1"
              min="1"
              max="10"
              value={risk.consecutiveLossThreshold || 3}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ consecutiveLossThreshold: parseInt(e.target.value) || 3 })}
              tooltip="Número de pérdidas consecutivas requeridas para activar la acción de protección."
              tooltipTitle="Racha de Pérdidas"
            />
            {currentLossAction === 'reduce_risk' && (
              <Input
                id="risk-consec-reduction"
                label="% Reducción de Riesgo / Lote"
                type="number"
                step="5"
                min="10"
                max="90"
                value={risk.consecutiveLossReductionPct || 50}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ consecutiveLossReductionPct: parseInt(e.target.value) || 50 })}
                tooltip="Porcentaje al que se reduce el lotaje o riesgo durante la racha."
                tooltipTitle="Factor de Reducción"
              />
            )}
            {currentLossAction === 'stop_bot' && (
              <div style={{ fontSize: '0.8125rem', color: 'var(--color-accent-rose)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertTriangle size={16} />
                <span>El Asesor Experto se pausará automáticamente al alcanzar {risk.consecutiveLossThreshold || 3} pérdidas seguidas para evitar drawdowns profundos.</span>
              </div>
            )}
          </div>
        )}

        {/* Automatic Reactivation Options (When stop_bot is active) */}
        {currentLossAction === 'stop_bot' && (
          <div style={{ marginTop: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.375rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.875rem' }}>
              <Sparkles size={16} />
              <span>Alternativas de Reactivación Automática del Bot</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
              Define cuándo o cómo debe reactivarse la operativa tras detenerse por pérdidas consecutivas:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', marginBottom: '1rem' }}>
              {/* Option 1: Manual / Permanente */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'none' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: (risk.consecutiveLossReactivation || 'none') === 'none' ? '1px solid var(--color-accent-rose)' : '1px solid var(--color-border)',
                  background: (risk.consecutiveLossReactivation || 'none') === 'none' ? 'rgba(244, 63, 94, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <AlertTriangle size={15} color={(risk.consecutiveLossReactivation || 'none') === 'none' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: (risk.consecutiveLossReactivation || 'none') === 'none' ? 'var(--color-accent-rose)' : 'var(--color-text-main)' }}>Manual / Permanente</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Requiere reinicio manual</div>
                </div>
              </button>

              {/* Option 2: Velas de Enfriamiento (Cooldown) */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'cooldown_bars' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: risk.consecutiveLossReactivation === 'cooldown_bars' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  background: risk.consecutiveLossReactivation === 'cooldown_bars' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <Clock size={15} color={risk.consecutiveLossReactivation === 'cooldown_bars' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: risk.consecutiveLossReactivation === 'cooldown_bars' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>Por Tiempo (Velas)</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Velas de enfriamiento (IA/Manual)</div>
                </div>
              </button>

              {/* Option 3: Siguiente Sesión */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'next_session' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: risk.consecutiveLossReactivation === 'next_session' ? '1px solid var(--color-accent-amber)' : '1px solid var(--color-border)',
                  background: risk.consecutiveLossReactivation === 'next_session' ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <Timer size={15} color={risk.consecutiveLossReactivation === 'next_session' ? 'var(--color-accent-amber)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: risk.consecutiveLossReactivation === 'next_session' ? 'var(--color-accent-amber)' : 'var(--color-text-main)' }}>Siguiente Sesión</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Próxima sesión de trading</div>
                </div>
              </button>

              {/* Option 4: Al Siguiente Día */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'next_day' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: risk.consecutiveLossReactivation === 'next_day' ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                  background: risk.consecutiveLossReactivation === 'next_day' ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <TrendingUp size={15} color={risk.consecutiveLossReactivation === 'next_day' ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: risk.consecutiveLossReactivation === 'next_day' ? 'var(--color-accent-emerald)' : 'var(--color-text-main)' }}>Al Siguiente Día</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>A las 00:00 del próximo día</div>
                </div>
              </button>

              {/* Option 5: Cantidad de Días */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'days_count' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: risk.consecutiveLossReactivation === 'days_count' ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  background: risk.consecutiveLossReactivation === 'days_count' ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <Layers size={15} color={risk.consecutiveLossReactivation === 'days_count' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: risk.consecutiveLossReactivation === 'days_count' ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>Cantidad de Días (X)</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Pausar durante N días</div>
                </div>
              </button>

              {/* Option 6: Siguiente Semana */}
              <button
                type="button"
                onClick={() => updateRisk({ consecutiveLossReactivation: 'next_week' })}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: '6px',
                  border: risk.consecutiveLossReactivation === 'next_week' ? '1px solid var(--color-accent-amber)' : '1px solid var(--color-border)',
                  background: risk.consecutiveLossReactivation === 'next_week' ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  textAlign: 'left'
                }}
              >
                <Sliders size={15} color={risk.consecutiveLossReactivation === 'next_week' ? 'var(--color-accent-amber)' : 'var(--color-text-muted)'} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: risk.consecutiveLossReactivation === 'next_week' ? 'var(--color-accent-amber)' : 'var(--color-text-main)' }}>Siguiente Semana</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)' }}>Pausar hasta el lunes</div>
                </div>
              </button>
            </div>

            {/* Cooldown Bars sub-config */}
            {risk.consecutiveLossReactivation === 'cooldown_bars' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', background: 'rgba(0, 212, 255, 0.03)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(0, 212, 255, 0.12)', alignItems: 'center' }}>
                <div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: 'var(--color-text-main)', fontWeight: 500 }}>
                    <input
                      type="checkbox"
                      checked={risk.consecutiveLossAutoCooldown ?? true}
                      onChange={(e) => updateRisk({ consecutiveLossAutoCooldown: e.target.checked })}
                      style={{ accentColor: 'var(--color-accent-cyan)', width: '16px', height: '16px' }}
                    />
                    <span>✨ <b>Que la IA defina automáticamente</b> las velas de enfriamiento</span>
                  </label>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted)', margin: '0.25rem 0 0 1.5rem', lineHeight: '1.3' }}>
                    La IA analizará los patrones de rachas desfavorables para optimizar el período de cooldown.
                  </p>
                </div>

                {!risk.consecutiveLossAutoCooldown && (
                  <Input
                    id="risk-consec-cooldown-bars"
                    label="Velas fijas de enfriamiento"
                    type="number"
                    step="1"
                    min="1"
                    max="500"
                    value={risk.consecutiveLossCooldownBars || 20}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ consecutiveLossCooldownBars: parseInt(e.target.value) || 20 })}
                    tooltip="Cantidad exacta de velas que el bot esperará antes de reactivarse tras la racha de pérdidas."
                    tooltipTitle="Velas de Enfriamiento"
                  />
                )}
              </div>
            )}

            {/* Days Count sub-config */}
            {risk.consecutiveLossReactivation === 'days_count' && (
              <div style={{ background: 'rgba(0, 212, 255, 0.03)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(0, 212, 255, 0.12)', maxWidth: '320px' }}>
                <Input
                  id="risk-consec-cooldown-days"
                  label="Cantidad de Días a Esperar"
                  type="number"
                  step="1"
                  min="1"
                  max="30"
                  value={risk.consecutiveLossCooldownDays || 1}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ consecutiveLossCooldownDays: parseInt(e.target.value) || 1 })}
                  tooltip="Días que deben transcurrir tras la racha de pérdidas antes de permitir nuevas operaciones."
                  tooltipTitle="Días de Espera"
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* 4. Symbol & Contract Spec and MT5 Realistic Costs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        
        {/* Symbol & Contract Spec */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sliders size={18} color="var(--color-accent-amber)" />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
                Symbol & Contract Spec
              </h3>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-accent-cyan)', background: 'rgba(0, 212, 255, 0.08)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
              MT5 Spec Sync
            </span>
          </div>

          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Copia los valores desde la ventana <strong>Especificación de MT5</strong> para calcular el valor exacto del pip:
          </p>

          {/* Quick Presets for Common Asset Classes */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginBottom: '1rem' }}>
            <button
              type="button"
              onClick={() => updateRisk({ contractSize: 1, pointSize: 0.01 })}
              style={{
                fontSize: '0.6875rem',
                padding: '3px 8px',
                borderRadius: '4px',
                background: risk.contractSize === 1 && risk.pointSize === 0.01 ? 'rgba(0, 212, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: risk.contractSize === 1 && risk.pointSize === 0.01 ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                color: risk.contractSize === 1 && risk.pointSize === 0.01 ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              🏛️ Índices (NAS100 / US30): 1 & 0.01
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ contractSize: 100, pointSize: 0.01 })}
              style={{
                fontSize: '0.6875rem',
                padding: '3px 8px',
                borderRadius: '4px',
                background: risk.contractSize === 100 && risk.pointSize === 0.01 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: risk.contractSize === 100 && risk.pointSize === 0.01 ? '1px solid var(--color-accent-amber)' : '1px solid var(--color-border)',
                color: risk.contractSize === 100 && risk.pointSize === 0.01 ? 'var(--color-accent-amber)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              🪙 Oro (XAUUSD): 100 & 0.01
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ contractSize: 100000, pointSize: 0.00001 })}
              style={{
                fontSize: '0.6875rem',
                padding: '3px 8px',
                borderRadius: '4px',
                background: risk.contractSize === 100000 && risk.pointSize === 0.00001 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: risk.contractSize === 100000 && risk.pointSize === 0.00001 ? '1px solid var(--color-accent-emerald)' : '1px solid var(--color-border)',
                color: risk.contractSize === 100000 && risk.pointSize === 0.00001 ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              💱 Forex 5D (EURUSD): 100k & 0.00001
            </button>
            <button
              type="button"
              onClick={() => updateRisk({ contractSize: 1, pointSize: 0.01 })}
              style={{
                fontSize: '0.6875rem',
                padding: '3px 8px',
                borderRadius: '4px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-muted)',
                cursor: 'pointer'
              }}
            >
              ₿ Crypto (BTCUSD): 1 & 0.01
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <Input
              id="risk-contract-size"
              label="Contract Size (MT5 'Contract size')"
              type="number"
              step="1"
              min="1"
              value={risk.contractSize}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ contractSize: parseFloat(e.target.value) || 1 })}
              tooltip="Valor 'Contract size' en MT5 (1 para NAS100/US30/Crypto, 100 para Oro, 100,000 para Forex)."
              tooltipTitle="Contract Size"
            />
            <Input
              id="risk-point-size"
              label="Point / Pip Size (10^-Digits)"
              type="number"
              step="0.00001"
              min="0.00001"
              value={risk.pointSize}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ pointSize: parseFloat(e.target.value) || 0.01 })}
              tooltip="Fórmula: Si MT5 Digits = 2 -> 0.01 (NAS100/XAUUSD). Si Digits = 5 -> 0.00001 (Forex). Si Digits = 3 -> 0.001 (JPY)."
              tooltipTitle="Point / Pip Size"
            />
          </div>

          <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.25)', borderRadius: '6px', fontSize: '0.6875rem', color: 'var(--color-text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <div>🔹 <strong>Contract Size:</strong> Copia directo el campo <code>Contract size</code> de la ficha MT5.</div>
            <div>🔹 <strong>Point / Pip Size:</strong> Se obtiene de los <code>Digits</code> de MT5: 2 dígitos = <code>0.01</code>, 3 dígitos = <code>0.001</code>, 5 dígitos = <code>0.00001</code>.</div>
          </div>
        </div>

        {/* MT5 Realistic Costs (Spread, Commission, Swap) */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Scale size={18} color="var(--color-accent-rose)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              MT5 Costs (Realismo del Backtest)
            </h3>
          </div>

          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            El simulador cobra los costos que MT5 aplica en cada operación para evitar métricas irreales.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <Input
              id="risk-spread-pips"
              label="Spread (Pips)"
              type="number"
              step="0.1"
              min="0"
              value={risk.spreadPips}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ spreadPips: parseFloat(e.target.value) || 0 })}
              tooltip="Spread medio del símbolo en pips."
              tooltipTitle="Spread Bid/Ask"
            />
            <Input
              id="risk-commission-lot"
              label="Comisión ($/lote)"
              type="number"
              step="0.5"
              min="0"
              value={risk.commissionPerLot}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ commissionPerLot: parseFloat(e.target.value) || 0 })}
              tooltip="Comisión por lote cobrada por el broker."
              tooltipTitle="Comisión por Lote"
            />
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: 'var(--color-text-main)', fontWeight: 500, padding: '0.25rem 0' }}>
              <input
                type="checkbox"
                checked={risk.commissionPerSide ?? true}
                onChange={(e) => updateRisk({ commissionPerSide: e.target.checked })}
                style={{ accentColor: 'var(--color-accent-rose)', width: '16px', height: '16px' }}
              />
              <span><b>Comisión por lado</b> (entrada + salida)</span>
            </label>
            <Input
              id="risk-swap-day"
              label="Swap ($/lote/día)"
              type="number"
              step="0.5"
              min="0"
              value={risk.swapPerLotPerDay}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ swapPerLotPerDay: parseFloat(e.target.value) || 0 })}
              tooltip="Financiamiento overnight por lote y por día (0 = sin swap)."
              tooltipTitle="Swap Overnight"
            />
          </div>
        </div>

      </div>
    </div>
  );
};
