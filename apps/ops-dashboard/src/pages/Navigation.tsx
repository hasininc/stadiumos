import React, { useEffect, useState } from 'react';
import { dashboardService, MapNode, RouteResult } from '../services/dashboard';
import { parseApiError } from '../utils/apiError';

export const Navigation: React.FC = () => {
  const [nodes, setNodes] = useState<MapNode[]>([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [accessible, setAccessible] = useState(false);
  const [route, setRoute] = useState<RouteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<{ active_navigation_sessions: number; dynamic_reroutes_last_hour: number } | null>(null);
  const [accessibleCount, setAccessibleCount] = useState(0);
  const [evacuationStatus, setEvacuationStatus] = useState<string>('—');

  useEffect(() => {
    const load = async () => {
      try {
        const [map, navStatus, accessibility, evacuation] = await Promise.all([
          dashboardService.getNavigationMap(),
          dashboardService.getNavigationStatus(),
          dashboardService.getNavigationAccessibility(),
          dashboardService.getEvacuationStatus(),
        ]);
        setNodes(map.nodes);
        setStatus(navStatus);
        setAccessibleCount(accessibility.accessible_nodes.length);
        setEvacuationStatus(evacuation?.status || 'unknown');
        if (map.nodes.length >= 2) {
          setStart(map.nodes[0].id);
          setEnd(map.nodes[map.nodes.length - 1].id);
        }
      } catch {
        // empty states
      }
    };
    load();
  }, []);

  const calculateRoute = async () => {
    setLoading(true);
    setError(null);
    setRoute(null);
    try {
      const result = await dashboardService.calculateRoute({
        start_node_id: start,
        end_node_id: end,
        routing_profile: 'Shortest',
        requires_accessibility: accessible,
      });
      setRoute(result);
    } catch (err: unknown) {
      setError(parseApiError(err, 'Could not calculate route.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Smart Navigation Control</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Live routing via /api/v1/navigation</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Sessions</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">
            {status?.active_navigation_sessions ?? '—'}
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Reroutes (1H)</span>
          <div className="text-xl font-extrabold text-[#F59E0B] font-display">
            {status?.dynamic_reroutes_last_hour ?? '—'}
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Accessible Nodes</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">{accessibleCount}</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Evacuation Status</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display uppercase">{evacuationStatus}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl flex flex-col">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Route Calculator</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">{nodes.length} map nodes loaded</p>
          </div>

          {error && <div className="mt-4 p-3 bg-red-950/20 border border-red-900/50 text-red-400 text-xs rounded-xl">{error}</div>}

          <div className="space-y-4 mt-6 flex-1">
            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase">Start Node</label>
              <select
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white"
              >
                {nodes.map((n) => (
                  <option key={n.id} value={n.id}>{n.name} ({n.id})</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-[9px] text-[#94A3B8] font-bold uppercase">End Node</label>
              <select
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="bg-[#111A33] border border-white/10 px-3.5 py-2.5 rounded-xl text-xs outline-none text-white"
              >
                {nodes.map((n) => (
                  <option key={n.id} value={n.id}>{n.name} ({n.id})</option>
                ))}
              </select>
            </div>

            <div className="flex items-center justify-between py-2">
              <span className="text-xs text-gray-300">Wheelchair accessible</span>
              <input
                type="checkbox"
                checked={accessible}
                onChange={(e) => setAccessible(e.target.checked)}
                className="w-4 h-4 rounded bg-[#111A33] border-white/10 text-[#00A8FF] focus:ring-0 outline-none"
              />
            </div>

            <button
              onClick={calculateRoute}
              disabled={loading || !start || !end}
              className="w-full bg-[#00A8FF] hover:bg-[#0096e5] disabled:opacity-50 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-widest"
            >
              {loading ? 'Calculating...' : 'Compute Route'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl min-h-[420px] flex flex-col">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Route Result</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">From navigation routing engine</p>
          </div>

          <div className="flex-1 overflow-y-auto mt-6">
            {route ? (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl text-center">
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase">Distance</div>
                    <div className="text-lg font-bold text-white mt-1 font-mono">{route.total_distance_meters.toFixed(1)} m</div>
                  </div>
                  <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl text-center">
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase">Duration</div>
                    <div className="text-lg font-bold text-white mt-1 font-mono">{route.estimated_time_seconds.toFixed(0)} sec</div>
                  </div>
                  <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl text-center">
                    <div className="text-[9px] text-[#94A3B8] font-bold uppercase">Confidence</div>
                    <div className="text-lg font-bold text-white mt-1 font-mono">{(route.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                </div>
                <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl">
                  <div className="text-[9px] text-[#94A3B8] font-bold uppercase mb-3">Path ({route.path_nodes.length} nodes)</div>
                  <div className="flex flex-wrap items-center gap-2">
                    {route.path_nodes.map((node, idx) => (
                      <React.Fragment key={node.id}>
                        <span className="px-3 py-1.5 bg-[#050B1C] border border-white/10 rounded-lg text-xs font-mono text-[#00E5FF]">
                          {node.name}
                        </span>
                        {idx < route.path_nodes.length - 1 && <span className="text-gray-600 font-bold">→</span>}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-[#94A3B8] text-xs">
                Select start and end nodes, then compute a route.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Navigation;
