import React, { useState } from 'react';
import { useOpsStore } from '../store/opsStore';
import { dashboardService } from '../services/dashboard';
import { parseApiError } from '../utils/apiError';

const TOOLS = [
  { name: 'get_crowd_status', desc: 'Fetch zone heatmap data', endpoint: '/api/v1/crowd/heatmap' },
  { name: 'get_vendor_inventory', desc: 'List all vendor inventory', endpoint: '/api/v1/vendors/inventory' },
  { name: 'get_low_stock', desc: 'List low-stock inventory items', endpoint: '/api/v1/vendors/inventory/low-stock' },
  { name: 'get_incidents', desc: 'List active emergency incidents', endpoint: '/api/v1/emergencies' },
  { name: 'generate_route', desc: 'Calculate navigation route', endpoint: 'POST /api/v1/navigation/route' },
];

export const AICommandCenter: React.FC = () => {
  const store = useOpsStore();
  const [selectedTool, setSelectedTool] = useState(TOOLS[0].name);
  const [toolParams, setToolParams] = useState('{}');
  const [executionResult, setExecutionResult] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const handleExecute = async () => {
    setRunning(true);
    setExecutionResult(null);
    try {
      const parsed = JSON.parse(toolParams || '{}');
      let result: unknown;

      switch (selectedTool) {
        case 'get_crowd_status':
          result = await dashboardService.getCrowdHeatmap();
          break;
        case 'get_vendor_inventory':
          result = await dashboardService.getVendorInventory();
          break;
        case 'get_low_stock':
          result = await dashboardService.getLowStockInventory();
          break;
        case 'get_incidents':
          result = await dashboardService.getIncidents(parsed);
          break;
        case 'generate_route':
          result = await dashboardService.calculateRoute({
            start_node_id: parsed.start_node_id,
            end_node_id: parsed.end_node_id,
            requires_accessibility: parsed.requires_accessibility ?? false,
          });
          break;
        default:
          result = { error: 'Unknown tool' };
      }

      setExecutionResult(JSON.stringify(result, null, 2));
    } catch (err: unknown) {
      if (err instanceof SyntaxError) {
        setExecutionResult(JSON.stringify({ status: 'error', message: 'Invalid JSON parameters' }, null, 2));
      } else {
        setExecutionResult(JSON.stringify({ status: 'error', message: parseApiError(err, 'Tool execution failed') }, null, 2));
      }
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Operations Tool Console</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Execute live API tools against the backend</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Zones Tracked</span>
          <div className="text-xl font-extrabold text-[#8B5CF6] font-display">{store.crowdMetrics.length}</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Incidents</span>
          <div className="text-xl font-extrabold text-[#EF4444] font-display">
            {store.incidents.filter((i) => i.status !== 'Resolved').length}
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Low Stock Items</span>
          <div className="text-xl font-extrabold text-[#F59E0B] font-display">{store.inventories.length}</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Available Tools</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">{TOOLS.length}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl flex flex-col min-h-[400px]">
          <h3 className="text-base font-bold text-white tracking-wider">Tool Executor</h3>
          <div className="space-y-4 mt-6 flex-1">
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase">Tool</label>
              <select
                value={selectedTool}
                onChange={(e) => {
                  setSelectedTool(e.target.value);
                  const defaults: Record<string, string> = {
                    generate_route: JSON.stringify({ start_node_id: 'NODE-GATE-A', end_node_id: 'NODE-SEAT-1', requires_accessibility: false }, null, 2),
                    get_incidents: JSON.stringify({ limit: 20 }, null, 2),
                  };
                  setToolParams(defaults[e.target.value] || '{}');
                }}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white"
              >
                {TOOLS.map((t) => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase">Parameters (JSON)</label>
              <textarea
                value={toolParams}
                onChange={(e) => setToolParams(e.target.value)}
                className="bg-[#111A33] border border-white/10 p-3 rounded-xl text-xs outline-none text-white font-mono h-28 resize-none"
              />
            </div>
            <button
              onClick={handleExecute}
              disabled={running}
              className="w-full bg-[#8B5CF6] hover:bg-[#7c4ee4] disabled:opacity-50 text-white font-bold py-3 rounded-xl text-xs uppercase tracking-widest"
            >
              {running ? 'Executing...' : 'Run Tool'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl min-h-[400px] flex flex-col">
          <h3 className="text-base font-bold text-white tracking-wider">API Response</h3>
          <div className="bg-[#050B1C] border border-white/5 p-4 rounded-xl flex-1 mt-4 font-mono text-[11px] text-gray-300 overflow-y-auto whitespace-pre">
            {executionResult || 'Select a tool and click Run to see live API output.'}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl">
        <h3 className="text-base font-bold text-white tracking-wider text-[#8B5CF6]">Tools Catalog</h3>
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-[#94A3B8] border-b border-white/5">
                <th className="py-3 px-4 font-bold uppercase">Tool</th>
                <th className="py-3 px-4 font-bold uppercase">Endpoint</th>
                <th className="py-3 px-4 font-bold uppercase">Description</th>
              </tr>
            </thead>
            <tbody>
              {TOOLS.map((t) => (
                <tr key={t.name} className="border-b border-white/5">
                  <td className="py-4 px-4 font-mono text-[#00A8FF] font-bold">{t.name}</td>
                  <td className="py-4 px-4 font-mono text-gray-400">{t.endpoint}</td>
                  <td className="py-4 px-4 text-gray-300">{t.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default AICommandCenter;
