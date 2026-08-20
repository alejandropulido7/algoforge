import React, { useState, useMemo } from 'react';
import { useJobStore } from '../../store/jobStore';
import { Info, X, Sparkles, Plus, Check } from 'lucide-react';
import { INDICATORS_CATALOG, getIndicatorCatalogItem, calculateTotalCombinations } from '../../data/indicatorsCatalog';
import type { ParamRangeDef } from '../../data/indicatorsCatalog';
import styles from '../../styles/pages.module.css';

export const ALL_INDICATORS = INDICATORS_CATALOG.map(i => ({
  id: i.id,
  name: i.name,
  category: i.category as any,
  desc: i.desc,
  detail: i.params.map(p => `${p.name}: [${p.defaultMin}-${p.defaultMax}]`).join(', ') || 'Serie Acumulativa'
}));

const StepIndicators: React.FC = () => {
  const { config, toggleIndicator, setIndicatorParamRange } = useJobStore();
  const [activeTooltip, setActiveTooltip] = useState<{
    indName: string;
    param: ParamRangeDef;
    x: number;
    y: number;
  } | null>(null);

  const selectedItems = useMemo(() => {
    return config.indicators
      .map(id => getIndicatorCatalogItem(id))
      .filter((item): item is NonNullable<typeof item> => Boolean(item));
  }, [config.indicators]);

  const totalCombinations = useMemo(() => {
    return calculateTotalCombinations(config.indicators, config.indicatorRanges);
  }, [config.indicators, config.indicatorRanges]);

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const handleAddIndicator = (id: string) => {
    if (!config.indicators.includes(id)) {
      toggleIndicator(id, true);
    }
  };

  const handleRemoveIndicator = (id: string) => {
    toggleIndicator(id, false);
  };

  const handleRangeChange = (
    indId: string,
    paramKey: string,
    field: 'min' | 'step' | 'max',
    value: number
  ) => {
    setIndicatorParamRange(indId, paramKey, { [field]: value });
  };

  return (
    <div className={styles.stepContainer} style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div className="mb-6">
        <h2 className={styles.stepTitle}>Selección de Indicadores y Espacio de Búsqueda</h2>
        <p className={styles.stepSubtitle}>
          Elige los indicadores para el motor genético y define los rangos (Desde, Pasos, Hasta) para descubrir combinaciones optimizadas.
        </p>
      </div>

      {/* TOP PILLS: "Agregar indicador" */}
      <div style={{
        background: 'var(--color-bg-secondary, #131829)',
        border: '1px solid var(--color-border, #1f293d)',
        borderRadius: '12px',
        padding: '1.25rem',
        marginBottom: '1.5rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '0.875rem'
        }}>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-secondary, #94a3b8)', letterSpacing: '0.025em' }}>
            Agregar indicador ({INDICATORS_CATALOG.length} disponibles)
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-accent-cyan, #00d4ff)' }}>
            {config.indicators.length} seleccionados
          </span>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.5rem',
          maxHeight: '180px',
          overflowY: 'auto',
          paddingRight: '0.25rem'
        }}>
          {INDICATORS_CATALOG.map(ind => {
            const isSelected = config.indicators.includes(ind.id);
            return (
              <button
                key={ind.id}
                type="button"
                onClick={() => {
                  if (isSelected) {
                    handleRemoveIndicator(ind.id);
                  } else {
                    handleAddIndicator(ind.id);
                  }
                }}
                title={ind.desc}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.375rem',
                  padding: '0.35rem 0.75rem',
                  borderRadius: '20px',
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  background: isSelected 
                    ? 'rgba(0, 212, 255, 0.15)' 
                    : 'rgba(255, 255, 255, 0.03)',
                  border: isSelected 
                    ? '1px solid var(--color-accent-cyan, #00d4ff)' 
                    : '1px solid var(--color-border, #1f293d)',
                  color: isSelected 
                    ? 'var(--color-accent-cyan, #00d4ff)' 
                    : 'var(--color-text-secondary, #94a3b8)',
                }}
              >
                {isSelected ? <Check size={12} strokeWidth={2.5} /> : <Plus size={12} />}
                <span>{ind.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* MAIN TABLE: SELECTED INDICATORS & PARAMETER RANGES */}
      <div style={{
        background: 'var(--color-bg-secondary, #131829)',
        border: '1px solid var(--color-border, #1f293d)',
        borderRadius: '12px',
        overflow: 'hidden',
        marginBottom: '1.5rem'
      }}>
        {selectedItems.length === 0 ? (
          <div style={{ padding: '3.5rem 2rem', textAlign: 'center' }}>
            <Sparkles size={40} style={{ color: 'var(--color-accent-cyan, #00d4ff)', margin: '0 auto 1rem', opacity: 0.7 }} />
            <h4 style={{ color: 'var(--color-text-primary, #e2e8f0)', fontWeight: 600, fontSize: '1.125rem', marginBottom: '0.5rem' }}>
              Ningún indicador seleccionado
            </h4>
            <p style={{ color: 'var(--color-text-secondary, #94a3b8)', fontSize: '0.875rem', maxWidth: '460px', margin: '0 auto' }}>
              Haz clic en cualquier píldora de arriba (por ejemplo <strong>+ RSI</strong>, <strong>+ Estocástico</strong>, <strong>+ Bollinger</strong>, <strong>+ MACD</strong>) para agregarlo y definir sus rangos de exploración.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{
                  borderBottom: '1px solid var(--color-border, #1f293d)',
                  background: 'rgba(0, 0, 0, 0.2)',
                  color: 'var(--color-text-secondary, #94a3b8)',
                  fontSize: '0.8125rem'
                }}>
                  <th style={{ padding: '0.875rem 1.25rem', width: '22%' }}>Indicador</th>
                  <th style={{ padding: '0.875rem 1.25rem', width: '30%' }}>Parámetro</th>
                  <th style={{ padding: '0.875rem 1.25rem', width: '16%', textAlign: 'center' }}>Desde</th>
                  <th style={{ padding: '0.875rem 1.25rem', width: '16%', textAlign: 'center' }}>Pasos</th>
                  <th style={{ padding: '0.875rem 1.25rem', width: '16%', textAlign: 'center' }}>Hasta</th>
                </tr>
              </thead>
              <tbody>
                {selectedItems.map((ind, indIdx) => {
                  const hasParams = ind.params.length > 0;
                  const indRanges = config.indicatorRanges?.[ind.id] || {};

                  if (!hasParams) {
                    return (
                      <tr 
                        key={ind.id} 
                        style={{
                          borderBottom: indIdx < selectedItems.length - 1 ? '1px solid var(--color-border, #1f293d)' : 'none',
                          background: indIdx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)'
                        }}
                      >
                        <td style={{ padding: '1rem 1.25rem' }}>
                          <button
                            type="button"
                            onClick={() => handleRemoveIndicator(ind.id)}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              background: 'transparent',
                              border: 'none',
                              color: 'var(--color-accent-cyan, #00d4ff)',
                              fontWeight: 600,
                              fontSize: '0.9375rem',
                              cursor: 'pointer',
                              padding: 0
                            }}
                          >
                            <X size={14} style={{ color: 'var(--color-text-secondary, #94a3b8)' }} />
                            <span>{ind.name}</span>
                          </button>
                        </td>
                        <td style={{ padding: '1rem 1.25rem', color: 'var(--color-text-muted, #64748b)', fontStyle: 'italic' }}>
                          Serie fija acumulativa (sin parámetros)
                        </td>
                        <td colSpan={3} style={{ padding: '1rem 1.25rem', textAlign: 'center', color: 'var(--color-text-muted, #64748b)' }}>
                          -
                        </td>
                      </tr>
                    );
                  }

                  return ind.params.map((param, pIdx) => {
                    const currentRange = indRanges[param.key] || {
                      min: param.defaultMin,
                      step: param.defaultStep,
                      max: param.defaultMax
                    };

                    const isFirstParamOfInd = pIdx === 0;
                    const isLastParamOfInd = pIdx === ind.params.length - 1;
                    const isLastIndicator = indIdx === selectedItems.length - 1;

                    return (
                      <tr 
                        key={`${ind.id}_${param.key}`}
                        style={{
                          borderBottom: (isLastParamOfInd && !isLastIndicator) ? '1px solid var(--color-border, #1f293d)' : 'none',
                          background: indIdx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.015)'
                        }}
                      >
                        {/* Indicador Column */}
                        <td style={{
                          padding: '0.875rem 1.25rem',
                          verticalAlign: 'middle'
                        }}>
                          {isFirstParamOfInd ? (
                            <button
                              type="button"
                              onClick={() => handleRemoveIndicator(ind.id)}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--color-accent-cyan, #00d4ff)',
                                fontWeight: 600,
                                fontSize: '0.9375rem',
                                cursor: 'pointer',
                                padding: 0
                              }}
                              title={`Eliminar ${ind.name}`}
                            >
                              <X size={14} style={{ color: 'var(--color-text-secondary, #94a3b8)' }} />
                              <span>{ind.name}</span>
                            </button>
                          ) : null}
                        </td>

                        {/* Parámetro Column with (i) Toast Trigger */}
                        <td style={{ padding: '0.875rem 1.25rem', verticalAlign: 'middle' }}>
                          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ color: 'var(--color-text-primary, #e2e8f0)', fontWeight: 500, fontSize: '0.875rem' }}>
                              {param.name}
                            </span>
                            <button
                              type="button"
                              onMouseEnter={(e) => {
                                const rect = e.currentTarget.getBoundingClientRect();
                                setActiveTooltip({
                                  indName: ind.name,
                                  param,
                                  x: rect.right + 12,
                                  y: rect.top - 20
                                });
                              }}
                              onMouseLeave={() => setActiveTooltip(null)}
                              onClick={(e) => {
                                const rect = e.currentTarget.getBoundingClientRect();
                                setActiveTooltip(prev => prev?.param.key === param.key ? null : {
                                  indName: ind.name,
                                  param,
                                  x: rect.right + 12,
                                  y: rect.top - 20
                                });
                              }}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: 'rgba(0, 212, 255, 0.08)',
                                border: '1px solid rgba(0, 212, 255, 0.25)',
                                color: 'var(--color-accent-cyan, #00d4ff)',
                                borderRadius: '50%',
                                width: '18px',
                                height: '18px',
                                cursor: 'help',
                                padding: 0
                              }}
                            >
                              <Info size={11} />
                            </button>
                          </div>
                        </td>

                        {/* Desde Column */}
                        <td style={{ padding: '0.875rem 1.25rem', textAlign: 'center' }}>
                          <input
                            type="number"
                            step={param.defaultStep}
                            value={currentRange.min}
                            onChange={(e) => handleRangeChange(ind.id, param.key, 'min', parseFloat(e.target.value) || 0)}
                            style={{
                              width: '90px',
                              padding: '0.45rem 0.65rem',
                              borderRadius: '8px',
                              border: '1px solid var(--color-border, #1f293d)',
                              background: 'var(--color-bg-primary, #0a0e1a)',
                              color: 'var(--color-text-primary, #e2e8f0)',
                              fontSize: '0.875rem',
                              textAlign: 'center',
                              outline: 'none'
                            }}
                          />
                        </td>

                        {/* Pasos Column */}
                        <td style={{ padding: '0.875rem 1.25rem', textAlign: 'center' }}>
                          <input
                            type="number"
                            step={param.defaultStep}
                            value={currentRange.step}
                            onChange={(e) => handleRangeChange(ind.id, param.key, 'step', parseFloat(e.target.value) || 1)}
                            style={{
                              width: '90px',
                              padding: '0.45rem 0.65rem',
                              borderRadius: '8px',
                              border: '1px solid var(--color-border, #1f293d)',
                              background: 'var(--color-bg-primary, #0a0e1a)',
                              color: 'var(--color-text-primary, #e2e8f0)',
                              fontSize: '0.875rem',
                              textAlign: 'center',
                              outline: 'none'
                            }}
                          />
                        </td>

                        {/* Hasta Column */}
                        <td style={{ padding: '0.875rem 1.25rem', textAlign: 'center' }}>
                          <input
                            type="number"
                            step={param.defaultStep}
                            value={currentRange.max}
                            onChange={(e) => handleRangeChange(ind.id, param.key, 'max', parseFloat(e.target.value) || 0)}
                            style={{
                              width: '90px',
                              padding: '0.45rem 0.65rem',
                              borderRadius: '8px',
                              border: '1px solid var(--color-border, #1f293d)',
                              background: 'var(--color-bg-primary, #0a0e1a)',
                              color: 'var(--color-text-primary, #e2e8f0)',
                              fontSize: '0.875rem',
                              textAlign: 'center',
                              outline: 'none'
                            }}
                          />
                        </td>
                      </tr>
                    );
                  });
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* BOTTOM SUMMARY: Combinaciones posibles con estos rangos */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1.125rem 1.5rem',
        background: 'var(--color-bg-secondary, #131829)',
        border: '1px solid var(--color-border, #1f293d)',
        borderRadius: '12px'
      }}>
        <div style={{ color: 'var(--color-text-secondary, #94a3b8)', fontSize: '0.9375rem', fontWeight: 500 }}>
          Combinaciones posibles con estos rangos:
        </div>
        <div style={{
          fontSize: '1.375rem',
          fontWeight: 700,
          color: 'var(--color-accent-emerald, #10b981)',
          letterSpacing: '0.025em',
          fontFamily: 'monospace'
        }}>
          {formatNumber(totalCombinations)}
        </div>
      </div>

      {/* FLOATING INFO TOAST / POPOVER */}
      {activeTooltip && (
        <div
          style={{
            position: 'fixed',
            left: Math.min(activeTooltip.x, window.innerWidth - 350),
            top: Math.max(15, Math.min(activeTooltip.y, window.innerHeight - 220)),
            width: '330px',
            background: '#0d1322',
            border: '1px solid var(--color-accent-cyan, #00d4ff)',
            borderRadius: '10px',
            padding: '0.875rem 1rem',
            boxShadow: '0 12px 28px -4px rgba(0, 0, 0, 0.8), 0 0 15px rgba(0, 212, 255, 0.15)',
            zIndex: 9999,
            pointerEvents: 'none',
            backdropFilter: 'blur(8px)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
            <span style={{ fontWeight: 700, color: 'var(--color-accent-cyan, #00d4ff)', fontSize: '0.875rem' }}>
              {activeTooltip.param.name}
            </span>
            <span style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              background: 'rgba(255, 255, 255, 0.08)',
              padding: '0.1rem 0.4rem',
              borderRadius: '4px',
              color: 'var(--color-text-secondary, #94a3b8)'
            }}>
              {activeTooltip.indName}
            </span>
          </div>

          <div style={{ fontSize: '0.75rem', color: 'var(--color-accent-amber, #f59e0b)', fontWeight: 500, marginBottom: '0.45rem' }}>
            {activeTooltip.param.labelHelp}
          </div>

          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-primary, #e2e8f0)', lineHeight: 1.4, margin: '0 0 0.6rem 0' }}>
            {activeTooltip.param.description}
          </p>

          <div style={{
            fontSize: '0.6875rem',
            color: 'var(--color-text-muted, #64748b)',
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            paddingTop: '0.4rem',
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            <span>Rango Sugerido:</span>
            <strong style={{ color: 'var(--color-accent-emerald, #10b981)' }}>
              {activeTooltip.param.defaultMin} a {activeTooltip.param.defaultMax} (Paso {activeTooltip.param.defaultStep})
            </strong>
          </div>
        </div>
      )}
    </div>
  );
};

export default StepIndicators;
