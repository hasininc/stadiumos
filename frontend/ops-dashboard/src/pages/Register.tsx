import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Card, Button, TextField, Typography, Alert } from '@mui/material';

export const Register: React.FC = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/v1/auth/register', { email, password });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0C0E12] px-4">
      <Card className="w-full max-w-md p-8 bg-[#161920] border border-gray-800 text-white rounded-2xl shadow-xl">
        <Typography variant="h4" className="font-bold text-center text-[#00E676] mb-2 font-display">
          Register Account
        </Typography>
        <Typography variant="body2" className="text-gray-400 text-center mb-6">
          Join the StadiumOS Operations Network
        </Typography>

        {error && (
          <Alert severity="error" className="mb-4 bg-red-900/20 text-red-400 border border-red-900/50">
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" className="mb-4 bg-green-900/20 text-green-400 border border-green-900/50">
            Account created successfully! Redirecting to login...
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

          <TextField
            fullWidth
            label="Confirm Password"
            variant="outlined"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
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

          <Button
            fullWidth
            variant="contained"
            type="submit"
            disabled={loading}
            className="py-3 bg-[#00E676] hover:bg-[#00c853] text-black font-semibold rounded-lg transition-colors mt-2"
          >
            {loading ? 'Processing...' : 'Register'}
          </Button>
        </form>

        <Typography variant="body2" className="text-gray-400 text-center mt-6 text-sm">
          Already have an account?{' '}
          <Link to="/login" className="text-[#2979FF] hover:underline">
            Login Here
          </Link>
        </Typography>
      </Card>
    </div>
  );
};
export default Register;
