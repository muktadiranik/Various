// src/App.jsx
import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import MainLayout from './components/layout/MainLayout';
import { checkAuth } from './store/slices/authSlice';

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, loading } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(checkAuth());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#36393f]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#5865f2]"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />
      <Route path="/*" element={isAuthenticated ? <MainLayout /> : <Navigate to="/login" />} />
    </Routes>
  );
}

export default App;