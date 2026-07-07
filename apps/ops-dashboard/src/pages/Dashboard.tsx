import React, { useEffect } from 'react';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';
import wsClient from '../services/websocket';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, Grid, Typography } from '@mui/material';

export const Dashboard: React.FC = () => {
  const store = useOpsStore();

  useEffect(() => {
    wsClient.connectAll();

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
        // Dev offline fallbacks
      }
    };
    bootstrapMetrics();

    return () => wsClient.disconnectAll();
  }, []);

  const criticalZonesCount = store.crowdMetrics.filter((z) => z.status === 'Critical').length;
  const totalIncidentsCount = store.incidents.filter((i) => i.status !== 'Resolved').length;

  return (
    <div className="flex-1 bg-[#0C0E12] min-h-screen p-8 text-white space-y-8 overflow-y-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white font-display">Executive Operations Command</h1>
          <p className="text-gray-400 text-sm mt-1">FIFA World Cup 2026 Live Telemetry Console</p>
        </div>
      </div>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl flex flex-col justify-between h-36">
            <Typography variant="body2" className="text-gray-400 font-semibold uppercase">Critical Zones</Typography>
            <div className="flex justify-between items-baseline mt-4">
              <Typography variant="h3" className="font-extrabold text-red-500">{criticalZonesCount}</Typography>
              <span className="text-xs text-red-400 bg-red-950/30 px-2.5 py-1 rounded-full border border-red-900/50">Immediate Action</span>
            </div>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl flex flex-col justify-between h-36">
            <Typography variant="body2" className="text-gray-400 font-semibold uppercase">Active Emergencies</Typography>
            <div className="flex justify-between items-baseline mt-4">
              <Typography variant="h3" className="font-extrabold text-orange-500">{totalIncidentsCount}</Typography>
              <span className="text-xs text-orange-400 bg-orange-950/30 px-2.5 py-1 rounded-full border border-orange-900/50">Dispatched Responders</span>
            </div>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl flex flex-col justify-between h-36">
            <Typography variant="body2" className="text-gray-400 font-semibold uppercase">Prediction Models Active</Typography>
            <div className="flex justify-between items-baseline mt-4">
              <Typography variant="h3" className="font-extrabold text-[#00E676]">6</Typography>
              <span className="text-xs text-[#00E676] bg-green-950/30 px-2.5 py-1 rounded-full border border-green-900/50">Inference OK</span>
            </div>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl flex flex-col justify-between h-36">
            <Typography variant="body2" className="text-gray-400 font-semibold uppercase">CCTV Feeds Streaming</Typography>
            <div className="flex justify-between items-baseline mt-4">
              <Typography variant="h3" className="font-extrabold text-[#2979FF]">12</Typography>
              <span className="text-xs text-[#2979FF] bg-blue-950/30 px-2.5 py-1 rounded-full border border-blue-900/50">YOLO Processing</span>
            </div>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        <Grid item xs={12} lg={8}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl h-[400px]">
            <Typography variant="h6" className="font-bold text-white mb-4">Crowd Density Trends (Last Hour)</Typography>
            <div className="w-full h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={[
                  { time: '17:00', density: 3400 },
                  { time: '17:15', density: 4200 },
                  { time: '17:30', density: 5100 },
                  { time: '17:45', density: 4800 },
                  { time: '18:00', density: 5600 }
                ]}>
                  <CartesianGrid stroke="#333" strokeDasharray="3 3" />
                  <XAxis dataKey="time" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ backgroundColor: '#1A1D26', border: '1px solid #333' }} />
                  <Line type="monotone" dataKey="density" stroke="#00E676" strokeWidth={3} dot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl h-[400px] flex flex-col">
            <Typography variant="h6" className="font-bold text-white mb-4">AI Advisor Feed</Typography>
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {store.recommendations.length > 0 ? (
                store.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-4 bg-[#1E232F] rounded-xl border border-gray-700 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-[#00E676]">{rec.agent_name}</span>
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">{rec.response_text}</p>
                  </div>
                ))
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                  No operational recommendations compiled
                </div>
              )}
            </div>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl h-80 flex flex-col">
            <Typography variant="h6" className="font-bold text-white mb-4">Active Incidents Queue</Typography>
            <div className="flex-1 overflow-y-auto space-y-3">
              {store.incidents.length > 0 ? (
                store.incidents.map((inc) => (
                  <div key={inc.id} className="flex justify-between items-center p-3.5 bg-[#1C1F26] rounded-xl border border-gray-800">
                    <div>
                      <div className="text-sm font-semibold">{inc.title}</div>
                      <div className="text-xs text-gray-500">{inc.type} in Zone B</div>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 bg-red-950 text-red-400 rounded-lg border border-red-900/40">
                      {inc.severity}
                    </span>
                  </div>
                ))
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                  Active area secure. No incidents reported.
                </div>
              )}
            </div>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card className="p-6 bg-[#161920] border border-gray-800 text-white rounded-2xl h-80 flex flex-col">
            <Typography variant="h6" className="font-bold text-white mb-4">Concessions Inventory Restock Warnings</Typography>
            <div className="flex-1 overflow-y-auto space-y-3">
              {store.inventories.length > 0 ? (
                store.inventories.map((inv) => (
                  <div key={inv.id} className="flex justify-between items-center p-3.5 bg-[#1C1F26] rounded-xl border border-gray-800">
                    <div>
                      <div className="text-sm font-semibold">Vendor Kiosk {inv.vendor_id}</div>
                      <div className="text-xs text-gray-500">Product: {inv.product_id}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-red-500">{inv.current_stock} Units</div>
                      <div className="text-xs text-gray-500">Min Alert: {inv.min_threshold}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                  Inventory stocked above alert thresholds.
                </div>
              )}
            </div>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
};
export default Dashboard;
