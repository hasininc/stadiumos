import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useOpsStore } from '../store/opsStore';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const wsConnected = useOpsStore((state) => state.wsConnected);

  return (
    <header className="h-16 bg-[#11141A] border-b border-[#1E232F] text-white flex items-center justify-between px-8">
      <div className="flex items-center space-x-4">
        {/* Dynamic status socket indicators */}
        <div className="flex items-center space-x-2">
          <span className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-[#00E676] animate-pulse' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-400 font-medium">
            {wsConnected ? 'Live Stream Active' : 'Connecting Data Pipeline...'}
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="text-right">
          <div className="text-sm font-semibold">{user?.email}</div>
          <div className="text-xs text-gray-500">Operator Session</div>
        </div>

        <button
          onClick={logout}
          className="px-4 py-2 border border-red-500/30 hover:bg-red-500/10 text-red-400 text-sm font-medium rounded-lg transition-colors duration-200"
        >
          Sign Out
        </button>
      </div>
    </header>
  );
};
export default Topbar;
