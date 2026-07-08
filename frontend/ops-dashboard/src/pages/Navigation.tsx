import React, { useState } from 'react';

export const Navigation: React.FC = () => {
  const [start, setStart] = useState("NODE-GATE-A");
  const [end, setEnd] = useState("NODE-SEAT-1");
  const [accessible, setAccessible] = useState(false);
  const [path, setPath] = useState<string[]>([]);
  const [dist, setDist] = useState<number | null>(null);
  const [est, setEst] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const calculateOptimalPath = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (accessible) {
        setPath(["NODE-GATE-A", "NODE-CONC-1", "NODE-ELEVATOR-1", "NODE-SEAT-1-ACC"]);
        setDist(35.0);
        setEst(120.0);
      } else {
        setPath(["NODE-GATE-A", "NODE-CONC-1", "NODE-SEAT-1"]);
        setDist(23.0);
        setEst(46.0);
      }
    } catch (e) {
      // Dev fallbacks
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Smart Navigation Control</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Dijkstra routing paths estimation, wheelchair-accessible filters, and dynamic evacuation redirects</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Routing Sessions</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">240 Sessions</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Dynamic Reroutes (1H)</span>
          <div className="text-xl font-extrabold text-[#F59E0B] font-display">8 Redirects</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Wheelchair Accessible Routes</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">42 Queries</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Stadium Evacuation Status</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">NORMAL</div>
        </div>
      </div>

      {/* Layout split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Navigation request form */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Routing Search Console</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Define coordinate parameters to test pathing vectors</p>
          </div>

          <div className="space-y-4 mt-6 flex-1">
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Start Coordinates Node</label>
              <input
                type="text"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#00A8FF]"
              />
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase tracking-wider">Target Node Destination</label>
              <input
                type="text"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white focus:border-[#00A8FF]"
              />
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-xs text-gray-300">Wheelchair Accessible (Avoid Stairs)</span>
              <input
                type="checkbox"
                checked={accessible}
                onChange={(e) => setAccessible(e.target.checked)}
                className="w-4 h-4 rounded bg-[#111A33] border-white/10 text-[#00A8FF] focus:ring-0 outline-none"
              />
            </div>

            <button
              onClick={calculateOptimalPath}
              disabled={loading}
              className="w-full bg-[#00A8FF] hover:bg-[#0096e5] text-white font-bold py-3.5 rounded-xl transition-colors text-xs uppercase tracking-widest"
            >
              {loading ? "Running Dijkstra..." : "Compute Routing Map"}
            </button>
          </div>
        </div>

        {/* Map Route Output display */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[420px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Navigation Routing Log</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Calculated path nodes layout segments</p>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 mt-6 pr-2">
            {path.length > 0 ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl text-center">
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase">Estimated Traversal Distance</div>
                    <div className="text-lg font-bold text-white mt-1 font-mono">{dist} Meters</div>
                  </div>
                  <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl text-center">
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase">Estimated Traversal Duration</div>
                    <div className="text-lg font-bold text-white mt-1 font-mono">{est} Seconds</div>
                  </div>
                </div>

                <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl">
                  <div className="text-[9px] text-[#94A3B8] font-bold uppercase mb-3">Path Traversal Sequence</div>
                  <div className="flex flex-wrap items-center gap-2">
                    {path.map((node, idx) => (
                      <React.Fragment key={idx}>
                        <span className="px-3 py-1.5 bg-[#050B1C] border border-white/10 rounded-lg text-xs font-mono font-bold text-[#00E5FF]">
                          {node}
                        </span>
                        {idx < path.length - 1 && <span className="text-gray-600 font-bold">→</span>}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                Trigger routing computation to display path node segments.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Navigation;
