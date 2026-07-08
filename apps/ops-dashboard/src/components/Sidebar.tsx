import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const userRoles = user?.roles.map((r) => r.name) || [];

  const checkRoleAccess = (allowed: string[]) => {
    if (!user) return false;
    if (userRoles.includes('Administrator')) return true;
    if (userRoles.includes('Operations Manager')) return true;
    return allowed.some((r) => userRoles.includes(r));
  };

  const navItems = [
    { to: '/', label: 'Dashboard Hub', roles: ['Security Staff', 'Medical Staff', 'Operations Manager'] },
    { to: '/crowd', label: 'Crowd Intelligence', roles: ['Security Staff', 'Operations Manager'] },
    { to: '/ai-command', label: 'AI Command Center', roles: ['Operations Manager'] },
    { to: '/emergencies', label: 'Emergency Response', roles: ['Security Staff', 'Medical Staff', 'Operations Manager'] },
    { to: '/navigation', label: 'Smart Navigation', roles: ['Security Staff', 'Operations Manager'] },
    { to: '/vendors', label: 'Vendor Operations', roles: ['Operations Manager'] },
    { to: '/users', label: 'User Management', roles: ['Administrator'] },
    { to: '/settings', label: 'System Settings', roles: ['Administrator', 'Operations Manager'] }
  ];

  return (
    <aside className="w-[280px] min-w-[280px] bg-[#0B1228]/95 border-r border-white/5 min-h-screen text-[#F8FAFC] flex flex-col shadow-2xl relative z-20">
      {/* Brand Header */}
      <div className="p-6 border-b border-white/5 flex flex-col space-y-1.5 bg-[#050B1C]">
        <div className="flex items-center space-x-3">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00A8FF] pulse-indicator" />
          <h2 className="text-xl font-bold tracking-widest font-display text-white">STADIUMOS</h2>
        </div>
        <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-widest">Operations Console</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.filter((item) => checkRoleAccess(item.roles)).length === 0 && user && (
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center px-4 py-3.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-300 ${
                isActive
                  ? 'bg-gradient-to-r from-[#00A8FF]/10 to-transparent text-[#00A8FF] border-l-2 border-[#00A8FF]'
                  : 'text-[#94A3B8] hover:bg-[#111A33]/50 hover:text-white'
              }`
            }
          >
            Dashboard Hub
          </NavLink>
        )}
        {navItems.map(
          (item) =>
            checkRoleAccess(item.roles) && (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-to-r from-[#00A8FF]/10 to-transparent text-[#00A8FF] border-l-2 border-[#00A8FF] shadow-[inset_4px_0_12px_rgba(0,168,255,0.05)]'
                      : 'text-[#94A3B8] hover:bg-[#111A33]/50 hover:text-white'
                  }`
                }
              >
                {item.label}
              </NavLink>
            )
        )}
      </nav>

      {/* Footer Profile Segment */}
      <div className="p-5 border-t border-white/5 bg-[#050B1C]">
        <div className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Access Scope:</div>
        <div className="text-xs font-bold text-[#00E5FF] mt-1 truncate">
          {userRoles.length > 0 ? userRoles.join(' • ') : 'No Role Mapping'}
        </div>
      </div>
    </aside>
  );
};
export default Sidebar;
