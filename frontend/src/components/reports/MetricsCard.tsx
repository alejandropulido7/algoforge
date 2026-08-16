import React from 'react';
import styles from '../../styles/pages.module.css';

interface MetricsCardProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'cyan' | 'emerald' | 'amber' | 'rose';
}

const MetricsCard: React.FC<MetricsCardProps> = ({ label, value, trend, color = 'cyan' }) => {
  return (
    <div className={styles.metricsCard} style={{ borderTop: `2px solid var(--color-accent-${color})` }}>
      <div className={styles.metricsLabel}>{label}</div>
      <div className={styles.metricsValueContainer}>
        <span className={styles.metricsValue}>{value}</span>
        {trend && (
          <span className={`${styles.metricsTrend} ${trend === 'up' ? 'text-emerald' : trend === 'down' ? 'text-rose' : 'text-secondary'}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '-'}
          </span>
        )}
      </div>
    </div>
  );
};

export default MetricsCard;
