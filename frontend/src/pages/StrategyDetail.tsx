import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileCode, Copy, Check, Download, Activity, Cpu, HelpCircle, ChevronDown, ChevronUp, FolderCheck, History, GitBranch } from 'lucide-react';
import { useStrategy } from '../hooks/useStrategies';
import { useJob } from '../hooks/useJobs';
import { exportStrategy, downloadOnnxModel } from '../services/api';
import EquityCurve from '../components/charts/EquityCurve';
import MonteCarloFan from '../components/charts/MonteCarloFan';
import MetricsCard from '../components/reports/MetricsCard';
import JobConfigCard from '../components/reports/JobConfigCard';
import { StrategyExplainerCard } from '../components/reports/StrategyExplainerCard';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import styles from '../styles/pages.module.css';

const StrategyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: strategy, isLoading } = useStrategy(id!);
  const { data: job } = useJob(strategy?.job_id || '');
  const [activeTab, setActiveTab] = useState<'mt5' | 'pine' | 'python'>('mt5');
  const [code, setCode] = useState<string>('');
  const [loadingCode, setLoadingCode] = useState(false);
  const [copied, setCopied] = useState(false);
  const [downloadingOnnx, setDownloadingOnnx] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [tradeFilter, setTradeFilter] = useState<'latest50' | 'first50' | 'all'>('latest50');

  const stratId = strategy?.id;

  useEffect(() => {
    if (!stratId) return;
    let isMounted = true;
    const fetchCode = async () => {
      setLoadingCode(true);
      try {
        const res = await exportStrategy(stratId, activeTab);
        if (isMounted) setCode(res.code);
      } catch {
        if (isMounted) {
          setCode(activeTab === 'mt5' ? '// Error generating MQL5 code' : (activeTab === 'pine' ? '// Error generating Pine Script' : '# Error generating Python script'));
        }
      } finally {
        if (isMounted) setLoadingCode(false);
      }
    };
    fetchCode();
    return () => {
      isMounted = false;
    };
  }, [stratId, activeTab]);

  if (isLoading || !strategy) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  const formatPct = (val: number) => `${Number(val || 0).toFixed(2)}%`;
  const formatNum = (val: number) => Number(val || 0).toFixed(2);
  const formatCurrency = (val: number) => `$${Number(val || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const isRLStrategy = (strategy.strategy_tree || '').includes("RL_Agent") || 
                       Boolean((strategy as any).is_rl) || 
                       Boolean((strategy as any).onnx_filename);

  // Robust calculation of MT5 Strategy Tester metrics if missing from database record
  const tradeLog = strategy.trade_log || [];
  const displayedTrades = tradeFilter === 'latest50'
    ? [...tradeLog].slice(-50).reverse()
    : (tradeFilter === 'first50' ? tradeLog.slice(0, 50) : tradeLog);

  const pnls = tradeLog.map(t => Number(t.pnl || 0));
  
  const grossProfit = (strategy.gross_profit && strategy.gross_profit > 0) 
    ? strategy.gross_profit 
    : pnls.filter(p => p > 0).reduce((a, b) => a + b, 0);

  const grossLoss = (strategy.gross_loss && strategy.gross_loss > 0)
    ? strategy.gross_loss
    : Math.abs(pnls.filter(p => p < 0).reduce((a, b) => a + b, 0));

  const totalNetProfit = (strategy.total_net_profit !== undefined && strategy.total_net_profit !== 0)
    ? strategy.total_net_profit
    : (grossProfit - grossLoss);

  const expectedPayoff = (strategy.expected_payoff !== undefined && strategy.expected_payoff !== 0)
    ? strategy.expected_payoff
    : (pnls.length > 0 ? (totalNetProfit / pnls.length) : 0);

  // Consecutive Streaks Analysis
  let currW = 0, currL = 0, maxW = 0, maxL = 0;
  let currWCash = 0, currLCash = 0, maxWCash = 0, maxLCash = 0;
  const wStreaks: number[] = [], lStreaks: number[] = [];

  pnls.forEach(p => {
    if (p > 0) {
      currW++;
      currWCash += p;
      if (currL > 0) {
        lStreaks.push(currL);
        currL = 0;
        currLCash = 0;
      }
      if (currW > maxW) maxW = currW;
      if (currWCash > maxWCash) maxWCash = currWCash;
    } else if (p < 0) {
      currL++;
      currLCash += Math.abs(p);
      if (currW > 0) {
        wStreaks.push(currW);
        currW = 0;
        currWCash = 0;
      }
      if (currL > maxL) maxL = currL;
      if (currLCash > maxLCash) maxLCash = currLCash;
    }
  });
  if (currW > 0) wStreaks.push(currW);
  if (currL > 0) lStreaks.push(currL);

  const maxConsecWins = strategy.consecutive_wins_max || maxW;
  const maxConsecWinsCash = strategy.consecutive_wins_max_cash || maxWCash;
  const maxConsecLosses = strategy.consecutive_losses_max || maxL;
  const maxConsecLossesCash = strategy.consecutive_losses_max_cash || maxLCash;
  const avgConsecWins = strategy.consecutive_wins_avg || (wStreaks.length ? (wStreaks.reduce((a, b) => a + b, 0) / wStreaks.length) : 1);
  const avgConsecLosses = strategy.consecutive_losses_avg || (lStreaks.length ? (lStreaks.reduce((a, b) => a + b, 0) / lStreaks.length) : 1);
  const recoveryFactor = strategy.recovery_factor || (totalNetProfit / Math.max(1, (strategy.max_drawdown_pct || 10)));

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadCode = () => {
    const extMap = { mt5: 'mq5', pine: 'pine', python: 'py' };
    const ext = extMap[activeTab];
    const filename = `AlgoForge_Strategy_${strategy.rank}.${ext}`;
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadOnnx = async () => {
    setDownloadingOnnx(true);
    try {
      const blob = await downloadOnnxModel(strategy.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AlgoForge_Strategy_${strategy.rank}.onnx`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("ONNX model file not found on server for this strategy.");
    } finally {
      setDownloadingOnnx(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <div className={styles.titleWithBadge}>
            <h2>Strategy #{strategy.rank}</h2>
            <Badge variant="info">Score: {formatNum(strategy.total_score)}</Badge>
            {isRLStrategy && (
              <Badge variant="success">Deep RL (Neural ONNX)</Badge>
            )}
          </div>
          <p className={styles.subtitle}>ID: {strategy.id}</p>
        </div>
      </div>

      {/* Parent Job Configuration Card */}
      {job?.config && (
        <JobConfigCard config={job.config} defaultExpanded={false} />
      )}

      {/* Human-Readable Strategy Explanation & Mechanics */}
      <StrategyExplainerCard strategy={strategy} config={job?.config} />

      {/* Strategy Rule & Logic Formula */}
      {strategy.strategy_tree && (
        <div style={{
          background: 'var(--color-bg-card)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <GitBranch size={16} color="var(--color-accent-cyan)" />
            <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-text-main)' }}>
              Discovered Strategy Logic & Execution Tree
            </span>
          </div>
          <code style={{
            display: 'block',
            padding: '0.75rem 1rem',
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '6px',
            color: 'var(--color-accent-emerald)',
            fontSize: '0.8125rem',
            fontFamily: 'monospace',
            overflowX: 'auto',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            {strategy.strategy_tree}
          </code>
        </div>
      )}

      {/* Primary KPI Grid */}
      <div className={styles.metricsGrid}>
        <MetricsCard 
          label="Total Return" 
          value={totalNetProfit ? `${formatCurrency(totalNetProfit)} (${formatPct(strategy.total_return_pct)})` : formatPct(strategy.total_return_pct)} 
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
              <span style={{ color: 'var(--color-accent-emerald)', fontWeight: 600 }}>{formatCurrency(grossProfit)}</span>
              <span style={{ color: 'var(--color-accent-rose)', fontWeight: 600 }}>-{formatCurrency(grossLoss)}</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Expected Payoff</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: expectedPayoff >= 0 ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)' }}>
              {formatCurrency(expectedPayoff)} <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>/ trade</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Max Consecutive Wins</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-emerald)' }}>
              {maxConsecWins} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>({formatCurrency(maxConsecWinsCash)})</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Max Consecutive Losses</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-rose)' }}>
              {maxConsecLosses} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>(-{formatCurrency(maxConsecLossesCash)})</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Avg Consecutive Wins / Losses</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
              <span style={{ color: 'var(--color-accent-emerald)' }}>{formatNum(avgConsecWins)}</span> / <span style={{ color: 'var(--color-accent-rose)' }}>{formatNum(avgConsecLosses)}</span>
            </div>
          </div>

          <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.875rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Recovery Factor / MC Robustness</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-accent-cyan)' }}>
              {formatNum(recoveryFactor)} <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>({formatPct(strategy.mc_robustness)} MC)</span>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.chartsGrid}>
        <EquityCurve data={strategy.equity_curve || []} />
        <MonteCarloFan paths={[
          (strategy.equity_curve || []).map(v => v * 0.8), 
          strategy.equity_curve || [], 
          (strategy.equity_curve || []).map(v => v * 1.2)
        ]} />
      </div>

      {/* Trade Log Table */}
      {strategy.trade_log && strategy.trade_log.length > 0 && (
        <div className={styles.tableCard} style={{ marginBottom: '1.5rem' }}>
          <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <History size={18} className="text-cyan" />
              <h3 className={styles.tableTitle} style={{ margin: 0 }}>Trade Execution History</h3>
              <Badge variant="info">{strategy.trade_log.length} trades totales</Badge>
            </div>
            
            <div className="flex items-center gap-1.5 p-1 rounded-md" style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
              <button
                type="button"
                onClick={() => setTradeFilter('latest50')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: tradeFilter === 'latest50' ? 'rgba(0, 212, 255, 0.15)' : 'transparent',
                  color: tradeFilter === 'latest50' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                  border: tradeFilter === 'latest50' ? '1px solid var(--color-accent-cyan)' : '1px solid transparent'
                }}
              >
                Últimos 50 Trades (Recientes)
              </button>
              <button
                type="button"
                onClick={() => setTradeFilter('first50')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: tradeFilter === 'first50' ? 'rgba(0, 212, 255, 0.15)' : 'transparent',
                  color: tradeFilter === 'first50' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                  border: tradeFilter === 'first50' ? '1px solid var(--color-accent-cyan)' : '1px solid transparent'
                }}
              >
                Primeros 50 Trades
              </button>
              {strategy.trade_log.length > 50 && (
                <button
                  type="button"
                  onClick={() => setTradeFilter('all')}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    background: tradeFilter === 'all' ? 'rgba(0, 212, 255, 0.15)' : 'transparent',
                    color: tradeFilter === 'all' ? 'var(--color-accent-cyan)' : 'var(--color-text-muted)',
                    border: tradeFilter === 'all' ? '1px solid var(--color-accent-cyan)' : '1px solid transparent'
                  }}
                >
                  Ver Todos ({strategy.trade_log.length})
                </button>
              )}
            </div>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.5rem' }}># Trade</th>
                  <th style={{ padding: '0.5rem' }}>Tipo</th>
                  <th style={{ padding: '0.5rem' }}>Fecha Entrada</th>
                  <th style={{ padding: '0.5rem' }}>Fecha Salida</th>
                  <th style={{ padding: '0.5rem' }}>Precio Entrada</th>
                  <th style={{ padding: '0.5rem' }}>Stop Loss (SL)</th>
                  <th style={{ padding: '0.5rem' }}>Take Profit (TP)</th>
                  <th style={{ padding: '0.5rem' }}>Precio Salida</th>
                  <th style={{ padding: '0.5rem' }}>Lotaje</th>
                  <th style={{ padding: '0.5rem' }}>Beneficio / Pérdida</th>
                  <th style={{ padding: '0.5rem' }}>Motivo de Salida</th>
                  <th style={{ padding: '0.5rem' }}>Velas</th>
                </tr>
              </thead>
              <tbody>
                {displayedTrades.map((t, idx) => {
                  const isProfit = (t.pnl || 0) >= 0;
                  const tradeNum = t.trade_idx || (tradeFilter === 'latest50' ? (strategy.trade_log.length - idx) : idx + 1);
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '0.5rem', color: 'var(--color-accent-cyan)', fontWeight: 600 }}>#{tradeNum}</td>
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
                      <td style={{ padding: '0.5rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
                        {t.entry_time ? t.entry_time.slice(0, 16) : '-'}
                      </td>
                      <td style={{ padding: '0.5rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
                        {t.exit_time ? t.exit_time.slice(0, 16) : '-'}
                      </td>
                      <td style={{ padding: '0.5rem' }}>{t.entry_price}</td>
                      <td style={{ padding: '0.5rem', color: t.sl_price ? 'var(--color-accent-rose)' : 'var(--color-text-muted)' }}>
                        {t.sl_price ? t.sl_price : '-'}
                      </td>
                      <td style={{ padding: '0.5rem', color: t.tp_price ? 'var(--color-accent-emerald)' : 'var(--color-text-muted)' }}>
                        {t.tp_price ? t.tp_price : '-'}
                      </td>
                      <td style={{ padding: '0.5rem' }}>{t.exit_price}</td>
                      <td style={{ padding: '0.5rem' }}>{t.size || 0.1}</td>
                      <td style={{ padding: '0.5rem', fontWeight: 600, color: isProfit ? 'var(--color-accent-emerald)' : 'var(--color-accent-rose)' }}>
                        {isProfit ? `+${formatCurrency(t.pnl)}` : formatCurrency(t.pnl)}
                      </td>
                      <td style={{ padding: '0.5rem' }}>
                        <span style={{
                          fontSize: '0.6875rem',
                          textTransform: 'uppercase',
                          padding: '0.125rem 0.375rem',
                          borderRadius: '4px',
                          background: t.exit_reason === 'tp' ? 'rgba(16, 185, 129, 0.15)' : (t.exit_reason === 'sl' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(255, 255, 255, 0.05)'),
                          color: t.exit_reason === 'tp' ? 'var(--color-accent-emerald)' : (t.exit_reason === 'sl' ? 'var(--color-accent-rose)' : 'var(--color-text-muted)'),
                          fontWeight: 600
                        }}>
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

      {/* Code & Model Export Section */}
      <div className={styles.tableCard}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <FileCode size={20} className="text-cyan" />
            <h3 className={styles.tableTitle} style={{ margin: 0 }}>
              {isRLStrategy ? 'Export Neural Model & Execution Scripts' : 'Export Executable Strategy Code'}
            </h3>
          </div>
          <button 
            type="button" 
            onClick={() => setShowInstructions(!showInstructions)} 
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--color-accent-cyan)',
              fontSize: '0.8125rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            <HelpCircle size={16} />
            <span>{showInstructions ? 'Hide Setup Guide' : 'How to install in MT5'}</span>
            {showInstructions ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {/* Step-by-Step MT5 & ONNX Installation Guide */}
        {showInstructions && (
          <div style={{
            background: 'rgba(0, 212, 255, 0.03)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            borderRadius: '8px',
            padding: '1.25rem',
            marginBottom: '1.25rem',
            fontSize: '0.875rem'
          }}>
            <h4 style={{ color: 'var(--color-accent-cyan)', fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FolderCheck size={18} />
              Step-by-Step Setup in MetaTrader 5
            </h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', color: 'var(--color-text-main)' }}>
              <div style={{ background: 'var(--color-bg-card)', padding: '0.875rem', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-accent-cyan)', marginBottom: '0.25rem' }}>
                  1. Place the ONNX Model (If Deep RL)
                </div>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', margin: 0 }}>
                  Click <b>Download Model (.onnx)</b> and save it in your MT5 files folder:
                  <br />
                  <code style={{ color: 'var(--color-accent-amber)', fontSize: '0.75rem', background: 'rgba(0,0,0,0.3)', padding: '0.125rem 0.25rem', borderRadius: '4px' }}>
                    MT5 Menu ➔ File ➔ Open Data Folder ➔ MQL5/Files/
                  </code>
                  <br />
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                    💡 <i>Para el Strategy Tester (Probador)</i>: También puedes colocarlo en <b>File ➔ Open Common Data Folder ➔ Files/</b> para acceso global en todos los agentes (Core 1, Core 2, etc.).
                  </span>
                </p>
              </div>

              <div style={{ background: 'var(--color-bg-card)', padding: '0.875rem', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-accent-cyan)', marginBottom: '0.25rem' }}>
                  2. Save & Compile the EA in MetaEditor
                </div>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', margin: 0 }}>
                  Click <b>Download .mq5</b> and place it in <code style={{ color: 'var(--color-accent-amber)', fontSize: '0.75rem' }}>MQL5/Experts/</code>. Open <b>MetaEditor</b> (press F4 in MT5), open the file and press <b>Compile (F7)</b>.
                </p>
              </div>

              <div style={{ background: 'var(--color-bg-card)', padding: '0.875rem', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-accent-cyan)', marginBottom: '0.25rem' }}>
                  3. Enable Algo Trading & Permissions
                </div>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', margin: 0 }}>
                  In MT5: <b>Tools ➔ Options ➔ Expert Advisors</b>. Check:
                  <br />
                  <span style={{ color: 'var(--color-accent-emerald)' }}>✓ Allow Algorithmic Trading</span> and <span style={{ color: 'var(--color-accent-emerald)' }}>✓ Allow DLL / Model imports</span>.
                </p>
              </div>

              <div style={{ background: 'var(--color-bg-card)', padding: '0.875rem', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-accent-cyan)', marginBottom: '0.25rem' }}>
                  4. Attach to Chart or Strategy Tester
                </div>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', margin: 0 }}>
                  Drag the Expert Advisor from Navigator onto any chart or open the <b>Strategy Tester (Ctrl+R)</b> to run tick-by-tick neural backtests!
                </p>
              </div>
            </div>
          </div>
        )}

        <div className={styles.codeTabs}>
          <button 
            className={`${styles.codeTab} ${activeTab === 'mt5' ? styles.codeTabActive : ''}`} 
            onClick={() => setActiveTab('mt5')}
          >
            {isRLStrategy ? 'MetaTrader 5 (MQL5 + ONNX EA)' : 'MetaTrader 5 (MQL5 EA)'}
          </button>
          <button 
            className={`${styles.codeTab} ${activeTab === 'pine' ? styles.codeTabActive : ''}`} 
            onClick={() => setActiveTab('pine')}
          >
            TradingView Pine Script v6
          </button>
          <button 
            className={`${styles.codeTab} ${activeTab === 'python' ? styles.codeTabActive : ''}`} 
            onClick={() => setActiveTab('python')}
          >
            Python Live Trader (MT5 API)
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
            {isRLStrategy && (
              <Button 
                size="sm" 
                variant="secondary" 
                className="flex items-center gap-1" 
                onClick={handleDownloadOnnx}
                isLoading={downloadingOnnx}
              >
                <Cpu size={14} className="text-cyan" />
                <span>Download Model (.onnx)</span>
              </Button>
            )}
            <Button size="sm" variant="secondary" className="flex items-center gap-1" onClick={handleCopy}>
              {copied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </Button>
            <Button size="sm" variant="primary" className="flex items-center gap-1" onClick={handleDownloadCode}>
              <Download size={14} />
              <span>Download .{activeTab === 'mt5' ? 'mq5' : (activeTab === 'pine' ? 'pine' : 'py')}</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyDetail;
