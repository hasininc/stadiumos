import React, { useState } from 'react';
import { useOpsStore } from '../store/opsStore';
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

export const CrowdMonitoring: React.FC = () => {
  const store = useOpsStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");

  const zones = [
    { name: "North Gate A", occupancy: 92, status: "Critical", count: 1840 },
    { name: "South Gate B", occupancy: 45, status: "Safe", count: 900 },
    { name: "VIP Area", occupancy: 28, status: "Safe", count: 280 },
    { name: "Food Court East", occupancy: 78, status: "Moderate", count: 1560 },
    { name: "Parking Lot C", occupancy: 60, status: "Moderate", count: 1200 },
    { name: "Emergency Exit 4", occupancy: 12, status: "Safe", count: 120 }
  ];

  const filteredZones = zones.filter((z) => {
    const matchesSearch = z.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === "All" || z.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    if (status === "Critical") return "bg-[#EF4444]";
    if (status === "Moderate") return "bg-[#F59E0B]";
    return "bg-[#22C55E]";
  };

  const getStatusText = (status: string) => {
    if (status === "Critical") return "text-[#EF4444] border-[#EF4444]/20 bg-[#EF4444]/10";
    if (status === "Moderate") return "text-[#F59E0B] border-[#F59E0B]/20 bg-[#F59E0B]/10";
    return "text-[#22C55E] border-[#22C55E]/20 bg-[#22C55E]/10";
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Crowd Intelligence & Density</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Live zone capacity estimations and YOLOv11 edge integrations</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Average Gate Wait Time</span>
          <div className="text-xl font-extrabold text-[#00E5FF] font-display">2.4 Minutes</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Total Entrance Flow Rate</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">420 Fans / Min</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Turnstiles Ingress</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">18 / 20</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Peak Occupancy Concourse</span>
          <div className="text-xl font-extrabold text-[#EF4444] font-display">Zone East (92%)</div>
        </div>
      </div>

      {/* Visual Heatmap and graph splits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Live Heatmap visual widgets grid */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl flex flex-col justify-between h-[420px]">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Live Zone Heatmap Matrix</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Spatially mapped coordinate occupancy states</p>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-6 flex-1">
            {zones.map((z, idx) => (
              <div key={idx} className="p-4 bg-[#111A33] border border-white/5 rounded-xl flex flex-col justify-between">
                <span className="text-xs font-semibold text-white truncate">{z.name}</span>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-sm font-bold text-gray-300">{z.occupancy}%</span>
                  <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor(z.status)} pulse-indicator`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recharts occupancy comparisons graph */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Capacity Saturation Comparison</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Bar metrics representation of total zone occupancies</p>
          </div>
          <div className="w-full h-[280px] mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={zones}>
                <XAxis dataKey="name" stroke="#94A3B8" fontSize={9} axisLine={false} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={9} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#111A33', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                <Bar dataKey="occupancy" fill="#00A8FF" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Enterprise logs list table */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/5 pb-4 space-y-3 md:space-y-0">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Live Zone Aggregates</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Search and filter active corridor states</p>
          </div>
          <div className="flex space-x-3 w-full md:w-auto">
            <input
              type="text"
              placeholder="Search zones..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-[#111A33] border border-white/10 px-4 py-2 rounded-xl text-xs outline-none text-white placeholder-gray-500 focus:border-[#00A8FF] w-full md:w-48"
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-[#111A33] border border-white/10 px-3 py-2 rounded-xl text-xs outline-none text-white focus:border-[#00A8FF]"
            >
              <option value="All">All Statuses</option>
              <option value="Safe">Safe</option>
              <option value="Moderate">Moderate</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-[#94A3B8] border-b border-white/5">
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Zone Identifier</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Status Badge</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Headcount</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Occupancy Index</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Operations Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredZones.map((z, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-[#111A33]/20 transition-colors">
                  <td className="py-4 px-4 font-semibold text-white">{z.name}</td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex px-2 py-0.5 text-[9px] font-bold rounded border uppercase tracking-wider ${getStatusText(z.status)}`}>
                      {z.status}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-white font-mono">{z.count.toLocaleString()} Fans</td>
                  <td className="py-4 px-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-24 bg-[#111A33] rounded-full h-1.5 overflow-hidden">
                        <div className={`h-1.5 rounded-full ${getStatusColor(z.status)}`} style={{ width: `${z.occupancy}%` }} />
                      </div>
                      <span className="font-mono text-gray-300 font-bold">{z.occupancy}%</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <button className="px-3.5 py-1.5 bg-[#00A8FF]/10 hover:bg-[#00A8FF]/20 text-[#00A8FF] border border-[#00A8FF]/20 rounded-lg font-bold tracking-wider uppercase text-[9px] transition-colors duration-200">
                      View Feed
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default CrowdMonitoring;
