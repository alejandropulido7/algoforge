import React, { useState, useMemo } from 'react';
import { useJobStore } from '../../store/jobStore';
import { Info, X, Sparkles, Plus, Check, Target, Shield } from 'lucide-react';
import { TPSL_CATALOG, getTPSLModeItem, calculateTotalTPSLCombinations } from '../../data/tpslCatalog';
import type { TPSLParamDef } from '../../data/tpslCatalog';

export const TPSLManagementSection: React.FC = () => {
  const { config, toggleTPSLMode, setTPSLParamRange } = useJobStore();
  const [activeTooltip, setActiveTooltip] = useState<{
    modeName: string;
    param: TPSLParamDef;
    x: number;
    y: number;
  } | null>(null);

  const selectedModes = useMemo(() => {
    return (config.tpslModes || [])
      .map(id => getTPSLModeItem(id))
      .filter((item): item is NonNullable<typeof item> => Boolean(item));
  }, [config.tpslModes]);

  const totalCombinations = useMemo(() => {
    return calculateTotalTPSLCombinations(config.tpslModes || [], config.tpslRanges || {});
  }, [config.tpslModes, config.tpslRanges]);

  const handleAddMode = (id: string) => {
    toggleTPSLMode(id, true);
  };

  const handleRemoveMode = (id: string) => {
    toggleTPSLMode(id, false);
  };

  const handleRangeChange = (
    modeId: string,
    paramKey: string,
    field: 'min' | 'step' | 'max',
    value: number
  ) => {
    setTPSLParamRange(modeId, paramKey, { [field]: value });
  };

  return (
    <div style={{
      background: 'var(--color-bg-card, #131829)',
      border: '1px solid var(--color-border, #1f293d)',
      borderRadius: '10px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)'
    }}>
      {/* SECTION HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            background: 'rgba(0, 212, 255, 0.1)',
            padding: '0.4rem',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Target size={20} color="var(--color-accent-cyan, #00d4ff)" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-main, #f8fafc)', margin: 0 }}>
              TP/SL Management
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted, #94a3b8)', margin: '0.125rem 0 0 0' }}>
              Define los modos de Take Profit, Stop Loss y protecciones activas para optimizar el espacio de salidas de las estrategias.
            </p>
          </div>
        </div>
        <span style={{
          fontSize: '0.75rem',
          color: 'var(--color-accent-cyan, #00d4ff)',
          background: 'rgba(0, 212, 255, 0.08)',
          padding: '0.25rem 0.625rem',
          borderRadius: '20px',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          fontWeight: 500
        }}>
          {selectedModes.length} de {TPSL_CATALOG.length} Modos Activos
        </span>
      </div>

      {/* TOP PILLS: AGREGAR / ACTIVAR MODO */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.015)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        borderRadius: '8px',
        padding: '0.875rem 1rem',
        margin: '1rem 0 1.25rem 0'
      }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary, #94a3b8)', marginBottom: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Seleccionar Modos de Salida para Optimización
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {TPSL_CATALOG.map(mode => {
            const isSelected = (config.tpslModes || []).includes(mode.id);
            return (
              <button
                key={mode.id}
                type="button"
                onClick={() => {
                  if (isSelected) {
                    handleRemoveMode(mode.id);
                  } else {
                    handleAddMode(mode.id);
                  }
                }}
                title={mode.desc}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.375rem',
                  padding: '0.4rem 0.75rem',
                  borderRadius: '20px',
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  border: isSelected
                    ? '1px solid var(--color-accent-cyan, #00d4ff)'
                    : '1px solid var(--color-border, #1f293d)',
                  background: isSelected
                    ? 'rgba(0, 212, 255, 0.12)'
                    : 'rgba(255, 255, 255, 0.03)',
                  color: isSelected
                    ? 'var(--color-accent-cyan, #00d4ff)'
                    : 'var(--color-text-secondary, #94a3b8)',
                  boxShadow: isSelected
                    ? '0 0 10px rgba(0, 212, 255, 0.15)'
                    : 'none'
                }}
              >
                {isSelected ? <Check size={13} strokeWidth={3} /> : <Plus size={13} strokeWidth={2.5} />}
                <span>{mode.name}</span>
                <span style={{
                  fontSize: '0.6875rem',
                  opacity: 0.7,
                  marginLeft: '2px'
                }}>
                  ({mode.badge})
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* MAIN TP/SL TABLE */}
      {selectedModes.length > 0 ? (
        <div style={{
          border: '1px solid var(--color-border, #1f293d)',
          borderRadius: '8px',
          overflow: 'hidden',
          background: 'rgba(10, 14, 26, 0.4)'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{
                background: 'rgba(255, 255, 255, 0.02)',
                borderBottom: '1px solid var(--color-border, #1f293d)',
                color: 'var(--color-text-secondary, #94a3b8)',
                textAlign: 'left'
              }}>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 600, width: '28%' }}>Modo de salida</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 600, width: '32%' }}>Parámetro</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'center', width: '13%' }}>Desde</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'center', width: '13%' }}>Pasos</th>
                <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'center', width: '14%' }}>Hasta</th>
              </tr>
            </thead>
            <tbody>
              {selectedModes.map((mode, modeIdx) => {
                const isEven = modeIdx % 2 === 0;
                const rowBg = isEven ? 'rgba(255, 255, 255, 0.01)' : 'transparent';

                return (
                  <React.Fragment key={mode.id}>
                    {mode.params.map((param, paramIdx) => {
                      const userRange = config.tpslRanges?.[mode.id]?.[param.key] || {
                        min: param.defaultMin,
                        step: param.defaultStep,
                        max: param.defaultMax
                      };

                      return (
                        <tr
                          key={`${mode.id}-${param.key}`}
                          style={{
                            background: rowBg,
                            borderBottom: paramIdx === mode.params.length - 1
                              ? '1px solid var(--color-border, #1f293d)'
                              : '1px solid rgba(255, 255, 255, 0.03)',
                            transition: 'background 0.15s ease'
                          }}
                        >
                          {/* MODO DE SALIDA CELL (with rowSpan) */}
                          {paramIdx === 0 && (
                            <td
                              rowSpan={mode.params.length}
                              style={{
                                padding: '0.75rem 1rem',
                                verticalAlign: 'top',
                                borderRight: '1px solid rgba(255, 255, 255, 0.04)'
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <button
                                  type="button"
                                  onClick={() => handleRemoveMode(mode.id)}
                                  title={`Eliminar ${mode.name}`}
                                  style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'var(--color-text-muted, #64748b)',
                                    cursor: 'pointer',
                                    padding: '2px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    borderRadius: '4px'
                                  }}
                                  onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--color-accent-rose, #f43f5e)')}
                                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--color-text-muted, #64748b)')}
                                >
                                  <X size={14} />
                                </button>
                                <span style={{
                                  fontWeight: 600,
                                  color: 'var(--color-accent-cyan, #00d4ff)',
                                  fontSize: '0.9375rem'
                                }}>
                                  {mode.name}
                                </span>
                                <span style={{
                                  fontSize: '0.6875rem',
                                  padding: '0.125rem 0.375rem',
                                  borderRadius: '4px',
                                  background: 'rgba(255, 255, 255, 0.04)',
                                  color: 'var(--color-text-muted, #94a3b8)',
                                  border: '1px solid rgba(255, 255, 255, 0.08)'
                                }}>
                                  {mode.badge}
                                </span>
                              </div>
                              <div style={{ fontSize: '0.6875rem', color: 'var(--color-text-muted, #64748b)', marginTop: '0.25rem', paddingLeft: '1.35rem' }}>
                                {mode.desc}
                              </div>
                            </td>
                          )}

                          {/* PARÁMETRO CELL WITH INFO TOAST TRIGGER */}
                          <td style={{ padding: '0.625rem 1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <span style={{ color: 'var(--color-text-main, #f8fafc)', fontWeight: 500 }}>
                                {param.name}
                              </span>
                              <button
                                type="button"
                                title="Ver explicación completa"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  const rect = e.currentTarget.getBoundingClientRect();
                                  setActiveTooltip(prev =>
                                    prev?.param.key === param.key && prev?.modeName === mode.name
                                      ? null
                                      : {
                                          modeName: mode.name,
                                          param,
                                          x: Math.min(rect.right + 12, window.innerWidth - 340),
                                          y: rect.top - 20
                                        }
                                  );
                                }}
                                onMouseEnter={(e) => {
                                  const rect = e.currentTarget.getBoundingClientRect();
                                  setActiveTooltip({
                                    modeName: mode.name,
                                    param,
                                    x: Math.min(rect.right + 12, window.innerWidth - 340),
                                    y: rect.top - 20
                                  });
                                }}
                                style={{
                                  background: 'transparent',
                                  border: 'none',
                                  color: 'var(--color-text-muted, #64748b)',
                                  cursor: 'pointer',
                                  padding: '2px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  borderRadius: '50%',
                                  transition: 'color 0.15s ease'
                                }}
                                onFocus={() => {}}
                              >
                                <Info size={14} />
                              </button>
                            </div>
                          </td>

                          {/* DESDE (MIN) INPUT */}
                          <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                            <input
                              type="number"
                              step={param.defaultStep}
                              value={userRange.min}
                              onChange={(e) => handleRangeChange(mode.id, param.key, 'min', parseFloat(e.target.value) || 0)}
                              style={{
                                width: '70px',
                                textAlign: 'center',
                                padding: '0.35rem 0.5rem',
                                borderRadius: '6px',
                                border: '1px solid var(--color-border, #1f293d)',
                                background: 'rgba(255, 255, 255, 0.04)',
                                color: 'var(--color-text-main, #f8fafc)',
                                fontSize: '0.875rem',
                                outline: 'none'
                              }}
                            />
                          </td>

                          {/* PASOS (STEP) INPUT */}
                          <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                            <input
                              type="number"
                              step={param.defaultStep}
                              min="0.01"
                              value={userRange.step}
                              onChange={(e) => handleRangeChange(mode.id, param.key, 'step', parseFloat(e.target.value) || 1)}
                              style={{
                                width: '70px',
                                textAlign: 'center',
                                padding: '0.35rem 0.5rem',
                                borderRadius: '6px',
                                border: '1px solid var(--color-border, #1f293d)',
                                background: 'rgba(255, 255, 255, 0.04)',
                                color: 'var(--color-text-main, #f8fafc)',
                                fontSize: '0.875rem',
                                outline: 'none'
                              }}
                            />
                          </td>

                          {/* HASTA (MAX) INPUT */}
                          <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                            <input
                              type="number"
                              step={param.defaultStep}
                              value={userRange.max}
                              onChange={(e) => handleRangeChange(mode.id, param.key, 'max', parseFloat(e.target.value) || 0)}
                              style={{
                                width: '70px',
                                textAlign: 'center',
                                padding: '0.35rem 0.5rem',
                                borderRadius: '6px',
                                border: '1px solid var(--color-border, #1f293d)',
                                background: 'rgba(255, 255, 255, 0.04)',
                                color: 'var(--color-text-main, #f8fafc)',
                                fontSize: '0.875rem',
                                outline: 'none'
                              }}
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '2rem 1rem',
          border: '1px dashed var(--color-border, #1f293d)',
          borderRadius: '8px',
          color: 'var(--color-text-muted, #64748b)'
        }}>
          <Shield size={28} style={{ opacity: 0.5, marginBottom: '0.5rem' }} />
          <p style={{ margin: 0, fontSize: '0.875rem' }}>
            No hay modos de salida seleccionados. Las estrategias cerrarán únicamente por señal contraria de indicadores.
          </p>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', opacity: 0.7 }}>
            Haz clic en los botones superiores para activar Take Profit, Stop Loss, Trailing o Breakeven.
          </p>
        </div>
      )}

      {/* BOTTOM SUMMARY: COMBINACIONES POSIBLES */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginTop: '1.25rem',
        padding: '0.875rem 1.25rem',
        background: 'rgba(0, 212, 255, 0.03)',
        border: '1px solid rgba(0, 212, 255, 0.12)',
        borderRadius: '8px',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={18} color="var(--color-accent-cyan, #00d4ff)" />
          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary, #94a3b8)', fontWeight: 500 }}>
            Combinaciones de TP/SL posibles:
          </span>
        </div>
        <div style={{
          fontSize: '1.25rem',
          fontWeight: 700,
          color: 'var(--color-accent-cyan, #00d4ff)',
          fontFamily: 'monospace',
          letterSpacing: '0.025em'
        }}>
          {totalCombinations}
        </div>
      </div>

      {/* FLOATING TOAST / POPOVER FOR (i) */}
      {activeTooltip && (
        <>
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 9998
            }}
            onClick={() => setActiveTooltip(null)}
          />
          <div
            style={{
              position: 'fixed',
              top: Math.max(10, activeTooltip.y),
              left: activeTooltip.x,
              zIndex: 9999,
              width: '320px',
              background: '#0d1322',
              border: '1px solid var(--color-accent-cyan, #00d4ff)',
              borderRadius: '8px',
              padding: '1rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6), 0 0 12px rgba(0, 212, 255, 0.2)',
              animation: 'fadeIn 0.15s ease'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-accent-cyan, #00d4ff)' }}>
                {activeTooltip.modeName} — {activeTooltip.param.name}
              </span>
              <button
                type="button"
                onClick={() => setActiveTooltip(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--color-text-muted, #94a3b8)',
                  cursor: 'pointer',
                  padding: '2px'
                }}
              >
                <X size={14} />
              </button>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-main, #f8fafc)', lineHeight: '1.4', margin: '0 0 0.5rem 0' }}>
              {activeTooltip.param.description}
            </p>
            <div style={{
              fontSize: '0.6875rem',
              color: 'var(--color-text-muted, #94a3b8)',
              background: 'rgba(255, 255, 255, 0.03)',
              padding: '0.375rem 0.5rem',
              borderRadius: '4px',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
              💡 <strong>Rango sugerido:</strong> Desde {activeTooltip.param.defaultMin} hasta {activeTooltip.param.defaultMax} (Pasos: {activeTooltip.param.defaultStep})
            </div>
          </div>
        </>
      )}
    </div>
  );
};
