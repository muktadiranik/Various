// src/components/auth/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useSelector((state) => state.auth);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#36393f]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#5865f2]"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;