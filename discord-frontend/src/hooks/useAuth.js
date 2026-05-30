// src/hooks/useAuth.js
import { useSelector } from 'react-redux';

function useAuth() {
  const { user, isAuthenticated, loading } = useSelector((state) => state.auth);
  
  return {
    user,
    isAuthenticated,
    loading,
    isAdmin: user?.is_admin || false,
    isBot: user?.is_bot || false,
  };
}

export default useAuth;