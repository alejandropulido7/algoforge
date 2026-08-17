import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useJob } from '../hooks/useJobs';
import { useStrategies } from '../hooks/useStrategies';
import { downloadOnnxModel } from '../services/api';
import StrategyTable from '../components/reports/StrategyTable';
import JobConfigCard from '../components/reports/JobConfigCard';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { Cpu } from 'lucide-react';
import styles from '../styles/pages.module.css';

const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: job, isLoading: jobLoading } = useJob(id!);
  const { data: strategies, isLoading: stratLoading } = useStrategies(id!);
  const [downloadingOnnx, setDownloadingOnnx] = useState(false);

  if (jobLoading || stratLoading) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  const isRLEnabled = Boolean(job?.config?.rl?.enabled);

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
      </div>

      {/* Analysis Configuration Details */}
      {job?.config && (
        <JobConfigCard config={job.config} defaultExpanded={true} />
      )}

      <div className={styles.tableCard}>
        <StrategyTable strategies={strategies || []} />
      </div>
    </div>
  );
};

export default Results;
