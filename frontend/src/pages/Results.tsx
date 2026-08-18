import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useJob, useDeleteJob } from '../hooks/useJobs';
import { useStrategies } from '../hooks/useStrategies';
import { downloadOnnxModel } from '../services/api';
import StrategyTable from '../components/reports/StrategyTable';
import JobConfigCard from '../components/reports/JobConfigCard';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { Cpu, Trash2, AlertTriangle } from 'lucide-react';
import styles from '../styles/pages.module.css';

const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: job, isLoading: jobLoading } = useJob(id!);
  const { data: strategies, isLoading: stratLoading } = useStrategies(id!);
  const deleteJobMutation = useDeleteJob();
  const [downloadingOnnx, setDownloadingOnnx] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  if (jobLoading || stratLoading) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  const isRLEnabled = Boolean(job?.config?.rl?.enabled);

  const handleDeleteJob = async () => {
    if (!id) return;
    try {
      await deleteJobMutation.mutateAsync(id);
      navigate('/');
    } catch (err) {
      console.error('Failed to delete job:', err);
    }
  };

  const handleDownloadJobOnnx = async () => {
    if (!id) return;
    setDownloadingOnnx(true);
    try {
      const blob = await downloadOnnxModel(id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AlgoForge_Job_${id}.onnx`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("ONNX neural model file not found on server for this job.");
    } finally {
      setDownloadingOnnx(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <h2 style={{ margin: 0 }}>Results: {job?.config?.dataSource?.symbol || 'Strategy Pool'}</h2>
            {isRLEnabled && (
              <Badge variant="success">
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Cpu size={12} /> Deep RL Active
                </span>
              </Badge>
            )}
          </div>
          <p className={styles.subtitle}>
            Generated strategies ranked by composite score ({strategies?.length || 0} candidates discovered).
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {isRLEnabled && (
            <Button
              size="sm"
              variant="secondary"
              className="flex items-center gap-1"
              onClick={handleDownloadJobOnnx}
              isLoading={downloadingOnnx}
            >
              <Cpu size={14} className="text-cyan" />
              <span>Download Job Neural Model (.onnx)</span>
            </Button>
          )}

          <Button
            size="sm"
            variant="ghost"
            className="flex items-center gap-1"
            style={{ color: 'var(--color-accent-rose)' }}
            onClick={() => setShowDeleteModal(true)}
            title="Delete this job and its strategies"
          >
            <Trash2 size={14} />
            <span>Delete Job</span>
          </Button>
        </div>
      </div>

      {/* Analysis Configuration Details */}
      {job?.config && (
        <JobConfigCard config={job.config} defaultExpanded={true} />
      )}

      <div className={styles.tableCard}>
        <StrategyTable strategies={strategies || []} />
      </div>

      {/* Confirmation Modal for Deleting Job */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => !deleteJobMutation.isPending && setShowDeleteModal(false)}
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
                Job Symbol: <strong style={{ color: 'var(--color-accent-cyan)' }}>{job?.config?.dataSource?.symbol}</strong> ({job?.config?.dataSource?.timeframe}).
                <br />
                This will permanently delete the job record, training metrics, and all {strategies?.length || 0} discovered trading strategies. This action cannot be undone.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
              disabled={deleteJobMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteJob}
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

export default Results;
