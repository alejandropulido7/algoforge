import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileCode, Copy, Check, Download, Activity } from 'lucide-react';
import { useStrategy } from '../hooks/useStrategies';
import { exportStrategy } from '../services/api';
import EquityCurve from '../components/charts/EquityCurve';
import MonteCarloFan from '../components/charts/MonteCarloFan';
import MetricsCard from '../components/reports/MetricsCard';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import styles from '../styles/pages.module.css';

const StrategyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: strategy, isLoading } = useStrategy(id!);
  const [activeTab, setActiveTab] = useState<'mt5' | 'pine'>('mt5');
  const [code, setCode] = useState<string>('');
  const [loadingCode, setLoadingCode] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!strategy) return;
    const fetchCode = async () => {
      setLoadingCode(true);
      try {
        const res = await exportStrategy(strategy.id, activeTab);
        setCode(res.code);
      } catch {
        setCode(activeTab === 'mt5' ? '// Error generating MQL5 code' : '// Error generating Pine Script');
      } finally {
        setLoadingCode(false);
      }
    };
    fetchCode();
  }, [strategy, activeTab]);

  if (isLoading || !strategy) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  const formatPct = (val: number) => `${Number(val || 0).toFixed(2)}%`;
  const formatNum = (val: number) => Number(val || 0).toFixed(2);
  const formatCurrency = (val: number) => `$${Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeTab === 'mt5' ? 'mq5' : 'pine';
    const filename = `AlgoForge_Strategy_${strategy.rank}.${ext}`;
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <div className={styles.titleWithBadge}>
            <h2>Strategy #{strategy.rank}</h2>
            <Badge variant="info">Score: {formatNum(strategy.total_score)}</Badge>
          </div>
          <p className={styles.subtitle}>ID: {strategy.id}</p>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className={styles.metricsGrid}>
        <MetricsCard 
          label="Total Return" 
          value={strategy.total_net_profit ? `${formatCurrency(strategy.total_net_profit)} (${formatPct(strategy.total_return_pct)})` : formatPct(strategy.total_return_pct)} 
          trend={strategy.total_return_pct >= 0 ? 'up' : 'down'} 
          color={strategy.total_return_pct >= 0 ? 'emerald' : 'rose'} 
        />
        <MetricsCard 
          label="Max Drawdown" 
          value={formatPct(strategy.max_drawdown_pct)} 
          trend="down" 
          color="rose" 
        />
        <MetricsCard 
          label="Win Rate" 
          value={formatPct(strategy.win_rate)} 
          color="cyan" 
        />
        <MetricsCard 
          label="Sharpe Ratio" 
          value={formatNum(strategy.sharpe_ratio)} 
          color="cyan" 
        />
        <MetricsCard 
          label="Profit Factor" 
          value={formatNum(strategy.profit_factor)} 
          color={strategy.profit_factor >= 1.0 ? 'emerald' : 'rose'} 
        />
        <MetricsCard 
          label="Total Trades" 
          value={strategy.n_trades} 
          color="amber" 
        />
      </div>

      {/* MetaTrader 5 Detailed Statistics Panel */}
      <div style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.75rem' }}>
          <Activity size={18} color="var(--color-accent-cyan)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-main)', margin: 0 }}>
            MT5 Strategy Tester Detailed Report
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Gross Profit / Loss</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--color-accent-emerald)', fontWeight: 600 }}>{formatCurrency(strategy.gross_profit || 0)}</span>
              <span style={{ color: 'var(--color-accent-rose)', fontWeight: 600 }}>-{formatCurrency(strategy.gross_loss || 0)}</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Expected Payoff</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: (strategy.expected_payoff || 0) >= 0 ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)' }}>
              {formatCurrency(strategy.expected_payoff || 0)} <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>/ trade</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Max Consecutive Wins</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-emerald)' }}>
              {strategy.consecutive_wins_max || 0} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>({formatCurrency(strategy.consecutive_wins_max_cash || 0)})</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Max Consecutive Losses</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-rose)' }}>
              {strategy.consecutive_losses_max || 0} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>(-{formatCurrency(strategy.consecutive_losses_max_cash || 0)})</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Avg Consecutive Wins / Losses</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
              <span style={{ color: 'var(--color-accent-emerald)' }}>{strategy.consecutive_wins_avg || 1}</span> / <span style={{ color: 'var(--color-accent-rose)' }}>{strategy.consecutive_losses_avg || 1}</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Recovery Factor / MC Robustness</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-cyan)' }}>
              {formatNum(strategy.recovery_factor || 0)} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>({formatPct(strategy.mc_robustness)} MC)</span>
            </div>
          </div>

        </div>
      </div>

      <div className={styles.chartsGrid}>
        <EquityCurve data={strategy.equity_curve || []} />
        <MonteCarloFan paths={[
          strategy.equity_curve.map(v => v * 0.8), 
          strategy.equity_curve, 
          strategy.equity_curve.map(v => v * 1.2)
        ]} />
      </div>

      {/* Trade Log Table */}
      {strategy.trade_log && strategy.trade_log.length > 0 && (
        <div className={styles.tableCard} style={{ marginBottom: '1.5rem' }}>
          <div className="flex justify-between items-center mb-3">
            <h3 className={styles.tableTitle} style={{ margin: 0 }}>Trade Execution History (Sample)</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Showing first {Math.min(strategy.trade_log.length, 50)} trades</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.5rem' }}>#</th>
                  <th style={{ padding: '0.5rem' }}>Type</th>
                  <th style={{ padding: '0.5rem' }}>Entry Price</th>
                  <th style={{ padding: '0.5rem' }}>Exit Price</th>
                  <th style={{ padding: '0.5rem' }}>Size</th>
                  <th style={{ padding: '0.5rem' }}>Profit / Loss</th>
                  <th style={{ padding: '0.5rem' }}>Exit Reason</th>
                  <th style={{ padding: '0.5rem' }}>Bars</th>
                </tr>
              </thead>
              <tbody>
                {strategy.trade_log.slice(0, 50).map((t, idx) => {
                  const isProfit = (t.pnl || 0) >= 0;
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '0.5rem', color: 'var(--color-text-muted)' }}>{t.trade_idx || idx + 1}</td>
                      <td style={{ padding: '0.5rem' }}>
                        <span style={{
                          padding: '0.125rem 0.375rem',
                          borderRadius: '4px',
                          fontSize: '0.6875rem',
                          fontWeight: 600,
                          background: (t.direction === 'buy' || t.direction === 'long') ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                          color: (t.direction === 'buy' || t.direction === 'long') ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)'
                        }}>
                          {(t.direction || 'BUY').toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: '0.5rem' }}>{t.entry_price}</td>
                      <td style={{ padding: '0.5rem' }}>{t.exit_price}</td>
                      <td style={{ padding: '0.5rem' }}>{t.size || 0.1}</td>
                      <td style={{ padding: '0.5rem', fontWeight: 600, color: isProfit ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)' }}>
                        {isProfit ? `+${formatCurrency(t.pnl)}` : formatCurrency(t.pnl)}
                      </td>
                      <td style={{ padding: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-text-muted)' }}>
                          {t.exit_reason || 'SIGNAL'}
                        </span>
                      </td>
                      <td style={{ padding: '0.5rem', color: 'var(--color-text-muted)' }}>{t.duration_bars || 1}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Code Export Section */}
      <div className={styles.tableCard}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <FileCode size={20} className="text-cyan" />
            <h3 className={styles.tableTitle} style={{ margin: 0 }}>Export Executable Code</h3>
          </div>
        </div>

        <div className={styles.codeTabs}>
          <button 
            className={`${styles.codeTab} ${activeTab === 'mt5' ? styles.codeTabActive : ''}`} 
            onClick={() => setActiveTab('mt5')}
          >
            MQL5 Expert Advisor (MetaTrader 5)
          </button>
          <button 
            className={`${styles.codeTab} ${activeTab === 'pine' ? styles.codeTabActive : ''}`} 
            onClick={() => setActiveTab('pine')}
          >
            TradingView Pine Script v5
          </button>
        </div>

        <div className={styles.codeContainer}>
          {loadingCode ? (
            <div className="py-12 flex justify-center"><Spinner size="md" /></div>
          ) : (
            <pre className={styles.codeBlock}>
              <code>{code || '// Loading code...'}</code>
            </pre>
          )}
          
          <div className="flex gap-2 absolute top-3 right-3">
            <Button size="sm" variant="secondary" className="flex items-center gap-1" onClick={handleCopy}>
              {copied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </Button>
            <Button size="sm" variant="primary" className="flex items-center gap-1" onClick={handleDownload}>
              <Download size={14} />
              <span>Download .{activeTab === 'mt5' ? 'mq5' : 'pine'}</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyDetail;
