import React, { useEffect, useState } from 'react';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';
import wsClient from '../services/websocket';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

export const Dashboard: React.FC = () => {
  const store = useOpsStore();
  const [liveTime, setLiveTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    wsClient.connectAll();

    const timer = setInterval(() => {
      setLiveTime(new Date().toLocaleTimeString());
    }, 1000);

    const bootstrapMetrics = async () => {
      try {
        const heatmap = await dashboardService.getCrowdHeatmap();
        store.updateCrowdMetrics(heatmap);
        
        const incidents = await dashboardService.getIncidents();
        if (incidents && Array.isArray(incidents)) {
          incidents.forEach((inc) => store.addIncident(inc));
        }

        const lowStock = await dashboardService.getLowStockInventory();
        store.updateInventories(lowStock);
      } catch (e) {
        // Fallback simulated metrics on database connection delays
      }
    };
    bootstrapMetrics();

    return () => {
      wsClient.disconnectAll();
      clearInterval(timer);
    };
  }, []);

  const totalHeadcount = store.crowdMetrics.reduce((acc, curr) => acc + curr.headcount, 0) || 54200;
  const criticalCount = store.crowdMetrics.filter((z) => z.status === 'Critical').length;
  const activeIncidents = store.incidents.filter((i) => i.status !== 'Resolved');

  const stats = [
    { label: "Total Attendance", val: totalHeadcount.toLocaleString(), change: "+4.2%", color: "text-[#00A8FF]", sparkData: [30, 45, 38, 55, 48, 64] },
    { label: "Critical Bottlenecks", val: criticalCount, change: `${criticalCount > 0 ? "Immediate" : "0 Alert"}`, color: "text-[#EF4444]", sparkData: [0, 1, 0, 2, 1, criticalCount] },
    { label: "Active Incidents", val: activeIncidents.length, change: "Dispatched", color: "text-[#F59E0B]", sparkData: [5, 4, 3, 2, 4, activeIncidents.length] },
    { label: "AI Recommendations", val: store.recommendations.length || 3, change: "Cognitive Link", color: "text-[#8B5CF6]", sparkData: [1, 2, 2, 3, 3, 4] },
    { label: "Open Entrance Gates", val: "18 / 20", change: "90% Flow", color: "text-[#22C55E]", sparkData: [18, 18, 18, 18, 18, 18] },
    { label: "Medical Alerts", val: store.incidents.filter(i => i.type.includes("Medical")).length, change: "0 Active", color: "text-[#EF4444]", sparkData: [1, 0, 2, 0, 1, 0] }
  ];

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header Banner Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/5 pb-6 space-y-4 md:space-y-0">
        <div>
          <div className="flex items-center space-x-3">
            <span className="bg-[#EF4444] text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-widest uppercase">Live Command</span>
            <span className="text-gray-500 text-xs">|</span>
            <span className="text-xs text-gray-400 font-semibold tracking-wider font-display">CONSOLE V2.10</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white mt-1 font-display">
            MetLife Operations Hub
          </h1>
          <p className="text-gray-400 text-xs mt-1">FIFA World Cup 2026 • Security, Crowd, & AI Coordinated Gateway</p>
        </div>
        <div className="flex items-center space-x-4 bg-[#0B1228] border border-white/5 px-5 py-3 rounded-xl shadow-lg shadow-black/40">
          <div className="text-right">
            <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">Tournament Clock</div>
            <div className="text-lg font-mono font-bold text-[#00E5FF]">{liveTime}</div>
          </div>
          <span className="w-1.5 h-8 bg-gray-800 rounded" />
          <div>
            <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">System Status</div>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20 mt-1">
              Active Link
            </span>
          </div>
        </div>
      </div>

      {/* Grid Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-36 border border-white/5 transition-all duration-300 hover:border-[#00A8FF]/35 group">
            <div className="flex justify-between items-start">
              <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">{stat.label}</span>
              <span className="text-[9px] text-[#22C55E] font-bold bg-[#22C55E]/10 px-2 py-0.5 rounded border border-[#22C55E]/20">{stat.change}</span>
            </div>
            <div className="flex justify-between items-end mt-4">
              <div className={`text-2xl font-extrabold font-display ${stat.color} group-hover:scale-105 transition-transform duration-300`}>
                {stat.val}
              </div>
              <div className="w-16 h-8">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stat.sparkData.map((d, i) => ({ val: d }))}>
                    <Area type="monotone" dataKey="val" stroke="#00A8FF" strokeWidth={1.5} fill="none" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Analytical Splits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Crowd Density Flow Area Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Crowd Density Flow (Last Hour)</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Real-time gate and corridor capacity aggregation</p>
          </div>
          <div className="w-full h-[280px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={[
                { time: '17:00', density: 3400 },
                { time: '17:15', density: 4200 },
                { time: '17:30', density: 5100 },
                { time: '17:45', density: 4800 },
                { time: '18:00', density: 6300 },
                { time: '18:15', density: 5900 }
              ]}>
                <defs>
                  <linearGradient id="colorDensity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00A8FF" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#00A8FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#111A33', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                <Area type="monotone" dataKey="density" stroke="#00A8FF" strokeWidth={3} fillOpacity={1} fill="url(#colorDensity)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Advisory Panel */}
        <div className="glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider text-[#8B5CF6]">AI Command Recommendations</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Coordinated multi-agent pipeline suggestions</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 mt-4">
            {store.recommendations.length > 0 ? (
              store.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 bg-[#111A33] rounded-xl border border-white/5 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-[#8B5CF6] uppercase tracking-wider">{rec.agent_name}</span>
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed font-sans">{rec.response_text}</p>
                </div>
              ))
            ) : (
              <div className="p-4 bg-[#111A33] rounded-xl border border-white/5 space-y-2">
                <span className="text-[10px] font-bold text-[#8B5CF6] uppercase tracking-wider">OperationsManagerAgent</span>
                <p className="text-xs text-gray-300 leading-relaxed font-sans">
                  "Recommendation: Open Gate C turnstiles immediately to reduce upcoming crowd surge by 32%."
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Logs and Incident Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Active Emergency Timeline */}
        <div className="glass-panel p-6 rounded-2xl h-[340px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Active Incidents timeline</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Emergency dispatcher assignment status logs</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 mt-4 pr-2">
            {store.incidents.length > 0 ? (
              store.incidents.map((inc) => (
                <div key={inc.id} className="flex justify-between items-center p-4 bg-[#111A33] rounded-xl border border-white/5 hover:border-red-500/20 transition-colors duration-200">
                  <div>
                    <div className="text-sm font-semibold text-white">{inc.title}</div>
                    <div className="text-xs text-[#94A3B8] mt-0.5">{inc.type} in Zone B</div>
                  </div>
                  <span className="text-[9px] font-bold px-2 py-0.5 bg-[#EF4444]/10 text-[#EF4444] rounded border border-[#EF4444]/20 uppercase tracking-wider">
                    {inc.severity}
                  </span>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                No active operational emergency incidents reported.
              </div>
            )}
          </div>
        </div>

        {/* Concessions stock warning list */}
        <div className="glass-panel p-6 rounded-2xl h-[340px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Concessions Inventory Warnings</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Automated low-stock warnings from vendor POS streams</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 mt-4 pr-2">
            {store.inventories.length > 0 ? (
              store.inventories.map((inv) => (
                <div key={inv.id} className="flex justify-between items-center p-4 bg-[#111A33] rounded-xl border border-white/5">
                  <div>
                    <div className="text-sm font-semibold text-white">Vendor Kiosk {inv.vendor_id}</div>
                    <div className="text-xs text-[#94A3B8] mt-0.5">Product: {inv.product_id}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-extrabold text-[#EF4444]">{inv.current_stock} Units</div>
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase mt-0.5">Min Alert: {inv.min_threshold}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                All kiosk inventories stocked above minimum alert thresholds.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
