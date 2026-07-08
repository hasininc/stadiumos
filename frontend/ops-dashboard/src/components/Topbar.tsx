import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useOpsStore } from '../store/opsStore';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const wsConnected = useOpsStore((state) => state.wsConnected);

  return (
    <header className="h-20 bg-[#0B1228] border-b border-white/5 text-[#F8FAFC] flex items-center justify-between px-8 z-10 shadow-md">
      {/* Left: Stadium name */}
      <div className="flex items-center space-x-3.5">
        <div className="w-8 h-8 rounded-lg bg-[#00A8FF]/10 border border-[#00A8FF]/20 flex items-center justify-center font-bold text-[#00A8FF]">
          L
        </div>
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide uppercase font-display">Lusail Stadium Operations</h3>
          <span className="text-[10px] text-[#94A3B8] font-semibold uppercase tracking-wider">Qatar Control Room</span>
        </div>
      </div>

      {/* Center: Live Match Status */}
      <div className="hidden md:flex items-center space-x-4 bg-[#111A33] border border-white/5 px-6 py-2.5 rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.2)]">
        <span className="w-2 h-2 rounded-full bg-red-500 pulse-indicator" />
        <div className="text-xs font-mono font-bold tracking-widest text-[#F8FAFC]">
          ARG <span className="text-[#00E5FF]">1</span> - <span className="text-[#00E5FF]">0</span> FRA
        </div>
        <span className="w-px h-3 bg-white/10" />
        <div className="text-xs font-bold text-[#00A8FF]">64' SECOND HALF</div>
      </div>

      {/* Right: Notifications, AI Link, Logout */}
      <div className="flex items-center space-x-6">
        {/* AI Status Indicator */}
        <div className="hidden lg:flex items-center space-x-2.5 bg-[#8B5CF6]/5 border border-[#8B5CF6]/20 px-3.5 py-1.5 rounded-xl">
          <span className="w-1.5 h-1.5 rounded-full bg-[#8B5CF6] pulse-indicator" />
          <span className="text-[10px] text-[#8B5CF6] font-bold uppercase tracking-wider">AI COGNITIVE LINK OK</span>
        </div>

        {/* WebSocket Pipeline Status */}
        <div className="flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-[#22C55E]' : 'bg-[#EF4444]'}`} />
          <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">
            {wsConnected ? 'Live Feed' : 'Offline'}
          </span>
        </div>

        {/* User Session profile */}
        <div className="flex items-center space-x-3.5">
          <div className="text-right">
            <div className="text-xs font-bold text-white">{user?.email}</div>
            <div className="text-[9px] text-[#94A3B8] font-semibold uppercase">Controller Console</div>
          </div>
          <button
            onClick={logout}
            className="px-3.5 py-2 border border-[#EF4444]/20 hover:bg-[#EF4444]/10 text-[#EF4444] text-[10px] font-bold tracking-wider uppercase rounded-xl transition-all duration-300"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
};
export default Topbar;
