import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.post('/api/v1/auth/register', { email, password });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0C0E12] text-white px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-md bg-[#161920] border border-gray-800 p-8 rounded-2xl space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-[#00E676] font-display">StadiumOS</h2>
          <p className="text-sm text-gray-400 mt-2">Onboard new operator coordinates</p>
        </div>

        {error && (
          <div className="p-3 bg-red-950/30 border border-red-900/50 text-red-400 text-xs rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-950/30 border border-green-900/50 text-green-400 text-xs rounded-lg">
            Account created successfully! Redirecting to sign in...
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

          <div className="flex flex-col space-y-1">
            <label className="text-xs text-gray-400 font-semibold uppercase">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="bg-[#1E232F] border border-gray-800 focus:border-[#00E676] px-4 py-3 rounded-xl text-sm outline-none transition-colors"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || success}
          className="w-full bg-[#00E676] hover:bg-[#00c865] text-black font-bold py-3 rounded-xl transition-colors text-sm"
        >
          {loading ? "Creating credentials..." : "Register"}
        </button>

        <div className="text-center text-xs text-gray-500">
          Already registered? <span onClick={() => navigate('/login')} className="text-[#2979FF] cursor-pointer hover:underline">Sign In</span>
        </div>
      </form>
    </div>
  );
};
export default Register;
