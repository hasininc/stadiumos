import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const userRoles = user?.roles.map((r) => r.name) || [];

  const checkRoleAccess = (allowed: string[]) => {
    if (userRoles.includes('Administrator')) return true;
    return allowed.some((r) => userRoles.includes(r));
  };

  const navItems = [
    { to: '/', label: 'Overview', roles: ['Security Staff', 'Medical Staff', 'Operations Manager'] },
    { to: '/crowd', label: 'Crowd Dynamics', roles: ['Security Staff', 'Operations Manager'] },
    { to: '/incidents', label: 'Incidents Center', roles: ['Security Staff', 'Medical Staff', 'Operations Manager'] },
    { to: '/vendors', label: 'Vendor Operations', roles: ['Operations Manager'] },
    { to: '/ai-advisory', label: 'AI Advisory', roles: ['Operations Manager'] }
  ];

  return (
    <aside className="w-64 bg-[#11141A] border-r border-[#1E232F] min-h-screen text-white flex flex-col">
      <div className="p-6 border-b border-[#1E232F]">
        <h2 className="text-xl font-bold text-[#00E676] tracking-wider font-display">StadiumOS</h2>
        <span className="text-xs text-gray-500 font-semibold uppercase">Command Console</span>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map(
          (item) =>
            checkRoleAccess(item.roles) && (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-[#00E676] text-black shadow-lg shadow-[#00E676]/20'
                      : 'text-gray-400 hover:bg-[#1E232F] hover:text-white'
                  }`
                }
              >
                {item.label}
              </NavLink>
            )
        )}
      </nav>

      <div className="p-4 border-t border-[#1E232F] bg-[#0E1015]">
        <div className="text-xs text-gray-400">Authenticated Role:</div>
        <div className="text-sm font-semibold text-[#2979FF] truncate">
          {userRoles.length > 0 ? userRoles.join(', ') : 'None'}
        </div>
      </div>
    </aside>
  );
};
export default Sidebar;
