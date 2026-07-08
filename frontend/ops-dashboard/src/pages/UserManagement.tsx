import React, { useState } from 'react';

export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState([
    { name: "John Doe", email: "j.doe@fifa2026.org", role: "Administrator", status: "Active" },
    { name: "Sarah Smith", email: "s.smith@stadiumos.com", role: "Operations Manager", status: "Active" },
    { name: "Agent Brown", email: "b.security@stadiumos.com", role: "Security Staff", status: "Active" },
    { name: "Dr. Taylor", email: "t.medic@stadiumos.com", role: "Medical Staff", status: "Active" }
  ]);

  return (
    <div className="p-8 text-[#F8FAFC] space-y-8 font-sans selection:bg-[#00A8FF]/20">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-white">User & Console Control</h1>
        <p className="text-[#94A3B8] text-xs mt-1">Onboard staff accounts, audit operator logs, and verify RBAC credentials</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Total Registered Personnel</span>
          <div className="text-xl font-extrabold text-[#00A8FF] font-display">24 Active Operators</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Active Terminal Access Locks</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">4 Connected Consoles</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-28 border border-white/5">
          <span className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Failed Security Handshakes (24H)</span>
          <div className="text-xl font-extrabold text-[#22C55E] font-display">0 Warnings</div>
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
        <div>
          <h3 className="text-base font-bold text-white tracking-wider">Operator Access Registry</h3>
          <p className="text-[#94A3B8] text-xs mt-0.5">Audit credential configurations</p>
        </div>

        <div className="overflow-x-auto mt-6">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="text-[#94A3B8] border-b border-white/5">
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Staff Name</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Secure Email</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Console Authorization Role</th>
                <th className="py-3 px-4 font-bold uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-[#111A33]/20 transition-colors">
                  <td className="py-4 px-4 font-semibold text-white">{u.name}</td>
                  <td className="py-4 px-4 text-[#94A3B8] font-mono">{u.email}</td>
                  <td className="py-4 px-4">
                    <span className="inline-flex px-2.5 py-0.5 text-[9px] font-bold bg-[#00A8FF]/10 text-[#00A8FF] border border-[#00A8FF]/20 rounded uppercase tracking-wider">
                      {u.role}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className="inline-flex px-2.5 py-0.5 text-[9px] font-bold bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/20 rounded uppercase tracking-wider">
                      {u.status}
                    </span>
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
export default UserManagement;
