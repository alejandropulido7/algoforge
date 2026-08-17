import React from 'react';
import { 
  Lightbulb, 
  TrendingUp, 
  TrendingDown, 
  ShieldAlert, 
  Zap, 
  CheckCircle2, 
  Flame,
  AlertTriangle
} from 'lucide-react';
import type { Strategy } from '../../types/strategy';
import type { JobConfig } from '../../types/job';

interface StrategyExplainerCardProps {
  strategy: Strategy;
  config?: JobConfig;
}

export const StrategyExplainerCard: React.FC<StrategyExplainerCardProps> = ({ strategy, config }) => {
  const tree = strategy.strategy_tree || '';
  const risk = (config as any)?.risk || {};
  const isRL = Boolean((strategy as any).is_rl_strategy || (strategy as any).is_rl || strategy.strategy_tree?.includes('RL_Neural_Policy') || strategy.strategy_tree?.includes('RL_Agent'));

  // Interpret Human Friendly Logic
  const explainTreeCondition = (expr: string): { summary: string; buyRule: string; sellRule: string } => {
    if (!expr || expr === '') {
      return {
        summary: 'Estrategia cuantitativa optimizada mediante reglas combinatorias de Price Action y momentum.',
        buyRule: 'Se activa al confirmarse la señal de compra del árbol evolutivo sobre la vela cerrada.',
        sellRule: 'Se activa al confirmarse la señal de venta del árbol evolutivo sobre la vela cerrada.'
      };
    }

    if (isRL) {
      return {
        summary: 'Estrategia neuronal de Deep Reinforcement Learning (PPO/A2C) entrenada en entorno estocástico continuo.',
        buyRule: 'La red neuronal clasifica el vector de 20 velas OHLCV recientes y emite una predicción con probabilidad > 50% de impulso alcista.',
        sellRule: 'La red neuronal clasifica el vector de 20 velas OHLCV recientes y emite una predicción con probabilidad > 50% de impulso bajista.'
      };
    }

    // AST / Expression string matching
    let summaryText = 'Estrategia algorítmica evolucionada mediante algoritmos genéticos simbólicos.';
    let buyText = `La señal se activa en compra cuando la expresión lógica [ ${expr} ] evalúa a un valor positivo (> 0).`;
    let sellText = `La señal se activa en venta cuando la expresión lógica [ ${expr} ] evalúa a un valor negativo (< 0).`;

    if (expr.includes('RSI') && expr.includes('gt')) {
      summaryText = 'Estrategia basada en Momentum e impulso relativo del RSI con confirmación direccional.';
      buyText = 'Se busca compra cuando el indicador RSI supera el nivel de equilibrio o filtro de tendencia alcista.';
      sellText = 'Se busca venta cuando el indicador RSI cae por debajo del nivel de equilibrio confirmando presión bajista.';
    } else if (expr.includes('EMA') || expr.includes('SMA')) {
      summaryText = 'Estrategia de Seguimiento de Tendencia y Cruce de Medias Móviles con filtro de volatilidad.';
      buyText = 'Se busca compra cuando el precio o media rápida se posiciona por encima de la media de tendencia.';
      sellText = 'Se busca venta cuando el precio o media rápida se posiciona por debajo de la media de tendencia.';
    } else if (expr.includes('BBands') || expr.includes('Bollinger')) {
      summaryText = 'Estrategia de Ruptura de Volatilidad y Bandas de Bollinger.';
      buyText = 'Entrada en compra al expandirse la banda superior o rechazar la banda media con impulso alcista.';
      sellText = 'Entrada en venta al expandirse la banda inferior o rechazar la banda media con impulso bajista.';
    } else if (expr.includes('ATR') || expr.includes('ADX')) {
      summaryText = 'Estrategia de Régimen de Volatilidad y Expansión de Rango.';
      buyText = 'Entrada en compra cuando el rango verdadero (ATR/ADX) confirma suficiente fuerza direccional alcista.';
      sellText = 'Entrada en venta cuando el rango verdadero confirma fuerza direccional bajista.';
    }

    return { summary: summaryText, buyRule: buyText, sellRule: sellText };
  };

  const explanation = explainTreeCondition(tree);
  const approach = risk.strategyApproach || 'all';

  const approachTitles: Record<string, string> = {
    all: 'Exploración Libre & Multi-Patrón (Auto Discovery)',
    break_retest: 'Break & Retest (Ruptura + Confirmación en Retroceso)',
    fakeout: 'Fakeout (Trampa de Liquidez y Reversión Rápida)',
    breakout: 'Breakout Directo (Impulso y Ruptura de Consolidación)',
    reversion: 'Reversión de Estructura (Agotamiento y Cambio de Tendencia)',
    pullback: 'Pullback Dinámico (Retroceso en Tendencia Activa)'
  };

  return (
    <div style={{
      background: 'var(--color-bg-card)',
      border: '1px solid var(--color-border)',
      borderRadius: '8px',
      padding: '1.25rem',
      marginBottom: '1.5rem'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
        <Lightbulb size={20} color="var(--color-accent-amber)" />
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
          ¿Cómo funciona esta estrategia? (Explicación de Lógica & Reglas)
        </h3>
      </div>

      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-main)', lineHeight: '1.5', marginBottom: '1rem' }}>
        {explanation.summary}
      </p>

      {/* Grid of 4 clear functional cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        
        {/* Card 1: Enfoque y Concepto Clave */}
        <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem', color: 'var(--color-accent-cyan)', fontWeight: 600, fontSize: '0.8125rem' }}>
            <Flame size={16} />
            <span>Enfoque de Mercado</span>
          </div>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text-main)', marginBottom: '0.25rem' }}>
            {approachTitles[approach] || 'Estrategia Cuantitativa'}
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', margin: 0, lineHeight: '1.4' }}>
            Diseñada para operar en activos con liquidez consistente, priorizando el filtrado de ruido en temporalidades cerradas.
          </p>
        </div>

        {/* Card 2: Reglas de Entrada (Long / Short) */}
        <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem', color: 'var(--color-accent-emerald)', fontWeight: 600, fontSize: '0.8125rem' }}>
            <CheckCircle2 size={16} />
            <span>Gatillos de Entrada</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.375rem' }}>
              <TrendingUp size={14} color="var(--color-accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span><strong style={{ color: 'var(--color-accent-emerald)' }}>Compra:</strong> {explanation.buyRule}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.375rem' }}>
              <TrendingDown size={14} color="var(--color-accent-rose)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span><strong style={{ color: 'var(--color-accent-rose)' }}>Venta:</strong> {explanation.sellRule}</span>
            </div>
          </div>
        </div>

        {/* Card 3: Modalidad de Ejecución & Órdenes */}
        <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem', color: 'var(--color-accent-amber)', fontWeight: 600, fontSize: '0.8125rem' }}>
            <Zap size={16} />
            <span>Ejecución & Tipo de Orden</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', margin: 0, lineHeight: '1.4' }}>
            {risk.orderType === 'stop' ? (
              <>Coloca una orden <b>Buy Stop / Sell Stop</b> a <b>{risk.pendingOffsetPips || 5} pips</b> del extremo de la vela. Si no se activa en <b>{risk.pendingTimeoutBars || 3} velas</b>, se cancela automáticamente.</>
            ) : risk.orderType === 'limit' ? (
              <>Coloca una orden <b>Buy Limit / Sell Limit</b> a <b>{risk.pendingOffsetPips || 5} pips</b> para buscar un mejor precio de retroceso. Expira tras <b>{risk.pendingTimeoutBars || 3} velas</b>.</>
            ) : (
              <>Ejecución inmediata <b>a mercado (On Market)</b> tras el cierre de la vela que valida la condición técnica.</>
            )}
          </p>
        </div>

        {/* Card 4: Gestión de Salida & Pérdidas Consecutivas */}
        <div style={{ background: 'rgba(255, 255, 255, 0.015)', padding: '1rem', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.5rem', color: 'var(--color-accent-rose)', fontWeight: 600, fontSize: '0.8125rem' }}>
            <ShieldAlert size={16} />
            <span>Gestión de Salida & Riesgo</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', lineHeight: '1.4' }}>
            <div>• <b>Stop Loss:</b> {risk.slType === 'atr' ? `${risk.slAtrMult || 1.5}x ATR` : (risk.slType === 'pips' ? `${risk.slPips || 50} pips` : 'Por señal')} | <b>Take Profit:</b> {risk.tpType === 'atr' ? `${risk.tpAtrMult || 3.0}x ATR` : (risk.tpType === 'pips' ? `${risk.tpPips || 100} pips` : 'Por señal')}</div>
            <div>• <b>Límite Temporal:</b> {risk.maxHoldingBars ? `Cierre forzoso a las ${risk.maxHoldingBars} velas` : 'Sin límite por velas (cierre por SL/TP)'}</div>
            {risk.consecutiveLossAction && risk.consecutiveLossAction !== 'none' && (
              <div style={{ color: 'var(--color-accent-amber)', marginTop: '0.375rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <AlertTriangle size={12} />
                  <span><b>Protección de Racha:</b> {risk.consecutiveLossAction === 'reduce_risk' ? `Reduce riesgo al ${risk.consecutiveLossReductionPct || 50}% tras ${risk.consecutiveLossThreshold || 3} pérdidas.` : `Pausa el bot tras ${risk.consecutiveLossThreshold || 3} pérdidas seguidas.`}</span>
                </div>
                {risk.consecutiveLossAction === 'stop_bot' && (
                  <div style={{ color: 'var(--color-accent-cyan)', fontSize: '0.6875rem', paddingLeft: '1rem' }}>
                    ↪ <b>Reactivación:</b> {
                      risk.consecutiveLossReactivation === 'cooldown_bars' ? (risk.consecutiveLossAutoCooldown ? 'Auto-cooldown inteligente calibrado por la IA tras fase de enfriamiento' : `Reanuda automáticamente tras ${risk.consecutiveLossCooldownBars || 20} velas de enfriamiento`) :
                      risk.consecutiveLossReactivation === 'next_session' ? 'Reanuda automáticamente al inicio de la siguiente sesión de trading' :
                      risk.consecutiveLossReactivation === 'next_day' ? 'Reanuda automáticamente al inicio del siguiente día (00:00)' :
                      risk.consecutiveLossReactivation === 'days_count' ? `Reanuda automáticamente tras ${risk.consecutiveLossCooldownDays || 1} días de espera` :
                      risk.consecutiveLossReactivation === 'next_week' ? 'Reanuda automáticamente el lunes de la siguiente semana' : 'Requiere reinicio manual del Asesor Experto'
                    }
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default StrategyExplainerCard;
