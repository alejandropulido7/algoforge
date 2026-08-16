import React from 'react';
import { useParams } from 'react-router-dom';
import { useJob } from '../hooks/useJobs';
import { useStrategies } from '../hooks/useStrategies';
import StrategyTable from '../components/reports/StrategyTable';
import Spinner from '../components/common/Spinner';
import styles from '../styles/pages.module.css';

const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: job, isLoading: jobLoading } = useJob(id!);
  const { data: strategies, isLoading: stratLoading } = useStrategies(id!);

  if (jobLoading || stratLoading) {
    return <div className={styles.loadingContainer}><Spinner size="lg" /></div>;
  }

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageHeader}>
        <div>
          <h2>Results: {job?.config.dataSource.symbol}</h2>
          <p className={styles.subtitle}>Generated strategies ranked by total score.</p>
        </div>
      </div>

      <div className={styles.tableCard}>
        <StrategyTable strategies={strategies || []} />
      </div>
    </div>
  );
};

export default Results;
