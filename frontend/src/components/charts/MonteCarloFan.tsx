import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import styles from '../../styles/charts.module.css';

interface MonteCarloFanProps {
  paths: number[][]; // [p5, p50, p95]
}

const downsampleFan = (p5: number[], p50: number[], p95: number[], maxPoints = 200) => {
  if (!p5 || p5.length === 0) return [];
  const len = Math.min(p5.length, p50?.length || p5.length, p95?.length || p5.length);
  if (len <= maxPoints) {
    return Array.from({ length: len }, (_, i) => ({
      idx: i,
      p5: Number(p5[i] || 0),
      p50: Number(p50 ? p50[i] : p5[i]),
      p95: Number(p95 ? p95[i] : p5[i]),
    }));
  }
  const step = Math.ceil(len / maxPoints);
  const res = [];
  for (let i = 0; i < len; i += step) {
    res.push({
      idx: i,
      p5: Number(p5[i] || 0),
      p50: Number(p50 ? p50[i] : p5[i]),
      p95: Number(p95 ? p95[i] : p5[i]),
    });
  }
  if (res[res.length - 1].idx !== len - 1) {
    res.push({
      idx: len - 1,
      p5: Number(p5[len - 1] || 0),
      p50: Number(p50 ? p50[len - 1] : p5[len - 1]),
      p95: Number(p95 ? p95[len - 1] : p5[len - 1]),
    });
  }
  return res;
};

const MonteCarloFan: React.FC<MonteCarloFanProps> = ({ paths }) => {
  const chartData = useMemo(() => {
    if (!paths || paths.length < 3) return [];
    return downsampleFan(paths[0], paths[1], paths[2], 200);
  }, [paths]);

  if (!paths || paths.length < 3 || chartData.length === 0) return null;

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
              formatter={(val: any, name: any) => [
                `$${Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
                name === 'p95' ? '95th Percentile' : (name === 'p50' ? 'Median (50th)' : '5th Percentile')
              ]}
            />
            <Line type="linear" dataKey="p95" stroke="var(--color-accent-emerald)" strokeWidth={1.5} dot={false} strokeDasharray="4 4" isAnimationActive={false} />
            <Line type="linear" dataKey="p50" stroke="var(--color-accent-cyan)" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="linear" dataKey="p5" stroke="var(--color-accent-rose)" strokeWidth={1.5} dot={false} strokeDasharray="4 4" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default React.memo(MonteCarloFan);
