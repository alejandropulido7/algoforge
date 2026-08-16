import { useQuery } from '@tanstack/react-query';
import { getStrategies, getStrategy } from '../services/api';

export const useStrategies = (jobId: string) => {
  return useQuery({
    queryKey: ['strategies', jobId],
    queryFn: () => getStrategies(jobId),
    enabled: !!jobId,
  });
};

export const useStrategy = (id: string) => {
  return useQuery({
    queryKey: ['strategy', id],
    queryFn: () => getStrategy(id),
    enabled: !!id,
  });
};
