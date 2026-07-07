import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';

export const App: React.FC = () => {
  return (
    <Routes>
      {/* Auth Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Dashboard Command Console */}
      <Route element={<ProtectedRoute />}>
        <Route
          path="/*"
          element={
            <div className="flex bg-[#0C0E12] min-h-screen">
              <Sidebar />
              <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
                <Topbar />
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </div>
            </div>
          }
        />
      </Route>
    </Routes>
  );
};
export default App;
