import { useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';
import type { JobPhase, JobStatus } from '../types/job';

export const useRealtimeJob = (jobId: string) => {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState<JobPhase>('queued');
  const [status, setStatus] = useState<JobStatus>('pending');

  useEffect(() => {
    if (!jobId) return;

    const fetchInitial = async () => {
      const { data, error } = await supabase
        .from('jobs')
        .select('progress, current_phase, status')
        .eq('id', jobId)
        .single();

      if (data && !error) {
        setProgress(data.progress);
        setPhase(data.current_phase as JobPhase);
        setStatus(data.status as JobStatus);
      }
    };
    fetchInitial();

    const channel = supabase
      .channel(`job_${jobId}`)
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'jobs', filter: `id=eq.${jobId}` },
        (payload) => {
          if (payload.new.progress !== undefined) setProgress(payload.new.progress);
          if (payload.new.current_phase !== undefined) setPhase(payload.new.current_phase as JobPhase);
          if (payload.new.status !== undefined) setStatus(payload.new.status as JobStatus);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [jobId]);

  return { progress, phase, status };
};
