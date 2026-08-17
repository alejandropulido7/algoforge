import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Rocket, ArrowLeft, ArrowRight, AlertCircle } from 'lucide-react';
import { useJobStore } from '../store/jobStore';
import { useCreateJob } from '../hooks/useJobs';
import StepDataSource from '../components/configurator/StepDataSource';
import StepIndicators from '../components/configurator/StepIndicators';
import { StepRiskManagement } from '../components/configurator/StepRiskManagement';
import StepAIConfig from '../components/configurator/StepAIConfig';
import StepReview from '../components/configurator/StepReview';
import Button from '../components/common/Button';
import styles from '../styles/pages.module.css';

const STEPS = ['Data', 'Indicators', 'Risk & Sizing', 'AI Config', 'Review'];

const NewJob: React.FC = () => {
  const { currentStep, config, nextStep, prevStep } = useJobStore();
  const createJob = useCreateJob();
  const navigate = useNavigate();
  const [stepError, setStepError] = useState<string | null>(null);

  const handleNext = () => {
    setStepError(null);

    // Validation for Step 1 (Data)
    if (currentStep === 1) {
      const { symbol, startDate, endDate } = config.dataSource;
      if (!symbol || symbol.trim() === '') {
        setStepError('Please specify or select a valid trading Symbol.');
        return;
      }
      if (!startDate || !endDate) {
        setStepError('Both Start Date and End Date are mandatory.');
        return;
      }
      if (new Date(startDate) >= new Date(endDate)) {
        setStepError('End Date must be strictly after Start Date.');
        return;
      }
    }

    // Validation for Step 2 (Indicators)
    if (currentStep === 2) {
      if (!config.indicators || config.indicators.length === 0) {
        setStepError('Please select at least 1 technical indicator for the genetic evolution pool.');
        return;
      }
    }

    nextStep();
  };

  const handleRun = async () => {
    setStepError(null);
    try {
      const job = await createJob.mutateAsync(config);
      navigate(`/jobs/${job.id}/progress`);
    } catch (err) {
      console.error(err);
      setStepError('Failed to start job pipeline. Please verify server connection.');
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1: return <StepDataSource />;
      case 2: return <StepIndicators />;
      case 3: return <StepRiskManagement />;
      case 4: return <StepAIConfig />;
      case 5: return <StepReview />;
      default: return null;
    }
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.wizardHeader}>
        {STEPS.map((step, idx) => {
          const num = idx + 1;
          const isActive = currentStep === num;
          const isPast = currentStep > num;
          
          return (
            <div key={step} className={`${styles.stepIndicator} ${isActive ? styles.stepActive : ''} ${isPast ? styles.stepPast : ''}`}>
              <div className={styles.stepCircle}>
                {isPast ? <Check size={14} strokeWidth={3} /> : num}
              </div>
              <div className={styles.stepLabel}>{step}</div>
              {idx < STEPS.length - 1 && <div className={styles.stepLine} />}
            </div>
          );
        })}
      </div>

      {stepError && (
        <div style={{
          maxWidth: '780px',
          margin: '0 auto 1.25rem',
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          color: 'var(--color-accent-rose)',
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <AlertCircle size={18} />
          <span>{stepError}</span>
        </div>
      )}

      <div className={styles.wizardContent}>
        {renderStep()}
      </div>

      <div className={styles.wizardFooter}>
        <Button 
          variant="secondary" 
          onClick={() => { setStepError(null); prevStep(); }} 
          disabled={currentStep === 1}
        >
          <ArrowLeft size={16} className="mr-1" />
          Back
        </Button>
        
        {currentStep < 5 ? (
          <Button variant="primary" onClick={handleNext}>
            Next Step
            <ArrowRight size={16} className="ml-1" />
          </Button>
        ) : (
          <Button 
            variant="primary" 
            onClick={handleRun}
            isLoading={createJob.isPending}
            className={styles.runButton}
          >
            <Rocket size={16} className="mr-2" />
            Run Pipeline
          </Button>
        )}
      </div>
    </div>
  );
};

export default NewJob;
