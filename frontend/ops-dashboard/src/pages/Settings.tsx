import React, { useState } from 'react';

export const Settings: React.FC = () => {
  const [yoloEnabled, setYoloEnabled] = useState(true);
  const [fcmEnabled, setFcmEnabled] = useState(true);
  const [redisSync, setRedisSync] = useState(true);

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">System Settings</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Configure operational thresholds, AI agents settings, and edge integrations</p>
      </div>

      {/* Grid */}
      <div className="max-w-3xl space-y-6">
        <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">Edge AI & Inference Settings</h3>
          <div className="h-px bg-white/5" />
          
          <div className="flex justify-between items-center py-2">
            <div>
              <div className="text-xs font-bold text-white uppercase tracking-wider">YOLOv11 Crowd Counting</div>
              <p className="text-[11px] text-gray-400 mt-1">Process camera frames every 2 seconds to estimate density counts.</p>
            </div>
            <input
              type="checkbox"
              checked={yoloEnabled}
              onChange={(e) => setYoloEnabled(e.target.checked)}
              className="w-4 h-4 rounded bg-[#111A33] border-white/10 text-[#00A8FF] focus:ring-0 outline-none"
            />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">Alert Notifications</h3>
          <div className="h-px bg-white/5" />

          <div className="flex justify-between items-center py-2">
            <div>
              <div className="text-xs font-bold text-white uppercase tracking-wider">Push Dispatch Alert Signals</div>
              <p className="text-[11px] text-gray-400 mt-1">Transmit mobile notifications on critical crowd bottlenecks or emergencies.</p>
            </div>
            <input
              type="checkbox"
              checked={fcmEnabled}
              onChange={(e) => setFcmEnabled(e.target.checked)}
              className="w-4 h-4 rounded bg-[#111A33] border-white/10 text-[#00A8FF] focus:ring-0 outline-none"
            />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">Data Pipeline Sync</h3>
          <div className="h-px bg-white/5" />

          <div className="flex justify-between items-center py-2">
            <div>
              <div className="text-xs font-bold text-white uppercase tracking-wider">Redis Cache Synchronizer</div>
              <p className="text-[11px] text-gray-400 mt-1">Synchronize local cache indices to Redis cluster nodes.</p>
            </div>
            <input
              type="checkbox"
              checked={redisSync}
              onChange={(e) => setRedisSync(e.target.checked)}
              className="w-4 h-4 rounded bg-[#111A33] border-white/10 text-[#00A8FF] focus:ring-0 outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
export default Settings;
