import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, Button, TextField, Typography, Alert } from '@mui/material';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0C0E12] px-4">
      <Card className="w-full max-w-md p-8 bg-[#161920] border border-gray-800 text-white rounded-2xl shadow-xl">
        <Typography variant="h4" className="font-bold text-center text-[#00E676] mb-2 font-display">
          StadiumOS
        </Typography>
        <Typography variant="body2" className="text-gray-400 text-center mb-6">
          Predict. Decide. Act.
        </Typography>

        {error && (
          <Alert severity="error" className="mb-4 bg-red-900/20 text-red-400 border border-red-900/50">
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextField
            fullWidth
            label="Email Address"
            variant="outlined"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            InputLabelProps={{ style: { color: '#888' } }}
            inputProps={{ style: { color: '#fff' } }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#333' },
                '&:hover fieldset': { borderColor: '#00E676' },
              },
            }}
          />

          <TextField
            fullWidth
            label="Password"
            variant="outlined"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            InputLabelProps={{ style: { color: '#888' } }}
            inputProps={{ style: { color: '#fff' } }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#333' },
                '&:hover fieldset': { borderColor: '#00E676' },
              },
            }}
          />

          <div className="flex justify-between items-center text-sm text-gray-400">
            <Link to="/forgot-password" className="hover:text-[#00E676] transition-colors">
              Forgot Password?
            </Link>
          </div>

          <Button
            fullWidth
            variant="contained"
            type="submit"
            disabled={loading}
            className="py-3 bg-[#00E676] hover:bg-[#00c853] text-black font-semibold rounded-lg transition-colors mt-2"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </Button>
        </form>

        <Typography variant="body2" className="text-gray-400 text-center mt-6 text-sm">
          Don't have an account?{' '}
          <Link to="/register" className="text-[#2979FF] hover:underline">
            Register Here
          </Link>
        </Typography>
      </Card>
    </div>
  );
};
export default Login;
