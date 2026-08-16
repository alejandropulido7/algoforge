import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Strategy } from '../../types/strategy';
import Badge from '../common/Badge';
import styles from '../../styles/pages.module.css';

interface StrategyTableProps {
  strategies: Strategy[];
}

const StrategyTable: React.FC<StrategyTableProps> = ({ strategies }) => {
  const navigate = useNavigate();

  const formatPct = (val: number) => `${(val * 100).toFixed(2)}%`;
  const formatNum = (val: number) => val.toFixed(2);

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Score</th>
            <th>Return</th>
            <th>Drawdown</th>
            <th>Win Rate</th>
            <th>Sharpe</th>
            <th>Trades</th>
            <th>MC Robustness</th>
          </tr>
        </thead>
        <tbody>
          {strategies.map(s => (
            <tr key={s.id} className={styles.tableRowClickable} onClick={() => navigate(`/strategies/${s.id}`)}>
              <td>
                <div className={styles.rankCircle}>#{s.rank}</div>
              </td>
              <td className="font-bold text-cyan">{formatNum(s.total_score)}</td>
              <td className={s.total_return_pct >= 0 ? 'text-emerald' : 'text-rose'}>
                {formatPct(s.total_return_pct)}
              </td>
              <td className="text-rose">{formatPct(s.max_drawdown_pct)}</td>
              <td>{formatPct(s.win_rate)}</td>
              <td>{formatNum(s.sharpe_ratio)}</td>
              <td>{s.n_trades}</td>
              <td>
                <Badge variant={s.mc_robustness > 0.8 ? 'success' : s.mc_robustness > 0.5 ? 'warning' : 'error'}>
                  {formatPct(s.mc_robustness)}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StrategyTable;
