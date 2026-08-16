import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import styles from '../../styles/charts.module.css';

interface MonteCarloFanProps {
  paths: number[][]; // e.g., 5th, 50th, 95th percentiles
}

const MonteCarloFan: React.FC<MonteCarloFanProps> = ({ paths }) => {
  if (!paths || paths.length < 3) return null;

  // Assume paths are [p5, p50, p95]
  const p5 = paths[0];
  const p50 = paths[1];
  const p95 = paths[2];

  const chartData = p5.map((_, idx) => ({
    idx,
    p5: p5[idx],
    p50: p50[idx],
    p95: p95[idx],
  }));

  return (
    <div className={styles.chartContainer}>
      <h4 className={styles.chartTitle}>Monte Carlo Robustness</h4>
      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
            <XAxis dataKey="idx" hide />
            <YAxis stroke="var(--color-text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border)' }}
            />
            <Line type="monotone" dataKey="p95" stroke="var(--color-accent-emerald)" strokeWidth={1} dot={false} strokeDasharray="5 5" />
            <Line type="monotone" dataKey="p50" stroke="var(--color-accent-cyan)" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="p5" stroke="var(--color-accent-rose)" strokeWidth={1} dot={false} strokeDasharray="5 5" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MonteCarloFan;
