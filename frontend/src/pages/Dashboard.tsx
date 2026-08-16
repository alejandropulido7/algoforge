import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Activity, CheckCircle2, Trophy, Layers, Eye, Sparkles } from 'lucide-react';
import { useJobs } from '../hooks/useJobs';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import ProgressBar from '../components/common/ProgressBar';
import Spinner from '../components/common/Spinner';
import styles from '../styles/pages.module.css';
import { useAuth } from '../hooks/useAuth';

const Dashboard: React.FC = () => {
  const { data: jobs, isLoading } = useJobs();
  const navigate = useNavigate();
  const { user } = useAuth();

  const getStatusBadge = (status: string) => {
    const map: Record<string, 'success'|'warning'|'error'|'info'|'neutral'> = {
      completed: 'success',
      running: 'info',
      failed: 'error',
      pending: 'warning'
    };
    return <Badge variant={map[status] || 'neutral'}>{status}</Badge>;
  };

  if (isLoading) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  const completedJobs = jobs?.filter(j => j.status === 'completed') || [];
  const totalJobs = jobs?.length || 0;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <h2>Welcome back, {user?.email?.split('@')[0]}</h2>
          <p className={styles.subtitle}>Here is an overview of your AI-generated trading strategies.</p>
        </div>
        <Button onClick={() => navigate('/new')} variant="primary" className="flex items-center gap-2">
          <Plus size={18} />
          <span>New Strategy</span>
        </Button>
      </div>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{color: 'var(--color-accent-cyan)'}}>
            <Activity size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Total Jobs</span>
            <span className={styles.statValue}>{totalJobs}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{color: 'var(--color-accent-emerald)'}}>
            <CheckCircle2 size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Completed</span>
            <span className={styles.statValue}>{completedJobs.length}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{color: 'var(--color-accent-amber)'}}>
            <Trophy size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Best Score</span>
            <span className={styles.statValue}>-</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{color: 'var(--color-text-secondary)'}}>
            <Layers size={24} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Total Strategies</span>
            <span className={styles.statValue}>-</span>
          </div>
        </div>
      </div>

      <div className={styles.tableCard}>
        <h3 className={styles.tableTitle}>Recent Jobs</h3>
        {totalJobs === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyStateIcon}>
              <Sparkles size={48} className="text-secondary" strokeWidth={1.5} />
            </div>
            <h4>No generation jobs yet</h4>
            <p>Start discovering automated MT5 strategies using Genetic Programming and Reinforcement Learning.</p>
            <Button onClick={() => navigate('/new')} variant="primary" className="mt-4 flex items-center gap-2">
              <Plus size={16} />
              <span>Create First Strategy</span>
            </Button>
          </div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs?.map(job => (
                  <tr key={job.id} onClick={() => navigate(`/jobs/${job.id}/progress`)} className={styles.tableRowClickable}>
                    <td>
                      <div className={styles.jobSymbol}>{job.config.dataSource.symbol}</div>
                      <div className={styles.jobTimeframe}>{job.config.dataSource.timeframe}</div>
                    </td>
                    <td>{getStatusBadge(job.status)}</td>
                    <td>
                      <div style={{width: '120px'}}>
                        <ProgressBar percentage={job.progress} phase={job.current_phase} />
                      </div>
                    </td>
                    <td>{new Date(job.created_at).toLocaleDateString()}</td>
                    <td>
                      <Button 
                        size="sm" 
                        variant="ghost" 
                        onClick={(e) => { e.stopPropagation(); navigate(`/jobs/${job.id}/results`); }}
                        className="flex items-center gap-1"
                      >
                        <Eye size={14} />
                        <span>View</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
