import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Rocket, ArrowLeft, ArrowRight } from 'lucide-react';
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

  const handleRun = async () => {
    try {
      const job = await createJob.mutateAsync(config);
      navigate(`/jobs/${job.id}/progress`);
    } catch (err) {
      console.error(err);
      alert('Failed to start job. See console.');
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

      <div className={styles.wizardContent}>
        {renderStep()}
      </div>

      <div className={styles.wizardFooter}>
        <Button 
          variant="secondary" 
          onClick={prevStep} 
          disabled={currentStep === 1}
        >
          <ArrowLeft size={16} className="mr-1" />
          Back
        </Button>
        
        {currentStep < 5 ? (
          <Button variant="primary" onClick={nextStep}>
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
