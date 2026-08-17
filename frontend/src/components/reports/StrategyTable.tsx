import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Strategy } from '../../types/strategy';
import Badge from '../common/Badge';
import { ArrowUpDown, ArrowUp, ArrowDown, Cpu } from 'lucide-react';
import styles from '../../styles/pages.module.css';

interface StrategyTableProps {
  strategies: Strategy[];
}

type SortField = 'rank' | 'total_score' | 'total_return_pct' | 'max_drawdown_pct' | 'win_rate' | 'sharpe_ratio' | 'n_trades' | 'mc_robustness';

const StrategyTable: React.FC<StrategyTableProps> = ({ strategies }) => {
  const navigate = useNavigate();
  const [sortField, setSortField] = useState<SortField>('rank');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const formatPct = (val: number) => `${Number(val || 0).toFixed(2)}%`;
  const formatNum = (val: number) => Number(val || 0).toFixed(2);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      // Default to descending for scores/returns, ascending for rank/drawdown
      setSortDir((field === 'rank' || field === 'max_drawdown_pct') ? 'asc' : 'desc');
    }
  };

  const sortedStrategies = useMemo(() => {
    return [...strategies].sort((a, b) => {
      let valA = (a as any)[sortField] ?? 0;
      let valB = (b as any)[sortField] ?? 0;
      if (typeof valA === 'string') valA = parseFloat(valA) || 0;
      if (typeof valB === 'string') valB = parseFloat(valB) || 0;

      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [strategies, sortField, sortDir]);

  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown size={12} style={{ opacity: 0.4, marginLeft: '4px' }} />;
    }
    return sortDir === 'asc' ? 
      <ArrowUp size={12} style={{ color: 'var(--color-accent-cyan)', marginLeft: '4px' }} /> : 
      <ArrowDown size={12} style={{ color: 'var(--color-accent-cyan)', marginLeft: '4px' }} />;
  };

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th onClick={() => handleSort('rank')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Rank {renderSortIcon('rank')}</div>
            </th>
            <th onClick={() => handleSort('total_score')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Score {renderSortIcon('total_score')}</div>
            </th>
            <th onClick={() => handleSort('total_return_pct')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Return {renderSortIcon('total_return_pct')}</div>
            </th>
            <th onClick={() => handleSort('max_drawdown_pct')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Drawdown {renderSortIcon('max_drawdown_pct')}</div>
            </th>
            <th onClick={() => handleSort('win_rate')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Win Rate {renderSortIcon('win_rate')}</div>
            </th>
            <th onClick={() => handleSort('sharpe_ratio')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Sharpe {renderSortIcon('sharpe_ratio')}</div>
            </th>
            <th onClick={() => handleSort('n_trades')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>Trades {renderSortIcon('n_trades')}</div>
            </th>
            <th onClick={() => handleSort('mc_robustness')} style={{ cursor: 'pointer', userSelect: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>MC Robustness {renderSortIcon('mc_robustness')}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedStrategies.map(s => {
            const isRL = (s.strategy_tree || '').includes("RL_Agent") || (s as any).is_rl;
            return (
              <tr key={s.id} className={styles.tableRowClickable} onClick={() => navigate(`/strategies/${s.id}`)}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                    <div className={styles.rankCircle}>#{s.rank}</div>
                    {isRL && (
                      <span title="Deep RL Agent" style={{ display: 'flex', alignItems: 'center', color: 'var(--color-accent-cyan)' }}>
                        <Cpu size={14} />
                      </span>
                    )}
                  </div>
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
                  <Badge variant={s.mc_robustness >= 70 ? 'success' : s.mc_robustness >= 40 ? 'warning' : 'error'}>
                    {formatPct(s.mc_robustness)}
                  </Badge>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default StrategyTable;
