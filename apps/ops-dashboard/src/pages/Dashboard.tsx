import React, { useEffect, useState } from 'react';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';
import wsClient from '../services/websocket';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

export const Dashboard: React.FC = () => {
  const store = useOpsStore();
  const [historyChart, setHistoryChart] = useState<{ time: string; density: number }[]>([]);
  const [incidentDashboard, setIncidentDashboard] = useState<{
    active_incidents_count: number;
    sla_compliance_rate: number;
  } | null>(null);

  useEffect(() => {
    wsClient.connectAll();

    const bootstrap = async () => {
      try {
        const [heatmap, incidents, lowStock, dashMetrics] = await Promise.all([
          dashboardService.getCrowdHeatmap(),
          dashboardService.getIncidents(),
          dashboardService.getLowStockInventory(),
          dashboardService.getIncidentDashboard(),
        ]);
        store.setCrowdMetrics(heatmap);
        store.setIncidents(incidents);
        store.setInventories(lowStock);
        setIncidentDashboard(dashMetrics);

        if (heatmap.length > 0) {
          const history = await dashboardService.getCrowdHistory(heatmap[0].zone_id, 12);
          setHistoryChart(
            history.map((h) => ({
              time: new Date(h.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              density: h.headcount,
            }))
          );
        }
      } catch {
        // Data unavailable — UI shows empty states
      }
    };
    bootstrap();

    return () => wsClient.disconnectAll();
  }, []);

  const totalHeadcount = store.crowdMetrics.reduce((acc, curr) => acc + curr.headcount, 0);
  const criticalCount = store.crowdMetrics.filter((z) => z.status === 'Critical').length;
  const activeIncidents = store.incidents.filter((i) => i.status !== 'Resolved');
  const medicalAlerts = store.incidents.filter((i) => i.type.includes('Medical') && i.status !== 'Resolved').length;
  const busyZones = store.crowdMetrics.filter((z) => z.status === 'Busy' || z.status === 'Critical').length;

  const stats = [
    {
      label: 'Total Attendance',
      val: totalHeadcount.toLocaleString(),
      sub: `${store.crowdMetrics.length} zones tracked`,
      color: 'text-[#00A8FF]',
      sparkData: store.crowdMetrics.map((z) => z.headcount),
    },
    {
      label: 'Critical Bottlenecks',
      val: criticalCount,
      sub: criticalCount > 0 ? 'Immediate action' : 'All clear',
      color: 'text-[#EF4444]',
      sparkData: store.crowdMetrics.map((z) => (z.status === 'Critical' ? 1 : 0)),
    },
    {
      label: 'Active Incidents',
      val: incidentDashboard?.active_incidents_count ?? activeIncidents.length,
      sub: `${activeIncidents.length} open`,
      color: 'text-[#F59E0B]',
      sparkData: [activeIncidents.length],
    },
    {
      label: 'SLA Compliance',
      val: incidentDashboard ? `${incidentDashboard.sla_compliance_rate.toFixed(0)}%` : '—',
      sub: 'Response within SLA',
      color: 'text-[#22C55E]',
      sparkData: incidentDashboard ? [incidentDashboard.sla_compliance_rate] : [0],
    },
    {
      label: 'Busy Zones',
      val: busyZones,
      sub: `of ${store.crowdMetrics.length} total`,
      color: 'text-[#22C55E]',
      sparkData: store.crowdMetrics.map((z) => z.occupancy_pct),
    },
    {
      label: 'Medical Alerts',
      val: medicalAlerts,
      sub: medicalAlerts > 0 ? 'Active' : 'None',
      color: 'text-[#EF4444]',
      sparkData: [medicalAlerts],
    },
  ];

  const zoneName = (zoneId: string) =>
    store.crowdMetrics.find((z) => z.zone_id === zoneId)?.zone_name || zoneId;

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Live Operations Command</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Real-time stadium telemetry from live API feeds</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-36 border border-white/5">
            <div className="flex justify-between items-start">
              <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">{stat.label}</span>
              <span className="text-[9px] text-[#94A3B8] font-bold">{stat.sub}</span>
            </div>
            <div className="flex justify-between items-end mt-4">
              <div className={`text-2xl font-extrabold font-display ${stat.color}`}>{stat.val}</div>
              {stat.sparkData.length > 1 && (
                <div className="w-16 h-8">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={stat.sparkData.map((d) => ({ val: d }))}>
                      <Area type="monotone" dataKey="val" stroke="#00A8FF" strokeWidth={1.5} fill="none" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[420px] flex flex-col">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Crowd Density Flow</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">
              {store.crowdMetrics[0]?.zone_name
                ? `Historical headcount — ${store.crowdMetrics[0].zone_name}`
                : 'No zone history available yet'}
            </p>
          </div>
          <div className="w-full h-[280px] mt-4">
            {historyChart.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historyChart}>
                  <defs>
                    <linearGradient id="colorDensity" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00A8FF" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#00A8FF" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#111A33', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                  <Area type="monotone" dataKey="density" stroke="#00A8FF" strokeWidth={3} fillOpacity={1} fill="url(#colorDensity)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                Record crowd snapshots to populate density history.
              </div>
            )}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl h-[420px] flex flex-col">
          <div>
            <h3 className="text-base font-bold text-[#8B5CF6] tracking-wider">Live Recommendations</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">From WebSocket agent feed</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 mt-4">
            {store.recommendations.length > 0 ? (
              store.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 bg-[#111A33] rounded-xl border border-white/5 space-y-2">
                  <span className="text-[10px] font-bold text-[#8B5CF6] uppercase tracking-wider">{rec.agent_name}</span>
                  <p className="text-xs text-gray-300 leading-relaxed">{rec.response_text}</p>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs text-center px-4">
                No live recommendations. Critical crowd alerts will appear here automatically.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="glass-panel p-6 rounded-2xl h-[340px] flex flex-col">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Active Incidents</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">From emergency response API</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 mt-4 pr-2">
            {activeIncidents.length > 0 ? (
              activeIncidents.map((inc) => (
                <div key={inc.id} className="flex justify-between items-center p-4 bg-[#111A33] rounded-xl border border-white/5">
                  <div>
                    <div className="text-sm font-semibold text-white">{inc.title}</div>
                    <div className="text-xs text-[#94A3B8] mt-0.5">
                      {inc.type} — {zoneName(inc.zone_id)}
                    </div>
                  </div>
                  <span className="text-[9px] font-bold px-2 py-0.5 bg-[#EF4444]/10 text-[#EF4444] rounded border border-[#EF4444]/20 uppercase">
                    {inc.severity}
                  </span>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                No active incidents reported.
              </div>
            )}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl h-[340px] flex flex-col">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Low Stock Warnings</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">From vendor inventory API</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 mt-4 pr-2">
            {store.inventories.length > 0 ? (
              store.inventories.map((inv) => (
                <div key={inv.id} className="flex justify-between items-center p-4 bg-[#111A33] rounded-xl border border-white/5">
                  <div>
                    <div className="text-sm font-semibold text-white">Vendor {inv.vendor_id.slice(0, 8)}</div>
                    <div className="text-xs text-[#94A3B8] mt-0.5">Product {inv.product_id.slice(0, 8)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-extrabold text-[#EF4444]">{inv.current_stock} units</div>
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase mt-0.5">Min: {inv.min_threshold}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                All inventories above minimum thresholds.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
