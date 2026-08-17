import React, { useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import styles from '../../styles/charts.module.css';

interface EquityCurveProps {
  data: number[];
}

const downsample = (arr: number[], maxPoints = 200): { idx: number; value: number }[] => {
  if (!arr || arr.length === 0) return [];
  if (arr.length <= maxPoints) {
    return arr.map((val, idx) => ({ idx, value: Number(val || 0) }));
  }
  const step = Math.ceil(arr.length / maxPoints);
  const result: { idx: number; value: number }[] = [];
  for (let i = 0; i < arr.length; i += step) {
    result.push({ idx: i, value: Number(arr[i] || 0) });
  }
  if (result[result.length - 1].idx !== arr.length - 1) {
    result.push({ idx: arr.length - 1, value: Number(arr[arr.length - 1] || 0) });
  }
  return result;
};

const EquityCurve: React.FC<EquityCurveProps> = ({ data }) => {
  const chartData = useMemo(() => downsample(data, 200), [data]);

  return (
    <div className={styles.chartContainer}>
      <h4 className={styles.chartTitle}>Equity Curve</h4>
      <div className={styles.chartWrapper}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-accent-cyan)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="var(--color-accent-cyan)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
            <XAxis dataKey="idx" hide />
            <YAxis stroke="var(--color-text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border)' }}
              itemStyle={{ color: 'var(--color-accent-cyan)' }}
              labelStyle={{ color: 'var(--color-text-secondary)' }}
              formatter={(val: any) => [`$${Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 'Equity']}
            />
            <Area 
              type="linear" 
              dataKey="value" 
              stroke="var(--color-accent-cyan)" 
              fillOpacity={1} 
              fill="url(#colorValue)" 
              isAnimationActive={false}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default React.memo(EquityCurve);
