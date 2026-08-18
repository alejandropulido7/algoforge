import React from 'react';
import { useJobStore } from '../../store/jobStore';
import Input from '../common/Input';
import type { StrategyApproach } from '../../types/job';
import { 
  Scale, 
  Target, 
  Percent, 
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
  Flame,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import styles from '../../styles/pages.module.css';

interface StrategyApproachCard {
  key: StrategyApproach;
  title: string;
  badge: string;
  badgeColor: string;
  structure: string;
  entry: string;
  context: string;
  example: string;
}

const STRATEGY_APPROACHES: StrategyApproachCard[] = [
  {
    key: 'all',
    title: 'Cualquiera (Automático / Híbrido)',
    badge: 'Auto Discovery',
    badgeColor: 'var(--color-accent-cyan)',
    structure: 'Exploración combinatoria libre',
    entry: 'Optimización genética de señales de indicadores y precio',
    context: 'Cualquier régimen de mercado',
    example: 'El algoritmo evalúa y genera las mejores combinaciones sin restringir el patrón de entrada.'
  },
  {
    key: 'break_retest',
    title: 'Break & Retest',
    badge: 'Continuación',
    badgeColor: 'var(--color-accent-emerald)',
    structure: 'Ruptura + retest a zona rota',
    entry: 'Rechazo o patrón confirmatorio (mecha / engulfing)',
    context: 'Tendencia fuerte con volumen expansivo',
    example: '1. Rompe con vela fuerte y volumen creciente.\n2. Retrocede a la zona rota (pullback).\n3. Se forma rechazo (mecha o patrón engulfing).\n4. Entra en la dirección de la ruptura original.'
  },
  {
    key: 'fakeout',
    title: 'Fakeout (Falsa Ruptura)',
    badge: 'Reversión / Trampa',
    badgeColor: 'var(--color-accent-rose)',
    structure: 'Rompe y vuelve a la estructura previa',
    entry: 'Reingreso confirmado dentro del rango',
    context: 'Zonas de liquidez, extremos de sesión, barridos',
    example: '1. Rompimiento falso por mecha o cierre sin confirmación.\n2. Volumen alto en la mecha (absorción).\n3. Estructura previa intacta.\n4. Entrada cuando el precio regresa dentro del rango.'
  },
  {
    key: 'breakout',
    title: 'Breakout Directo',
    badge: 'Impulso / Momentum',
    badgeColor: 'var(--color-accent-amber)',
    structure: 'Ruptura directa de consolidación',
    entry: 'Entrada inmediata con momentum sin esperar retest',
    context: 'Apertura de sesión NY/Londres o alta volatilidad',
    example: '1. Vela amplia, cuerpo dominante, volumen alto.\n2. Nivel de consolidación roto claramente.\n3. Entrada directa por momentum (órdenes Stop o Market).'
  },
  {
    key: 'reversion',
    title: 'Reversión de Tendencia',
    badge: 'Cambio de Estructura',
    badgeColor: 'var(--color-accent-rose)',
    structure: 'Doble techo/suelo, fallo de nuevo extremo (MSS)',
    entry: 'Pullback al nuevo nivel de quiebre de estructura',
    context: 'Tendencia extendida (3+ impulsos) y agotamiento',
    example: '1. Tendencia extendida previa con divergencia.\n2. Quiebre de estructura menor (MSS en temporalidad de entrada).\n3. Entrada en pullback al nuevo punto de ruptura.'
  },
  {
    key: 'pullback',
    title: 'Pullback en Tendencia',
    badge: 'Continuación Dinámica',
    badgeColor: 'var(--color-accent-cyan)',
    structure: 'Corrección temporal dentro de tendencia activa',
    entry: 'Rechazo en zona dinámica (EMA, FVG, 50% Fibo)',
    context: 'Tendencia clara (HH-HL / LH-LL) en sesiones activas',
    example: '1. Tendencia alcista marcada.\n2. Precio corrige hasta EMA o zona de liquidez con vela de mecha larga.\n3. Vela de confirmación alcista (engulfing/pin bar).\n4. Entrada al cierre con SL debajo del retroceso.'
  }
];

export const StepRiskManagement: React.FC = () => {
  const { config, updateRisk } = useJobStore();
  const risk = config.risk || {
    initialDeposit: 10000,
    sizingMode: 'lots',
    lotSize: 0.1,
    riskPct: 1.0,
    direction: 'both',
    strategyApproach: 'all',
    orderType: 'market',
    pendingTimeoutBars: 3,
    pendingOffsetPips: 5.0,
    maxHoldingBars: 0,
    consecutiveLossAction: 'none',
    consecutiveLossThreshold: 3,
    consecutiveLossReductionPct: 50,
    slType: 'pips',
    slPips: 50.0,
    slAtrMult: 1.5,
    tpType: 'pips',
    tpPips: 100.0,
    tpAtrMult: 3.0,
    contractSize: 100000,
    pointSize: 0.0001,
    spreadPips: 1.0,
    commissionPerLot: 7.0,
    commissionPerSide: true,
    swapPerLotPerDay: 0.0,
  };

  const currentDir = risk.direction || 'both';
  const currentOrderType = risk.orderType || 'market';
  const currentApproach = risk.strategyApproach || 'all';
  const currentLossAction = risk.consecutiveLossAction || 'none';

  return (
    <div className={styles.stepContainer}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={22} color="var(--color-accent-cyan)" />
          Strategy config, Enfoque & Gestión de Riesgo
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Selecciona el enfoque de Price Action deseado (Break & Retest, Fakeout, Breakout, Reversión, Pullback), la dirección, el tipo de orden y los mecanismos de protección contra rachas perdedoras.
        </p>
      </div>

      {/* 1. Strategy Approach Selector Cards */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <Flame size={18} color="var(--color-accent-amber)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            Enfoque de Estrategia (Price Action & Estructura)
          </h3>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Define la lógica estructural dominante que el motor de IA priorizará al generar y filtrar las estrategias.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '0.875rem' }}>
          {STRATEGY_APPROACHES.map(app => {
            const isSelected = currentApproach === app.key;
            return (
              <div
                key={app.key}
                onClick={() => updateRisk({ strategyApproach: app.key })}
                style={{
                  padding: '1rem',
                  borderRadius: '6px',
                  border: isSelected ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                  background: isSelected ? 'rgba(0, 212, 255, 0.06)' : 'rgba(255, 255, 255, 0.015)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  boxShadow: isSelected ? '0 0 12px rgba(0, 212, 255, 0.1)' : 'none'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: isSelected ? 'var(--color-accent-cyan)' : 'var(--color-text-main)' }}>
                    {app.title}
                  </span>
                  <span style={{
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    padding: '0.125rem 0.375rem',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: app.badgeColor,
                    border: `1px solid ${app.badgeColor}33`
                  }}>
                    {app.badge}
                  </span>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                  <div><strong style={{ color: 'var(--color-text-main)' }}>Estructura:</strong> {app.structure}</div>
                  <div><strong style={{ color: 'var(--color-text-main)' }}>Entrada:</strong> {app.entry}</div>
                  <div><strong style={{ color: 'var(--color-text-main)' }}>Contexto:</strong> {app.context}</div>
                </div>

                <div style={{
                  marginTop: '0.25rem',
                  padding: '0.5rem',
                  background: 'rgba(0, 0, 0, 0.25)',
                  borderRadius: '4px',
                  fontSize: '0.6875rem',
                  color: 'var(--color-text-muted)',
                  whiteSpace: 'pre-line',
                  lineHeight: '1.3'
                }}>
                  {app.example}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Direction and Order Execution Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
        
        {/* Trade Direction Selector */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <ArrowLeftRight size={18} color="var(--color-accent-cyan)" />
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              Allowed Trade Direction
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Choose whether strategies seek buy setups, sell short setups, or both directions.
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
              Order Execution Mode
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            Execution mechanism tested in backtests and exported to MT5.
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
                On Market
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

      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: '0 0 0.5rem 0' }}>
          Simultaneous Trades
        </h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Establece cuántas operaciones simultáneas puede abrir el bot al mismo tiempo si la condición de entrada se sigue cumpliendo. (1 = Operación única por estrategia)
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
              Max Operaciones Simultáneas
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={risk.maxSimultaneousTrades || 1}
              onChange={(e) => updateRisk({ maxSimultaneousTrades: Number(e.target.value) })}
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
      </div>

      {/* 3. Consecutive Losses Protection (Kill Switch & Risk Reduction) */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <AlertTriangle size={18} color="var(--color-accent-rose)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            Protección de Pérdidas Consecutivas (Drawdown Kill-Switch)
          </h3>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Protege tu cuenta activando una reducción dinámica de lotaje o pausando las operaciones del bot tras acumular $X$ pérdidas seguidas.
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
                tooltip="Porcentaje al que se reduce el lotaje o riesgo (ej: 50% reduce el lote a la mitad durante la racha)."
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

      {/* 4. Timing & Candle Count Configuration */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <Clock size={18} color="var(--color-accent-cyan)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            Timing & Candle Rules (Candle Count Exits & Cancellations)
          </h3>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
          Configure maximum holding time in candles and expiration timeout for pending orders before automatic cancellation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {/* Rule 1: Pending Order Expiration */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem' }}>
              <Timer size={16} color="var(--color-accent-amber)" />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text-main)' }}>
                Pending Order Timeout (Velas para Omitir)
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
              Si se coloca un Buy Stop / Sell Stop y pasan <b>X velas</b> sin activarse, la orden se cancela automáticamente.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <Input
                id="risk-pending-timeout"
                label="Max Velas Pendiente"
                type="number"
                step="1"
                min="1"
                max="50"
                value={risk.pendingTimeoutBars || 3}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ pendingTimeoutBars: parseInt(e.target.value) || 3 })}
                tooltip="Cantidad de velas que la orden pendiente Buy Stop / Sell Stop permanecerá activa antes de ser descartada si el precio no la toca."
                tooltipTitle="Cancelación de Orden Pendiente"
              />
              <Input
                id="risk-pending-offset"
                label="Offset Distancia (Pips)"
                type="number"
                step="0.5"
                min="0.0"
                max="50.0"
                value={risk.pendingOffsetPips || 5.0}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ pendingOffsetPips: parseFloat(e.target.value) || 5.0 })}
                tooltip="Distancia en pips por encima del High (para Buy Stop) o por debajo del Low (para Sell Stop) al colocar la orden pendiente."
                tooltipTitle="Offset de Entrada Pendiente"
              />
            </div>
          </div>

          {/* Rule 2: Max Holding Period / Candle Time Exit */}
          <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem' }}>
              <Clock size={16} color="var(--color-accent-emerald)" />
              <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text-main)' }}>
                Time-Based Exit (Cierre tras X Velas)
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
              Cierra obligatoriamente la posición abierta si han transcurrido <b>X velas</b> desde la entrada sin tocar SL/TP.
            </p>
            <Input
              id="risk-max-holding-bars"
              label="Cerrar tras X Velas (0 = Desactivado)"
              type="number"
              step="1"
              min="0"
              max="200"
              value={risk.maxHoldingBars || 0}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ maxHoldingBars: parseInt(e.target.value) || 0 })}
              tooltip="Límite máximo de duración del trade en velas. Si se coloca 0, la posición solo cerrará al tocar Stop Loss, Take Profit o señal contraria."
              tooltipTitle="Cierre por Tiempo / Velas"
            />
          </div>
        </div>
      </div>

      {/* 5. Position Sizing, SL, TP & Contract Spec Grid */}
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
              Positions will remain open until an opposite exit signal or candle timeout is reached.
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
              Positions will close upon reaching an opposite signal or max holding candles limit.
            </div>
          )}
        </div>

        {/* Section 4: Contract & Point Parameters */}
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
            Copia los valores desde la ventana <strong>Especificación de MT5</strong> para calcular el valor exacto del pip y lotaje:
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

          {/* MT5 Direct Mapping Info Box */}
          <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.25)', borderRadius: '6px', fontSize: '0.6875rem', color: 'var(--color-text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            <div>🔹 <strong>Contract Size:</strong> Copia directo el campo <code>Contract size</code> de la ficha MT5.</div>
            <div>🔹 <strong>Point / Pip Size:</strong> Se obtiene de los <code>Digits</code> de MT5: 2 dígitos = <code>0.01</code>, 3 dígitos = <code>0.001</code>, 5 dígitos = <code>0.00001</code>.</div>
          </div>
        </div>

        {/* Section 5: MT5 Realistic Costs (Spread, Commission, Swap) */}
        <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Scale size={18} color="var(--color-accent-rose)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
              MT5 Costs (Realismo del Backtest)
            </h3>
          </div>

          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            El simulador debe castigar los costos que MT5 cobra en cada operación, o el backtest infla el PnL (spread gratis + comisión de un solo lado + sin swap). Configura los valores de <strong>tu broker</strong>.
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
              tooltip="Spread medio del símbolo en pips. El simulador compra al Ask (Open + spread/2) y vende al Bid (Open - spread/2), como MT5."
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
              tooltip="Comisión por lote (por lado, si 'Por lado' está activo). Ej: $7/lote = $0.70 por 0.1 lote en cada deal."
              tooltipTitle="Comisión por Lote"
            />
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', color: 'var(--color-text-main)', fontWeight: 500, padding: '0.25rem 0' }}>
              <input
                type="checkbox"
                checked={risk.commissionPerSide ?? true}
                onChange={(e) => updateRisk({ commissionPerSide: e.target.checked })}
                style={{ accentColor: 'var(--color-accent-rose)', width: '16px', height: '16px' }}
              />
              <span><b>Comisión por lado</b> (entrada + salida, como MT5)</span>
            </label>
            <Input
              id="risk-swap-day"
              label="Swap ($/lote/día)"
              type="number"
              step="0.5"
              min="0"
              value={risk.swapPerLotPerDay}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateRisk({ swapPerLotPerDay: parseFloat(e.target.value) || 0 })}
              tooltip="Financiamiento overnight por lote y por día que la posición permanece abierta (0 = sin swap). Revisa la ficha MT5 del símbolo."
              tooltipTitle="Swap Overnight"
            />
          </div>

          <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.25)', borderRadius: '6px', fontSize: '0.6875rem', color: 'var(--color-text-secondary)' }}>
            💡 Con ~600-1000 operaciones, el spread + comisión doble + swap pueden costar miles de dólares. Configúralos <strong>antes</strong> de optimizar para que la IA descarte estrategias que solo viven del spread gratis.
          </div>
        </div>

      </div>
    </div>
  );
};
