import React, { useState } from 'react';
import { useOpsStore } from '../store/opsStore';

export const AICommandCenter: React.FC = () => {
  const store = useOpsStore();
  const [selectedTool, setSelectedTool] = useState("get_crowd_status");
  const [toolParams, setToolParams] = useState('{"zone_id": "ZONE_GATE_A"}');
  const [executionResult, setExecutionResult] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const tools = [
    { name: "get_crowd_status", role: "Security Staff", desc: "Retrieves headcount and occupancy parameters for a target zone." },
    { name: "get_predictions", role: "Security Staff", desc: "Queries ML service for forecasted waiting times and bottleneck risk indicators." },
    { name: "get_camera_events", role: "Security Staff", desc: "Fetches YOLO detection records from edge CCTV feeds." },
    { name: "get_vendor_inventory", role: "Vendor", desc: "Checks stock counts and warning levels at concessions." },
    { name: "generate_route", label: "Evacuation Planner", role: "Operations Manager", desc: "Generates evacuation paths or optimal redirects." }
  ];

  const handleExecute = async () => {
    setRunning(true);
    setExecutionResult(null);
    try {
      await new Promise(resolve => setTimeout(resolve, 1200));
      const parsed = JSON.parse(toolParams);
      if (selectedTool === "get_crowd_status") {
        setExecutionResult(JSON.stringify({ status: "success", zone_id: parsed.zone_id || "ZONE_GATE_A", headcount: 1450, occupancy_pct: 72.5, state: "Busy" }, null, 2));
      } else {
        setExecutionResult(JSON.stringify({ status: "success", executed: selectedTool, payload: parsed, message: "Simulated output logs compiled" }, null, 2));
      }
    } catch (e) {
      setExecutionResult(JSON.stringify({ status: "error", message: "Invalid parameters schema format" }, null, 2));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">AI Command & Orchestrator</h1>
        <p className="text-[#94A3B8] text-xs mt-1">LangGraph cognitive execution pipeline controls and active tools registry</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Total Agent Requests</span>
          <div className="text-xl font-extrabold text-[#8B5CF6] font-display">1,482 Logs</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Average Inference Latency</span>
          <div className="text-xl font-extrabold text-[#00E5FF] font-display">124 ms</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Cognitive Graph Depth</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">6 Agent Nodes</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Safeguard Accuracy</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">99.8%</div>
        </div>
      </div>

      {/* Layout split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tool executor simulator panel */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl flex flex-col justify-between h-[450px]">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Tools Execution Console</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Mock-execute agent tool calling scripts</p>
          </div>

          <div className="space-y-4 mt-6 flex-1">
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Target Tool</label>
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#00A8FF]"
              >
                {tools.map((t, idx) => (
                  <option key={idx} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Parameter Schema (JSON)</label>
              <textarea
                value={toolParams}
                onChange={(e) => setToolParams(e.target.value)}
                className="bg-[#111A33] border border-white/10 p-3 rounded-xl text-xs outline-none text-white focus:border-[#00A8FF] font-mono h-24 resize-none"
              />
            </div>

            <button
              onClick={handleExecute}
              disabled={running}
              className="w-full bg-[#8B5CF6] hover:bg-[#7c4ee4] text-white font-bold py-3 rounded-xl transition-colors text-xs uppercase tracking-widest"
            >
              {running ? "Simulating execution..." : "Run Tool Call"}
            </button>
          </div>
        </div>

        {/* Output logs terminal */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[450px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Execution Output Terminal</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Response JSON compilation output from orchestrator</p>
          </div>
          <div className="bg-[#050B1C] border border-white/5 p-4 rounded-xl flex-1 mt-6 font-mono text-[11px] text-gray-300 overflow-y-auto whitespace-pre">
            {executionResult ? executionResult : "$ ./stadiumos_agent_cli --invoke-tool=" + selectedTool}
          </div>
        </div>
      </div>

      {/* Tools Registry Table */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
        <div>
          <h3 className="text-base font-bold text-white tracking-wider text-[#8B5CF6]">Active AI Tools Catalog</h3>
          <p className="text-[#94A3B8] text-xs mt-0.5">Permissions mapping and schema structures</p>
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-[#94A3B8] border-b border-white/5">
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Tool Name</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Role Restriction</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Functional Description</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {tools.map((t, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-[#111A33]/20 transition-colors">
                  <td className="py-4 px-4 font-mono text-[#00A8FF] font-bold">{t.name}</td>
                  <td className="py-4 px-4">
                    <span className="inline-flex px-2.5 py-0.5 text-[9px] font-bold bg-[#8B5CF6]/10 text-[#8B5CF6] border border-[#8B5CF6]/20 rounded uppercase tracking-wider">
                      {t.role}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-gray-300">{t.desc}</td>
                  <td className="py-4 px-4">
                    <span className="w-2 h-2 rounded-full bg-[#22C55E] inline-block" />
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
export default AICommandCenter;
