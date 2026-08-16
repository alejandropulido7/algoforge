import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import styles from '../../styles/charts.module.css';

interface EquityCurveProps {
  data: number[];
}

const EquityCurve: React.FC<EquityCurveProps> = ({ data }) => {
  const chartData = data.map((val, idx) => ({ idx, value: val }));

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
            />
            <Area type="monotone" dataKey="value" stroke="var(--color-accent-cyan)" fillOpacity={1} fill="url(#colorValue)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default EquityCurve;
