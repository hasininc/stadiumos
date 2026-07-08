import React, { useState } from 'react';
import { useOpsStore } from '../store/opsStore';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

export const VendorAnalytics: React.FC = () => {
  const store = useOpsStore();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredInvs = store.inventories.filter((inv) => {
    return inv.vendor_id.toLowerCase().includes(searchQuery.toLowerCase()) || 
           inv.product_id.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const salesData = [
    { hour: '14:00', sales: 420 },
    { hour: '15:00', sales: 680 },
    { hour: '16:00', sales: 940 },
    { hour: '17:00', sales: 1240 },
    { hour: '18:00', sales: 1850 },
    { hour: '19:00', sales: 1620 }
  ];

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">Vendor Operations & Analytics</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Concessions sales volume, demand spikes forecast, and stock alerts</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Total Concession Revenue</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">$8,420.00 USD</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Hourly Sales Average</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">$1,240.50 USD</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Demand Peak Forecast Time</span>
          <div className="text-xl font-extrabold text-[#8B5CF6] font-display">19:45 (Half Time)</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Low Stock Warnings</span>
          <div className="text-xl font-extrabold text-[#EF4444] font-display">
            {store.inventories.length} Kiosks
          </div>
        </div>
      </div>

      {/* Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sales Speed Graph */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl h-[400px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Concession Sales Velocity</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Transactional volume speed tracking</p>
          </div>
          <div className="w-full h-[280px] mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={salesData}>
                <defs>
                  <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22C55E" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#22C55E" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#111A33', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                <Area type="monotone" dataKey="sales" stroke="#22C55E" strokeWidth={3} fillOpacity={1} fill="url(#colorSales)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Popular products list */}
        <div className="lg:col-span-1 glass-panel p-6 rounded-2xl h-[400px] flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider">Popular Products</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Items with high transactional velocity</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 mt-6">
            <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl flex items-center justify-between">
              <span className="text-xs font-bold text-white">Bottled Water</span>
              <span className="text-xs font-mono text-[#00E5FF] font-bold">842 Units</span>
            </div>
            <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl flex items-center justify-between">
              <span className="text-xs font-bold text-white">Hot Dogs</span>
              <span className="text-xs font-mono text-[#00E5FF] font-bold">590 Units</span>
            </div>
            <div className="p-4 bg-[#111A33] border border-white/5 rounded-xl flex items-center justify-between">
              <span className="text-xs font-bold text-white">Ponchos (Rain Gear)</span>
              <span className="text-xs font-mono text-[#00E5FF] font-bold">342 Units</span>
            </div>
          </div>
        </div>
      </div>

      {/* Warnings table */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/5 pb-4 space-y-3 md:space-y-0">
          <div>
            <h3 className="text-base font-bold text-white tracking-wider text-[#EF4444]">Low Stock Concession Alerts</h3>
            <p className="text-[#94A3B8] text-xs mt-0.5">Restocking requests triggered to warehouse hubs</p>
          </div>
          <input
            type="text"
            placeholder="Filter by Kiosk or Product..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-[#111A33] border border-white/10 px-4 py-2 rounded-xl text-xs outline-none text-white placeholder-gray-500 focus:border-[#EF4444] w-full md:w-64"
          />
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-[#94A3B8] border-b border-white/5">
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Vendor Kiosk ID</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Product</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Current Stock</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Alert Threshold</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredInvs.length > 0 ? (
                filteredInvs.map((inv) => (
                  <tr key={inv.id} className="border-b border-white/5 hover:bg-[#111A33]/20 transition-colors">
                    <td className="py-4 px-4 font-semibold text-white">Kiosk {inv.vendor_id}</td>
                    <td className="py-4 px-4 font-mono text-[#00A8FF] font-bold">{inv.product_id}</td>
                    <td className="py-4 px-4 font-bold text-white">{inv.current_stock} Units</td>
                    <td className="py-4 px-4 text-gray-400">{inv.min_threshold} Units</td>
                    <td className="py-4 px-4">
                      <span className="inline-flex px-2 py-0.5 text-[9px] font-bold bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20 rounded uppercase tracking-wider">
                        CRITICAL STOCK
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500">
                    No low-stock kiosks mapped.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default VendorAnalytics;
