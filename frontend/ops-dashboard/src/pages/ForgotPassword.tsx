import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMsg(null);
    try {
      await api.post('/api/v1/auth/forgot-password', { email });
      setMsg("Password recovery link sent successfully.");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Recovery process failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#050B1C] text-white px-6 font-sans relative overflow-hidden">
      {/* Background glowing blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00A8FF]/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#00E5FF]/5 rounded-full filter blur-[120px] pointer-events-none" />

      <form onSubmit={handleSubmit} className="w-full max-w-md bg-[#111A33]/60 backdrop-blur-xl border border-white/10 p-10 rounded-3xl space-y-6 shadow-2xl shadow-black/80 relative z-10">
        <div className="text-center">
          <div className="flex justify-center items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#00A8FF]" />
            <h2 className="text-2xl font-extrabold text-white tracking-widest font-display">STADIUMOS</h2>
          </div>
          <p className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-widest mt-1">FIFA World Cup 2026</p>
          <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-4" />
          <p className="text-xs text-gray-400">Password Recovery Gateway</p>
        </div>

        {error && (
          <div className="p-3 bg-[#EF4444]/10 border border-[#EF4444]/20 text-[#EF4444] text-xs rounded-xl font-semibold">
            {error}
          </div>
        )}

        {msg && (
          <div className="p-3 bg-[#22C55E]/10 border border-[#22C55E]/20 text-[#22C55E] text-xs rounded-xl font-semibold">
            {msg}
          </div>
        )}

        <div className="space-y-4">
          <div className="flex flex-col space-y-1.5">
            <label className="text-[10px] text-[#94A3B8] font-bold uppercase tracking-wider">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-[#16213E]/60 border border-white/10 focus:border-[#00A8FF] px-4 py-3.5 rounded-xl text-xs outline-none transition-all duration-300 placeholder-gray-600 focus:shadow-md focus:shadow-[#00A8FF]/5 text-white"
              placeholder="operator@fifa2026.org"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#00A8FF] hover:bg-[#0096e5] active:scale-[0.98] text-white font-bold py-3.5 rounded-xl transition-all duration-300 text-xs uppercase tracking-widest"
        >
          {loading ? "Generating token..." : "Recover Password"}
        </button>

        <div className="text-center text-[11px] text-[#94A3B8] font-medium">
          Remember credentials? <span onClick={() => navigate('/login')} className="text-[#00E5FF] cursor-pointer hover:underline">Log in</span>
        </div>
      </form>
    </div>
  );
};
export default ForgotPassword;
