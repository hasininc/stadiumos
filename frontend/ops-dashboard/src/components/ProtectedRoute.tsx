import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute: React.FC = () => {
  const { accessToken, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0C0E12', color: '#fff' }}>
        <h3>Verifying Session...</h3>
      </div>
    );
  }

  return accessToken ? <Outlet /> : <Navigate to="/login" replace />;
};
