import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { useRealtimeJob } from '../hooks/useRealtimeJob';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import styles from '../styles/pages.module.css';

const PHASES = ['queued', 'indicators', 'genetic', 'rl', 'backtest', 'montecarlo', 'ranking', 'done'];

const JobProgress: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { progress, phase, status } = useRealtimeJob(id!);

  useEffect(() => {
    if (status === 'completed') {
      setTimeout(() => navigate(`/jobs/${id}/results`), 2000);
    }
  }, [status, id, navigate]);

  const currentPhaseIndex = PHASES.indexOf(phase);

  return (
    <div className={styles.progressContainer}>
      <div className={styles.progressCard}>
        <h2>Job Processing</h2>
        <p>Pipeline ID: {id}</p>
        
        <div className={styles.statusBadgeWrapper}>
          <Badge variant={status === 'running' ? 'info' : status === 'completed' ? 'success' : 'warning'}>
            {status.toUpperCase()}
          </Badge>
        </div>

        <div className={styles.mainProgress}>
          <div className={styles.circularProgress}>
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" className={styles.progressBg} />
              <circle cx="50" cy="50" r="45" className={styles.progressFg} style={{ strokeDashoffset: 283 - (283 * progress) / 100 }} />
            </svg>
            <div className={styles.progressText}>
              <span className={styles.progressPercent}>{Math.round(progress)}%</span>
            </div>
          </div>
        </div>

        <div className={styles.phaseList}>
          {PHASES.map((p, idx) => {
            const isDone = idx < currentPhaseIndex;
            const isCurrent = idx === currentPhaseIndex;
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
      </div>
    </div>
  );
};

export default JobProgress;
