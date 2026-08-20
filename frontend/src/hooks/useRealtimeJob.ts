import { useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';
import { getJob } from '../services/api';
import type { JobPhase, JobStatus } from '../types/job';

export interface RealtimeJobState {
  progress: number;
  phase: JobPhase;
  status: JobStatus;
  subProgress: number;
  subCurrent: number;
  subTotal: number;
  validCandidates: number;
  liveMessage: string;
  createdAt: string;
}

export const useRealtimeJob = (jobId: string): RealtimeJobState => {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState<JobPhase>('queued');
  const [status, setStatus] = useState<JobStatus>('pending');
  const [subProgress, setSubProgress] = useState(0);
  const [subCurrent, setSubCurrent] = useState(0);
  const [subTotal, setSubTotal] = useState(0);
  const [validCandidates, setValidCandidates] = useState(0);
  const [liveMessage, setLiveMessage] = useState('');
  const [createdAt, setCreatedAt] = useState('');

  useEffect(() => {
    if (!jobId) return;

    let isMounted = true;

    const fetchStatus = async () => {
      try {
        const job = await getJob(jobId);
        if (!isMounted || !job) return;

        if (job.progress !== undefined) setProgress(job.progress);
        if (job.current_phase !== undefined) setPhase(job.current_phase as JobPhase);
        if (job.status !== undefined) setStatus(job.status as JobStatus);
        if (job.created_at) setCreatedAt(job.created_at);

        const anyJob = job as unknown as Record<string, unknown>;
        if (typeof anyJob.sub_progress === 'number') setSubProgress(anyJob.sub_progress);
        if (typeof anyJob.sub_current === 'number') setSubCurrent(anyJob.sub_current);
        if (typeof anyJob.sub_total === 'number') setSubTotal(anyJob.sub_total);
        if (typeof anyJob.valid_candidates === 'number') setValidCandidates(anyJob.valid_candidates);
        if (typeof anyJob.live_message === 'string') setLiveMessage(anyJob.live_message);
      } catch (err) {
        // Silent catch for polling
      }
    };

    fetchStatus();

    // Fast polling interval (1000ms) for ultra-responsive live sub-progress ticks
    const interval = setInterval(() => {
      fetchStatus();
    }, 1000);

    const channel = supabase
      .channel(`job_${jobId}`)
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'jobs', filter: `id=eq.${jobId}` },
        (payload) => {
          if (!isMounted) return;
          if (payload.new.progress !== undefined) setProgress(payload.new.progress);
          if (payload.new.current_phase !== undefined) setPhase(payload.new.current_phase as JobPhase);
          if (payload.new.status !== undefined) setStatus(payload.new.status as JobStatus);
          if (payload.new.created_at) setCreatedAt(payload.new.created_at);
        }
      )
      .subscribe();

    return () => {
      isMounted = false;
      clearInterval(interval);
      supabase.removeChannel(channel);
    };
  }, [jobId]);

  return {
    progress,
    phase,
    status,
    subProgress,
    subCurrent,
    subTotal,
    validCandidates,
    liveMessage,
    createdAt
  };
};
