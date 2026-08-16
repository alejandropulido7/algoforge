import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuth = () => {
  const { user, session, isLoading, error, initialize, signIn, signUp, signOut } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  return { user, session, isLoading, error, signIn, signUp, signOut };
};
