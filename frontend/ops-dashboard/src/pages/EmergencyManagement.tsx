import React, { useState } from 'react';
import { useOpsStore } from '../store/opsStore';

export const EmergencyManagement: React.FC = () => {
  const store = useOpsStore();
  const [title, setTitle] = useState("");
  const [type, setType] = useState("Medical Emergency");
  const [severity, setSeverity] = useState("Critical");
  const [zone, setZone] = useState("ZONE_GATE_A");
  const [desc, setDesc] = useState("");
  const [loading, setLoading] = useState(false);

  const handleDispatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      store.addIncident({
        id: "inc-" + Math.floor(Math.random() * 900 + 100),
        title,
        description: desc,
        type,
        severity,
        status: "Reported",
        reported_at: new Date().toISOString()
      });
      setTitle("");
      setDesc("");
    } catch (e) {
      // Dev fallbacks
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (sev: string) => {
    if (sev === "Critical") return "text-[#EF4444] border-[#EF4444]/20 bg-[#EF4444]/10";
    if (sev === "High") return "text-[#F59E0B] border-[#F59E0B]/20 bg-[#F59E0B]/10";
    return "text-[#00A8FF] border-[#00A8FF]/20 bg-[#00A8FF]/10";
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Emergency Response Control</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Incident dispatch, responder assignments, and SLA response monitors</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Medical Incidents</span>
          <div className="text-xl font-extrabold text-[#EF4444] font-display">
            {store.incidents.filter(i => i.type.includes("Medical")).length} Active
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Security Violations</span>
          <div className="text-xl font-extrabold text-[#F59E0B] font-display">
            {store.incidents.filter(i => i.type.includes("Security") || i.type.includes("Crowd")).length} Active
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Average SLA Response Time</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">3.2 Minutes</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Dispatched Responders</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">4 Teams</div>
        </div>
      </div>

      {/* Layout split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Active Emergency list table */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col justify-between h-[420px]">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Emergency Incidents Timeline</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Real-time status updates and dispatcher notes</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 mt-6">
            {store.incidents.length > 0 ? (
              store.incidents.map((inc) => (
                <div key={inc.id} className="flex justify-between items-center p-4 bg-[#111A33] rounded-xl border border-white/5 hover:border-red-500/20 transition-all duration-300">
                  <div>
                    <div className="text-sm font-semibold text-white">{inc.title}</div>
                    <p className="text-xs text-gray-400 mt-1">{inc.description}</p>
                    <div className="text-[10px] text-gray-500 mt-2 font-mono">
                      Reported: {new Date(inc.reported_at).toLocaleTimeString()} | Location: Zone B
                    </div>
                  </div>
                  <div className="text-right flex flex-col space-y-2 items-end">
                    <span className={`inline-flex px-2.5 py-0.5 text-[9px] font-bold rounded border uppercase tracking-wider ${getSeverityBadge(inc.severity)}`}>
                      {inc.severity}
                    </span>
                    <span className="text-[10px] font-bold text-[#00E5FF] uppercase tracking-wider">{inc.status}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 text-xs">
                No incidents logged. Stadium zones secure.
              </div>
            )}
          </div>
        </div>

        {/* Dispatch trigger form */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider text-[#EF4444]">Dispatch Responders</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Log new incident parameters and alert responders</p>
          </div>

          <form onSubmit={handleDispatch} className="space-y-4 mt-6 flex-1">
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Incident Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Heat stroke at Concourse 104"
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#EF4444]"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="bg-[#111A33] border border-white/10 px-3 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#EF4444]"
                >
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Location Zone</label>
                <select
                  value={zone}
                  onChange={(e) => setZone(e.target.value)}
                  className="bg-[#111A33] border border-white/10 px-3 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#EF4444]"
                >
                  <option value="ZONE_GATE_A">North Gate A</option>
                  <option value="ZONE_SEC_104">Section 104</option>
                  <option value="ZONE_VIP">VIP Area</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#EF4444] hover:bg-[#d83535] text-white font-bold py-3.5 rounded-xl transition-colors text-xs uppercase tracking-widest"
            >
              {loading ? "Alerting responders..." : "Broadcast Incident Alert"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
export default EmergencyManagement;
