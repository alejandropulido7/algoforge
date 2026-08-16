import React from 'react';
import styles from '../../styles/components.module.css';

interface ProgressBarProps {
  percentage: number;
  label?: string;
  phase?: string;
  color?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ percentage, label, phase, color }) => {
  const clamp = (val: number) => Math.min(Math.max(val, 0), 100);
  const p = clamp(percentage);

  return (
    <div className={styles.progressBarContainer}>
      <div className={styles.progressBarHeader}>
        {label && <span className={styles.progressLabel}>{label}</span>}
        {phase && <span className={styles.progressPhase}>{phase}</span>}
        <span className={styles.progressValue}>{Math.round(p)}%</span>
      </div>
      <div className={styles.progressBarTrack}>
        <div 
          className={styles.progressBarFill} 
          style={{ 
            width: `${p}%`,
            backgroundColor: color || 'var(--color-accent-cyan)'
          }} 
        />
      </div>
    </div>
  );
};

export default ProgressBar;
