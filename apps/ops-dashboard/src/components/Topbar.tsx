import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();
  const wsConnected = useOpsStore((state) => state.wsConnected);
  const crowdMetrics = useOpsStore((state) => state.crowdMetrics);
  const incidents = useOpsStore((state) => state.incidents);
  const [stadiumName, setStadiumName] = useState('Stadium Operations');

  useEffect(() => {
    dashboardService.getCrowdZones().then((zones: { stadium_id?: string }[]) => {
      if (zones.length > 0) setStadiumName('Live Stadium Console');
    }).catch(() => {});
  }, []);

  const totalHeadcount = crowdMetrics.reduce((sum, z) => sum + z.headcount, 0);
  const criticalZones = crowdMetrics.filter((z) => z.status === 'Critical').length;
  const activeIncidents = incidents.filter((i) => i.status !== 'Resolved').length;

  return (
    <header className="h-20 bg-[#0B1228] border-b border-white/5 text-[#F8FAFC] flex items-center justify-between px-8 z-10 shadow-md">
      <div className="flex items-center space-x-3.5">
        <div className="w-8 h-8 rounded-lg bg-[#00A8FF]/10 border border-[#00A8FF]/20 flex items-center justify-center font-bold text-[#00A8FF]">
          S
        </div>
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide uppercase font-display">{stadiumName}</h3>
          <span className="text-[10px] text-[#94A3B8] font-semibold uppercase tracking-wider">
            {crowdMetrics.length} zones · {totalHeadcount.toLocaleString()} attendees
          </span>
        </div>
      </div>

      <div className="hidden md:flex items-center space-x-4 bg-[#111A33] border border-white/5 px-6 py-2.5 rounded-full">
        <span className={`w-2 h-2 rounded-full ${criticalZones > 0 ? 'bg-red-500 pulse-indicator' : 'bg-[#22C55E]'}`} />
        <div className="text-xs font-mono font-bold tracking-widest text-[#F8FAFC]">
          {criticalZones > 0 ? `${criticalZones} CRITICAL ZONE${criticalZones > 1 ? 'S' : ''}` : 'ALL ZONES NORMAL'}
        </div>
        <span className="w-px h-3 bg-white/10" />
        <div className="text-xs font-bold text-[#F59E0B]">{activeIncidents} ACTIVE INCIDENTS</div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-[#22C55E]' : 'bg-[#EF4444]'}`} />
          <span className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">
            {wsConnected ? 'Live Feed' : 'Offline'}
          </span>
        </div>

        <div className="flex items-center space-x-3.5">
          <div className="text-right">
            <div className="text-xs font-bold text-white">{user?.email}</div>
            <div className="text-[9px] text-[#94A3B8] font-semibold uppercase">
              {user?.roles.map((r) => r.name).join(', ') || 'No role'}
            </div>
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
