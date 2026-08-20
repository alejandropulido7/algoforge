import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Activity, CheckCircle2, Trophy, Layers, Eye, Trash2, Sparkles, AlertTriangle } from 'lucide-react';
import { useJobs, useDeleteJob } from '../hooks/useJobs';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import ProgressBar from '../components/common/ProgressBar';
import Spinner from '../components/common/Spinner';
import Modal from '../components/common/Modal';
import styles from '../styles/pages.module.css';
import { useAuth } from '../hooks/useAuth';
import type { Job } from '../types/job';

const Dashboard: React.FC = () => {
  const { data: jobs, isLoading } = useJobs();
  const deleteJobMutation = useDeleteJob();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [jobToDelete, setJobToDelete] = useState<Job | null>(null);

  const getStatusBadge = (status: string) => {
    const map: Record<string, 'success'|'warning'|'error'|'info'|'neutral'> = {
      completed: 'success',
      running: 'info',
      failed: 'error',
      cancelled: 'error',
      pending: 'warning'
    };
    return <Badge variant={map[status] || 'neutral'}>{status.toUpperCase()}</Badge>;
  };

  const handleDeleteConfirm = async () => {
    if (!jobToDelete) return;
    try {
      await deleteJobMutation.mutateAsync(jobToDelete.id);
      setJobToDelete(null);
    } catch (err) {
      console.error('Failed to delete job:', err);
    }
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
                  <th style={{ textAlign: 'right' }}>Actions</th>
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
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          onClick={(e) => { e.stopPropagation(); navigate(`/jobs/${job.id}/results`); }}
                          className="flex items-center gap-1"
                          title="View Results"
                        >
                          <Eye size={14} />
                          <span>View</span>
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          onClick={(e) => { 
                            e.stopPropagation(); 
                            setJobToDelete(job); 
                          }}
                          className="flex items-center gap-1"
                          style={{ color: 'var(--color-accent-rose)' }}
                          title="Delete Job"
                        >
                          <Trash2 size={14} />
                          <span>Delete</span>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Confirmation Modal for Deleting Job */}
      <Modal
        isOpen={Boolean(jobToDelete)}
        onClose={() => !deleteJobMutation.isPending && setJobToDelete(null)}
        title="Delete Strategy Job"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
            <div style={{ color: 'var(--color-accent-rose)', padding: '0.25rem' }}>
              <AlertTriangle size={28} />
            </div>
            <div>
              <p style={{ margin: 0, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                Are you sure you want to delete this job?
              </p>
              <p style={{ margin: '0.5rem 0 0', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                Job Symbol: <strong style={{ color: 'var(--color-accent-cyan)' }}>{jobToDelete?.config?.dataSource?.symbol}</strong> ({jobToDelete?.config?.dataSource?.timeframe}).
                <br />
                This will permanently delete the job record, training progress, and all discovered trading strategies. This action cannot be undone.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Button
              variant="secondary"
              onClick={() => setJobToDelete(null)}
              disabled={deleteJobMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteConfirm}
              isLoading={deleteJobMutation.isPending}
              className="flex items-center gap-2"
            >
              <Trash2 size={16} />
              <span>Delete Permanently</span>
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Dashboard;
