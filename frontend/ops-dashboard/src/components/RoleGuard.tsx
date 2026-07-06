import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ allowedRoles, children }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRoles = user.roles.map((r) => r.name);
  
  // Allow Administrators bypass
  if (userRoles.includes('Administrator')) {
    return <>{children}</>;
  }

  const hasAccess = allowedRoles.some((role) => userRoles.includes(role));

  return hasAccess ? <>{children}</> : <Navigate to="/unauthorized" replace />;
};
