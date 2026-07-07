import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Authentication failed. Validate credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0C0E12] text-white px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-md bg-[#161920] border border-gray-800 p-8 rounded-2xl space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-[#00E676] font-display">StadiumOS</h2>
          <p className="text-sm text-gray-400 mt-2">Sign in to the Executive Operations Console</p>
        </div>

        {error && (
          <div className="p-3 bg-red-950/30 border border-red-900/50 text-red-400 text-xs rounded-lg">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="flex flex-col space-y-1">
            <label className="text-xs text-gray-400 font-semibold uppercase">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-[#1E232F] border border-gray-800 focus:border-[#00E676] px-4 py-3 rounded-xl text-sm outline-none transition-colors"
              required
            />
          </div>

          <div className="flex flex-col space-y-1">
            <label className="text-xs text-gray-400 font-semibold uppercase">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-[#1E232F] border border-gray-800 focus:border-[#00E676] px-4 py-3 rounded-xl text-sm outline-none transition-colors"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#00E676] hover:bg-[#00c865] text-black font-bold py-3 rounded-xl transition-colors text-sm"
        >
          {loading ? "Authenticating session..." : "Sign In"}
        </button>

        <div className="text-center text-xs text-gray-500">
          New operator account? <span onClick={() => navigate('/register')} className="text-[#2979FF] cursor-pointer hover:underline">Register Here</span>
        </div>
      </form>
    </div>
  );
};
export default Login;
