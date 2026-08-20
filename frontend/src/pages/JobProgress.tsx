import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Check, Ban, AlertTriangle, ArrowLeft, Clock, Cpu, Sparkles, Terminal } from 'lucide-react';
import { useRealtimeJob } from '../hooks/useRealtimeJob';
import { useCancelJob } from '../hooks/useJobs';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Modal from '../components/common/Modal';
import styles from '../styles/pages.module.css';

const PHASES = ['queued', 'indicators', 'genetic', 'rl', 'backtest', 'montecarlo', 'ranking', 'done'];

const JobProgress: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    progress,
    phase,
    status,
    subProgress,
    subCurrent,
    subTotal,
    validCandidates,
    liveMessage,
    createdAt
  } = useRealtimeJob(id!);
  const cancelJobMutation = useCancelJob();
  const [showCancelModal, setShowCancelModal] = useState(false);

  // Live Timer State (Stopwatch)
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (!createdAt) return;
    const startMs = new Date(createdAt).getTime();

    const updateTimer = () => {
      const nowMs = Date.now();
      const diff = Math.max(0, Math.floor((nowMs - startMs) / 1000));
      setElapsedSeconds(diff);
    };

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);

    return () => clearInterval(timerInterval);
  }, [createdAt]);

  useEffect(() => {
    if (status === 'completed') {
      const t = setTimeout(() => navigate(`/jobs/${id}/results`), 2000);
      return () => clearTimeout(t);
    }
  }, [status, id, navigate]);

  const handleConfirmCancel = async () => {
    if (!id) return;
    try {
      await cancelJobMutation.mutateAsync(id);
      setShowCancelModal(false);
    } catch (err) {
      console.error('Error al cancelar el job:', err);
    }
  };

  const formatTimer = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} min`;
  };

  const currentPhaseIndex = PHASES.indexOf(phase);
  const isCancelled = status === 'cancelled' || phase === 'cancelled';
  const isRunning = status === 'running' || status === 'pending';

  return (
    <div className={styles.progressContainer}>
      <div className={styles.progressCard} style={{ maxWidth: '780px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2>{isCancelled ? 'Análisis Cancelado' : 'Procesamiento de Estrategias'}</h2>
            <p style={{ margin: '0.25rem 0 0' }}>Job ID: <strong style={{ color: 'var(--color-accent-cyan)' }}>{id}</strong></p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Live Stopwatch Badge */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              background: 'rgba(0, 212, 255, 0.08)',
              border: '1px solid rgba(0, 212, 255, 0.25)',
              padding: '0.375rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.8125rem',
              color: 'var(--color-accent-cyan)'
            }}>
              <Clock size={14} className={isRunning ? 'animate-pulse' : ''} />
              <span>Tiempo: <strong>{formatTimer(elapsedSeconds)}</strong></span>
            </div>

            <Badge variant={
              isCancelled ? 'error' :
              status === 'running' ? 'info' :
              status === 'completed' ? 'success' :
              status === 'failed' ? 'error' : 'warning'
            }>
              {isCancelled ? 'CANCELADO' : status.toUpperCase()}
            </Badge>
          </div>
        </div>

        {isCancelled ? (
          <div style={{
            background: 'var(--color-bg-subtle)',
            border: '1px solid var(--color-border)',
            borderRadius: '10px',
            padding: '2.5rem 1.5rem',
            textAlign: 'center',
            margin: '1.75rem 0'
          }}>
            <div style={{
              display: 'inline-flex',
              padding: '1rem',
              background: 'rgba(244, 63, 94, 0.1)',
              borderRadius: '50%',
              color: 'var(--color-accent-rose)',
              marginBottom: '1rem'
            }}>
              <Ban size={36} />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>
              El análisis ha sido detenido por el usuario
            </h3>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9375rem', maxWidth: '520px', margin: '0 auto 1.75rem', lineHeight: '1.5' }}>
              Se detuvo el recorrido de combinaciones. Las estrategias candidatas que alcanzaron a evaluarse antes de la detención han sido procesadas y guardadas.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.875rem' }}>
              <Button variant="secondary" onClick={() => navigate('/dashboard')} className="flex items-center gap-2">
                <ArrowLeft size={16} />
                <span>Ir al Dashboard</span>
              </Button>
              <Button variant="primary" onClick={() => navigate(`/jobs/${id}/results`)} className="flex items-center gap-2">
                <Sparkles size={16} />
                <span>Ver Resultados Parciales</span>
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* Main Circular Progress */}
            <div className={styles.mainProgress} style={{ margin: '1.75rem 0 1.25rem' }}>
              <div className={styles.circularProgress}>
                <svg viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" className={styles.progressBg} />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    className={styles.progressFg}
                    style={{ strokeDashoffset: 283 - (283 * progress) / 100 }}
                  />
                </svg>
                <div className={styles.progressText}>
                  <span className={styles.progressPercent}>{Math.round(progress)}%</span>
                </div>
              </div>
            </div>

            {/* Sub-process Live Indicators Progress Bar */}
            {phase === 'indicators' && subTotal > 0 && (
              <div style={{
                background: 'rgba(0, 0, 0, 0.35)',
                border: '1px solid rgba(0, 212, 255, 0.25)',
                borderRadius: '10px',
                padding: '1.25rem',
                margin: '1.25rem 0 1.75rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.625rem', fontSize: '0.8125rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-accent-cyan)', fontWeight: 600 }}>
                    <Cpu size={16} />
                    <span>Subproceso: Evaluación Determinista de Indicadores & TP/SL</span>
                  </div>
                  <div style={{ color: 'var(--color-text-secondary)' }}>
                    Combinación <strong style={{ color: 'var(--color-text-primary)' }}>{subCurrent.toLocaleString()}</strong> de <strong style={{ color: 'var(--color-text-primary)' }}>{subTotal.toLocaleString()}</strong> ({subProgress}%)
                  </div>
                </div>

                {/* Linear sub-progress bar */}
                <div style={{
                  width: '100%',
                  height: '8px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '4px',
                  overflow: 'hidden',
                  marginBottom: '0.75rem'
                }}>
                  <div style={{
                    width: `${Math.min(100, Math.max(0, subProgress))}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #00d4ff, #10b981)',
                    borderRadius: '4px',
                    transition: 'width 250ms ease'
                  }} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', color: 'var(--color-accent-emerald)' }}>
                    <Sparkles size={13} />
                    <strong>{validCandidates}</strong> candidatas con operaciones registradas
                  </span>
                  <span>Procesamiento por lotes de 15</span>
                </div>

                {/* Live Ticker Terminal */}
                {liveMessage && (
                  <div style={{
                    marginTop: '0.75rem',
                    padding: '0.5rem 0.75rem',
                    background: '#090d16',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    color: '#94a3b8',
                    overflow: 'hidden',
                    whiteSpace: 'nowrap',
                    textOverflow: 'ellipsis'
                  }}>
                    <Terminal size={14} style={{ color: 'var(--color-accent-cyan)', flexShrink: 0 }} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{liveMessage}</span>
                  </div>
                )}
              </div>
            )}

            <div className={styles.phaseList}>
              {PHASES.map((p, idx) => {
                const isDone = idx < currentPhaseIndex || status === 'completed';
                const isCurrent = idx === currentPhaseIndex && isRunning;
                return (
                  <div key={p} className={`${styles.phaseItem} ${isDone ? styles.phaseDone : ''} ${isCurrent ? styles.phaseCurrent : ''}`}>
                    <div className={styles.phaseIcon}>
                      {isDone ? <Check size={14} strokeWidth={3} className="text-emerald" /> : isCurrent ? <Spinner size="sm" /> : idx + 1}
                    </div>
                    <span className={styles.phaseLabel}>{p.toUpperCase()}</span>
                  </div>
                );
              })}
            </div>

            {isRunning && (
              <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="secondary"
                  onClick={() => setShowCancelModal(true)}
                  style={{
                    color: 'var(--color-accent-rose)',
                    borderColor: 'rgba(244, 63, 94, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.625rem 1.25rem'
                  }}
                  disabled={cancelJobMutation.isPending}
                >
                  <Ban size={16} />
                  <span>{cancelJobMutation.isPending ? 'Deteniendo...' : 'Detener Análisis y Ver Resultados'}</span>
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Confirmation Modal for Canceling Job */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => !cancelJobMutation.isPending && setShowCancelModal(false)}
        title="Detener Análisis en Ejecución"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
            <div style={{ color: 'var(--color-accent-amber)', padding: '0.25rem' }}>
              <AlertTriangle size={28} />
            </div>
            <div>
              <p style={{ margin: 0, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                ¿Deseas detener el análisis ahora?
              </p>
              <p style={{ margin: '0.5rem 0 0', fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: '1.5' }}>
                El motor <strong>no descartará el trabajo realizado</strong>: compilará y guardará inmediatamente las mejores estrategias descubiertas hasta este momento ({validCandidates} candidatas evaluadas).
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Button
              variant="secondary"
              onClick={() => setShowCancelModal(false)}
              disabled={cancelJobMutation.isPending}
            >
              Continuar Ejecutando
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirmCancel}
              disabled={cancelJobMutation.isPending}
              className="flex items-center gap-2"
            >
              {cancelJobMutation.isPending ? <Spinner size="sm" /> : <Ban size={14} />}
              <span>{cancelJobMutation.isPending ? 'Deteniendo...' : 'Detener y Guardar Parciales'}</span>
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default JobProgress;
