import React from 'react';
import { 
  Lightbulb, 
  TrendingUp, 
  TrendingDown, 
  ShieldAlert, 
  Zap, 
  BarChart3,
  Target,
  ArrowRightLeft,
  Clock,
  AlertTriangle
} from 'lucide-react';
import type { Strategy } from '../../types/strategy';
import type { JobConfig } from '../../types/job';

interface StrategyExplainerCardProps {
  strategy: Strategy;
  config?: JobConfig;
}

/** Parse the strategy_tree expression to extract used indicator names and constants */
function extractUsedIndicators(tree: string): { indicators: string[]; constants: { name: string; value: number }[] } {
  if (!tree) return { indicators: [], constants: [] };

  const indicators: string[] = [];
  const constants: { name: string; value: number }[] = [];

  // Match indicator terminals: anything that is NOT a function name, NOT a constant, NOT a number
  const tokens = tree.match(/[A-Za-z0-9_%]+/g) || [];
  const functions = new Set(['add', 'sub', 'mul', 'div', 'safe_add', 'safe_sub', 'safe_mul', 'safe_div',
    'gt', 'lt', 'gte', 'lte', 'eq', 'neq', 'and_op', 'or_op', 'not_op', 'neg', 'abs_val',
    'max_val', 'min_val', 'if_then_else', 'clamp', 'sign', 'sqrt_safe', 'log_safe', 'exp_safe',
    'pow_safe', 'sin_val', 'cos_val', 'tan_val', 'atan_val', 'atan2_val', 'clip',
    'lag_1', 'lag_2', 'lag_3', 'lag_5', 'delta_1', 'delta_3', 'sma_3', 'sma_5', 'roc_3', 'roc_5',
    'zscore_10', 'zscore_20', 'rank_pct', 'cross_above', 'cross_below']);

  for (const tok of tokens) {
    if (functions.has(tok)) continue;
    if (tok.startsWith('c_')) {
      const val = parseFloat(tok.replace('c_', '').replace('neg_', '-'));
      if (!isNaN(val)) constants.push({ name: tok, value: val });
    } else if (/^-?\d+(\.\d+)?$/.test(tok)) {
      constants.push({ name: tok, value: parseFloat(tok) });
    } else {
      // This is an indicator terminal
      indicators.push(tok);
    }
  }

  return { indicators: [...new Set(indicators)], constants };
}

/** Map raw indicator terminal names to human-readable display names */
function humanIndicatorName(raw: string): string {
  const map: Record<string, string> = {
    'RSI': 'RSI (Relative Strength Index)',
    'EMA': 'EMA (Exponential Moving Average)',
    'SMA': 'SMA (Simple Moving Average)',
    'WMA': 'WMA (Weighted Moving Average)',
    'HMA': 'HMA (Hull Moving Average)',
    'Williams_pctR': 'Williams %R',
    'MACD': 'MACD',
    'MACD_signal': 'MACD Signal Line',
    'MACD_hist': 'MACD Histogram',
    'ATR': 'ATR (Average True Range)',
    'ADX': 'ADX (Average Directional Index)',
    'Bollinger_upper': 'Bollinger Banda Superior',
    'Bollinger_lower': 'Bollinger Banda Inferior',
    'Bollinger_mid': 'Bollinger Banda Media',
    'Stochastic_K': 'Stochastic %K',
    'Stochastic_D': 'Stochastic %D',
    'OBV': 'OBV (On-Balance Volume)',
    'MFI': 'MFI (Money Flow Index)',
    'CCI': 'CCI (Commodity Channel Index)',
    'VWAP': 'VWAP',
    'PVO': 'PVO (Percentage Volume Oscillator)',
    'Aroon_up': 'Aroon Up',
    'Aroon_down': 'Aroon Down',
    'Ichimoku_conv': 'Ichimoku Tenkan-Sen',
    'Ichimoku_base': 'Ichimoku Kijun-Sen',
    'Vortex_pos': 'Vortex Positivo',
    'Vortex_neg': 'Vortex Negativo',
    'TRIX': 'TRIX',
    'ROC': 'ROC (Rate of Change)',
    'AO': 'Awesome Oscillator',
    'Force_Index': 'Force Index',
    'Ease_of_Movement': 'Ease of Movement',
    'Donchian_upper': 'Donchian Superior',
    'Donchian_lower': 'Donchian Inferior',
  };
  return map[raw] || raw.replace(/_/g, ' ');
}

/** Describe the indicator's default config */
function indicatorDefaultConfig(raw: string): string {
  const configs: Record<string, string> = {
    'RSI': 'Período: 14',
    'EMA': 'Período: 14',
    'SMA': 'Período: 14',
    'WMA': 'Período: 14',
    'HMA': 'Período: 14',
    'Williams_pctR': 'Período: 14, Rango: [-100, 0]',
    'MACD': 'Fast: 12, Slow: 26, Signal: 9',
    'MACD_signal': 'Fast: 12, Slow: 26, Signal: 9',
    'MACD_hist': 'Fast: 12, Slow: 26, Signal: 9',
    'ATR': 'Período: 14',
    'ADX': 'Período: 14',
    'Bollinger_upper': 'Período: 20, Desv: 2.0',
    'Bollinger_lower': 'Período: 20, Desv: 2.0',
    'Bollinger_mid': 'Período: 20',
    'Stochastic_K': 'Período: 14, Smooth: 3',
    'Stochastic_D': 'Período: 14, Smooth: 3',
    'OBV': 'Acumulativo',
    'MFI': 'Período: 14',
    'CCI': 'Período: 20',
    'VWAP': 'Sesión completa',
    'PVO': 'Fast: 12, Slow: 26, Signal: 9',
    'Aroon_up': 'Período: 25',
    'Aroon_down': 'Período: 25',
    'Ichimoku_conv': 'Tenkan: 9',
    'Ichimoku_base': 'Kijun: 26',
    'Vortex_pos': 'Período: 14',
    'Vortex_neg': 'Período: 14',
    'TRIX': 'Período: 15',
    'ROC': 'Período: 12',
    'AO': 'Fast: 5, Slow: 34',
    'Force_Index': 'Período: 13',
    'Ease_of_Movement': 'Período: 14',
    'Donchian_upper': 'Período: 20',
    'Donchian_lower': 'Período: 20',
  };
  return configs[raw] || 'Por defecto';
}

/** Build a human-readable expression explanation */
function explainExpression(tree: string, direction: string): { conditionText: string; formulaExplain: string } {
  if (!tree) return { conditionText: '', formulaExplain: '' };

  const { indicators, constants } = extractUsedIndicators(tree);
  
  // Build the formula explanation
  const indNames = indicators.map(i => humanIndicatorName(i));
  const constNames = constants.map(c => c.value);
  
  let formulaExplain = '';
  
  // Try to parse common patterns
  if (tree.startsWith('add(') && indicators.length === 1 && constants.length === 1) {
    const ind = humanIndicatorName(indicators[0]);
    const c = constants[0].value;
    formulaExplain = `Se calcula: ${c} + ${ind}. `;
    if (indicators[0] === 'Williams_pctR') {
      formulaExplain += `Williams %R oscila entre -100 y 0. Al sumar ${c}, el resultado es positivo cuando Williams %R está por encima de ${-c} (zona de sobrecompra / momentum alcista), y negativo cuando está por debajo de ${-c} (sin momentum).`;
    }
  } else if (tree.startsWith('gt(') || tree.startsWith('lt(')) {
    formulaExplain = `Se comparan los valores de ${indNames.join(' y ')} para determinar la dirección del momentum.`;
  } else if (tree.startsWith('sub(')) {
    formulaExplain = `Se calcula la diferencia entre ${indNames.join(' y ')}. Un resultado positivo indica momentum alcista.`;
  } else {
    formulaExplain = `La fórmula combina ${indNames.join(', ')}${constNames.length > 0 ? ` con constante(s) ${constNames.join(', ')}` : ''} para generar un valor numérico de señal.`;
  }

  let conditionText = '';
  if (direction === 'long') {
    conditionText = `Se abre una posición LONG (compra) cuando el resultado de la fórmula es positivo (> 0). Se cierra la posición cuando el resultado se vuelve negativo o igual a cero (≤ 0), o cuando se activa el Stop Loss o Take Profit.`;
  } else if (direction === 'short') {
    conditionText = `Se abre una posición SHORT (venta) cuando el resultado de la fórmula es negativo (< 0). Se cierra la posición cuando el resultado se vuelve positivo o igual a cero (≥ 0), o cuando se activa el Stop Loss o Take Profit.`;
  } else {
    conditionText = `Se abre LONG cuando la fórmula es positiva (> 0) y SHORT cuando es negativa (< 0). Las posiciones se cierran por señal contraria, Stop Loss o Take Profit.`;
  }

  return { conditionText, formulaExplain };
}

export const StrategyExplainerCard: React.FC<StrategyExplainerCardProps> = ({ strategy, config }) => {
  const tree = strategy.strategy_tree || '';
  const risk = (config as any)?.risk || (strategy as any)?.exit_rules?.risk_config || {};
  const isRL = Boolean((strategy as any).is_rl_strategy || (strategy as any).is_rl || strategy.strategy_tree?.includes('RL_Neural_Policy') || strategy.strategy_tree?.includes('RL_Agent'));

  const direction = risk.direction || 'both';
  const { indicators: usedIndicators } = extractUsedIndicators(tree);
  const { conditionText, formulaExplain } = explainExpression(tree, direction);

  const directionLabel: Record<string, { text: string; color: string; icon: React.ReactNode }> = {
    long: { text: 'Solo LONG (Compras)', color: 'var(--color-accent-emerald)', icon: <TrendingUp size={14} /> },
    short: { text: 'Solo SHORT (Ventas)', color: 'var(--color-accent-rose)', icon: <TrendingDown size={14} /> },
    both: { text: 'LONG & SHORT (Ambas direcciones)', color: 'var(--color-accent-cyan)', icon: <ArrowRightLeft size={14} /> },
  };
  const dirInfo = directionLabel[direction] || directionLabel.both;

  const orderTypeLabel: Record<string, string> = {
    market: 'Ejecución a Mercado (inmediata al cierre de vela)',
    stop: `Orden Pendiente Stop (${risk.pendingOffsetPips || 5} pips del extremo)`,
    limit: `Orden Pendiente Limit (${risk.pendingOffsetPips || 5} pips de retroceso)`,
  };

  const slLabel = risk.slType === 'atr' 
    ? `${risk.slAtrMult || 1.5}× ATR (dinámico según volatilidad)` 
    : risk.slType === 'pips' 
      ? `${risk.slPips || 50} pips (fijo)` 
      : 'Sin Stop Loss (solo por señal)';

  const tpLabel = risk.tpType === 'atr' 
    ? `${risk.tpAtrMult || 3.0}× ATR (dinámico según volatilidad)` 
    : risk.tpType === 'pips' 
      ? `${risk.tpPips || 100} pips (fijo)` 
      : 'Sin Take Profit (solo por señal)';

  const rrRatio = risk.slType !== 'none' && risk.tpType !== 'none'
    ? (risk.slType === 'atr' && risk.tpType === 'atr')
      ? ((risk.tpAtrMult || 3.0) / (risk.slAtrMult || 1.5)).toFixed(1)
      : (risk.slType === 'pips' && risk.tpType === 'pips')
        ? ((risk.tpPips || 100) / (risk.slPips || 50)).toFixed(1)
        : null
    : null;

  // Card styles
  const cardStyle: React.CSSProperties = {
    background: 'rgba(255, 255, 255, 0.02)',
    padding: '1rem',
    borderRadius: '8px',
    border: '1px solid rgba(255, 255, 255, 0.05)',
  };
  const headerStyle = (color: string): React.CSSProperties => ({
    display: 'flex', alignItems: 'center', gap: '0.375rem',
    marginBottom: '0.625rem', color, fontWeight: 600, fontSize: '0.8125rem',
    paddingBottom: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.04)',
  });
  const bodyText: React.CSSProperties = {
    fontSize: '0.8125rem', color: 'var(--color-text-main)', lineHeight: '1.55', margin: 0,
  };
  const mutedText: React.CSSProperties = {
    fontSize: '0.75rem', color: 'var(--color-text-muted)', lineHeight: '1.5',
  };
  const tagStyle = (bg: string, fg: string): React.CSSProperties => ({
    display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
    padding: '0.1875rem 0.5rem', borderRadius: '4px',
    background: bg, color: fg, fontSize: '0.75rem', fontWeight: 600,
  });

  if (isRL) {
    return (
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
          <Lightbulb size={20} color="var(--color-accent-amber)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            ¿Cómo funciona esta estrategia?
          </h3>
        </div>
        <p style={bodyText}>
          Estrategia neuronal de <strong>Deep Reinforcement Learning (PPO/A2C)</strong> entrenada en entorno estocástico continuo. La red neuronal evalúa vectores OHLCV de las últimas 20 velas para predecir la dirección del precio.
        </p>
      </div>
    );
  }

  return (
    <div style={{
      background: 'var(--color-bg-card)',
      border: '1px solid var(--color-border)',
      borderRadius: '8px',
      padding: '1.25rem',
      marginBottom: '1.5rem'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Lightbulb size={20} color="var(--color-accent-amber)" />
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
          ¿Cómo funciona esta estrategia?
        </h3>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>

        {/* Card 1: Indicadores Utilizados */}
        <div style={cardStyle}>
          <div style={headerStyle('var(--color-accent-cyan)')}>
            <BarChart3 size={16} />
            <span>Indicadores Utilizados</span>
          </div>
          {usedIndicators.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {usedIndicators.map((ind, idx) => (
                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.375rem 0.5rem', background: 'rgba(0, 212, 255, 0.04)', borderRadius: '6px', border: '1px solid rgba(0, 212, 255, 0.08)' }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
                    {humanIndicatorName(ind)}
                  </span>
                  <span style={{ ...mutedText, fontFamily: 'monospace', fontSize: '0.6875rem' }}>
                    {indicatorDefaultConfig(ind)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={mutedText}>Sin indicadores técnicos detectados en la fórmula.</p>
          )}
        </div>

        {/* Card 2: Condición de Entrada */}
        <div style={cardStyle}>
          <div style={headerStyle('var(--color-accent-emerald)')}>
            <Target size={16} />
            <span>Condición de Entrada</span>
          </div>

          {/* Formula */}
          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ ...mutedText, marginBottom: '0.25rem', fontWeight: 500 }}>Fórmula Genética:</div>
            <code style={{
              display: 'block', padding: '0.5rem 0.75rem', borderRadius: '6px',
              background: 'rgba(0, 0, 0, 0.3)', border: '1px solid rgba(255,255,255,0.06)',
              color: 'var(--color-accent-amber)', fontSize: '0.8125rem', fontFamily: 'monospace',
              wordBreak: 'break-all',
            }}>
              {tree}
            </code>
          </div>

          {/* Explain */}
          <p style={{ ...bodyText, fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.625rem' }}>
            {formulaExplain}
          </p>

          {/* Condition */}
          <p style={{ ...bodyText, fontSize: '0.75rem' }}>
            {conditionText}
          </p>
        </div>

        {/* Card 3: Dirección & Tipo de Ejecución */}
        <div style={cardStyle}>
          <div style={headerStyle('var(--color-accent-amber)')}>
            <Zap size={16} />
            <span>Dirección & Ejecución</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            {/* Direction */}
            <div>
              <div style={{ ...mutedText, marginBottom: '0.25rem', fontWeight: 500 }}>Dirección de Trading:</div>
              <span style={tagStyle(
                direction === 'long' ? 'rgba(16, 185, 129, 0.12)' : direction === 'short' ? 'rgba(244, 63, 94, 0.12)' : 'rgba(0, 212, 255, 0.12)',
                dirInfo.color
              )}>
                {dirInfo.icon} {dirInfo.text}
              </span>
            </div>

            {/* Order Type */}
            <div>
              <div style={{ ...mutedText, marginBottom: '0.25rem', fontWeight: 500 }}>Tipo de Entrada:</div>
              <span style={{ ...bodyText, fontSize: '0.8125rem' }}>
                {orderTypeLabel[risk.orderType || 'market'] || 'Ejecución a Mercado'}
              </span>
            </div>

            {/* Pending timeout */}
            {(risk.orderType === 'stop' || risk.orderType === 'limit') && (
              <div style={mutedText}>
                ⏱ Timeout: Cancela la orden pendiente si no se activa en <strong>{risk.pendingTimeoutBars || 3} velas</strong>
              </div>
            )}

            {/* Max holding */}
            {risk.maxHoldingBars > 0 && (
              <div style={{ ...mutedText, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Clock size={12} />
                <span>Límite temporal: Cierre forzoso a las <strong>{risk.maxHoldingBars} velas</strong></span>
              </div>
            )}
          </div>
        </div>

        {/* Card 4: Niveles de SL & TP */}
        <div style={cardStyle}>
          <div style={headerStyle('var(--color-accent-rose)')}>
            <ShieldAlert size={16} />
            <span>Stop Loss & Take Profit</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            {/* SL */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <div style={{
                ...tagStyle('rgba(244, 63, 94, 0.12)', 'var(--color-accent-rose)'),
                flexShrink: 0, minWidth: '28px', justifyContent: 'center',
              }}>SL</div>
              <span style={{ ...bodyText, fontSize: '0.8125rem' }}>{slLabel}</span>
            </div>

            {/* TP */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <div style={{
                ...tagStyle('rgba(16, 185, 129, 0.12)', 'var(--color-accent-emerald)'),
                flexShrink: 0, minWidth: '28px', justifyContent: 'center',
              }}>TP</div>
              <span style={{ ...bodyText, fontSize: '0.8125rem' }}>{tpLabel}</span>
            </div>

            {/* Risk/Reward Ratio */}
            {rrRatio && (
              <div style={{
                marginTop: '0.25rem', padding: '0.375rem 0.625rem', borderRadius: '6px',
                background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.15)',
                display: 'flex', alignItems: 'center', gap: '0.375rem',
              }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-accent-amber)', fontWeight: 600 }}>
                  Risk/Reward Ratio: 1:{rrRatio}
                </span>
              </div>
            )}

            {/* Consecutive Loss Protection */}
            {risk.consecutiveLossAction && risk.consecutiveLossAction !== 'none' && (
              <div style={{
                marginTop: '0.25rem', padding: '0.5rem', borderRadius: '6px',
                background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.12)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-accent-amber)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                  <AlertTriangle size={12} />
                  <span>Protección de Racha Perdedora</span>
                </div>
                <p style={{ ...mutedText, margin: 0 }}>
                  {risk.consecutiveLossAction === 'reduce_risk'
                    ? `Reduce el riesgo al ${risk.consecutiveLossReductionPct || 50}% tras ${risk.consecutiveLossThreshold || 3} pérdidas consecutivas.`
                    : `Pausa el bot completamente tras ${risk.consecutiveLossThreshold || 3} pérdidas consecutivas.`}
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default StrategyExplainerCard;
