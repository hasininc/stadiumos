import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { AIChatBot } from './components/AIChatBot';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { CrowdMonitoring } from './pages/CrowdMonitoring';
import { AICommandCenter } from './pages/AICommandCenter';
import { EmergencyManagement } from './pages/EmergencyManagement';
import { Navigation } from './pages/Navigation';
import { VendorAnalytics } from './pages/VendorAnalytics';
import { UserManagement } from './pages/UserManagement';
import { Settings } from './pages/Settings';

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
            <div className="flex bg-[#050B1C] h-screen w-screen overflow-hidden text-[#F8FAFC]">
              <Sidebar />
              <div className="flex-1 flex flex-col h-full overflow-hidden">
                <Topbar />
                <main className="flex-1 overflow-y-auto">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/crowd" element={<CrowdMonitoring />} />
                    <Route path="/ai-command" element={<AICommandCenter />} />
                    <Route path="/emergencies" element={<EmergencyManagement />} />
                    <Route path="/navigation" element={<Navigation />} />
                    <Route path="/vendors" element={<VendorAnalytics />} />
                    <Route path="/users" element={<UserManagement />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </main>
              </div>
              {/* Floating AI Agent Companion */}
              <AIChatBot />
            </div>
          }
        />
      </Route>
    </Routes>
  );
};
export default App;
