import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';
import { Clock, Bell, ShieldAlert, Cpu } from 'lucide-react';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const wsConnected = useOpsStore((state) => state.wsConnected);
  const crowdMetrics = useOpsStore((state) => state.crowdMetrics);
  const incidents = useOpsStore((state) => state.incidents);
  const [stadiumName, setStadiumName] = useState('Lusail Stadium');
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    dashboardService.getCrowdZones().then((zones: { stadium_id?: string }[]) => {
      if (zones.length > 0) setStadiumName('Lusail Stadium');
    }).catch(() => {});
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const date = new Date();
      setCurrentTime(date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const totalHeadcount = crowdMetrics.reduce((sum, z) => sum + z.headcount, 0);
  const criticalZones = crowdMetrics.filter((z) => z.status === 'Critical').length;
  const activeIncidents = incidents.filter((i) => i.status !== 'Resolved').length;
  const userRoles = user?.roles.map((r) => r.name) || [];

  return (
    <header className="h-20 bg-[#0B1228] border-b border-white/5 text-[#F8FAFC] flex items-center justify-between px-8 z-10 shadow-md">
      <div className="flex items-center space-x-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#00A8FF]/20 to-[#00E5FF]/20 border border-[#00A8FF]/30 flex items-center justify-center font-bold text-lg shadow-lg">
          🏆
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-sm font-extrabold text-white tracking-wider uppercase font-display">Argentina vs France</h3>
            <span className="px-2 py-0.5 text-[9px] font-bold bg-red-500/20 text-[#FF5A5A] rounded border border-red-500/30 uppercase tracking-widest animate-pulse">Live Match</span>
          </div>
          <span className="text-[10px] text-[#94A3B8] font-semibold tracking-wider uppercase">
            {stadiumName} · Lusail, Qatar · Round of 16
          </span>
        </div>
      </div>

      <div className="hidden lg:flex items-center space-x-6 bg-white/[0.02] border border-white/5 px-6 py-2.5 rounded-full backdrop-blur-md">
        <div className="flex items-center space-x-2 text-[#94A3B8]">
          <Clock className="w-3.5 h-3.5 text-[#00E5FF]" />
          <span className="text-xs font-mono font-bold tracking-wider text-white">{currentTime}</span>
        </div>
        <span className="w-px h-3.5 bg-white/10" />
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-[#22C55E] pulse-indicator" />
          <span className="text-[10px] font-bold tracking-widest text-[#22C55E] uppercase font-mono">AI Scanner: ACTIVE</span>
        </div>
        <span className="w-px h-3.5 bg-white/10" />
        <div className="text-[10px] font-bold text-[#F59E0B] flex items-center space-x-1.5">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>{activeIncidents} ACTIVE INCIDENTS</span>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <button className="relative w-9 h-9 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/5 flex items-center justify-center text-white transition-all duration-300">
          <Bell className="w-4 h-4" />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#EF4444] rounded-full text-[9px] font-bold flex items-center justify-center shadow-lg text-white">4</span>
        </button>

        <div className="flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-[#22C55E]' : 'bg-[#EF4444]'}`} />
          <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider font-mono">
            {wsConnected ? 'Telemetry Live' : 'Offline'}
          </span>
        </div>

        <div className="flex items-center space-x-3.5">
          <div className="text-right">
            <div className="text-xs font-bold text-white">{user?.email || 'operator@stadiumos.dev'}</div>
            <div className="text-[9px] text-[#00E5FF] font-semibold uppercase tracking-wider font-mono">
              {userRoles.length > 0 ? userRoles.join(' • ') : 'Ops Manager'}
            </div>
          </div>
          <button
            onClick={logout}
            className="px-3.5 py-2 border border-[#EF4444]/30 hover:bg-[#EF4444]/15 text-[#EF4444] text-[10px] font-bold tracking-wider uppercase rounded-xl transition-all duration-300"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
};
export default Topbar;

