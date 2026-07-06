import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card, Button, TextField, Typography, Alert } from '@mui/material';

export const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await axios.post('/api/v1/auth/forgot-password', { email });
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to dispatch recovery email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0C0E12] px-4">
      <Card className="w-full max-w-md p-8 bg-[#161920] border border-gray-800 text-white rounded-2xl shadow-xl">
        <Typography variant="h4" className="font-bold text-center text-[#00E676] mb-2 font-display">
          Forgot Password
        </Typography>
        <Typography variant="body2" className="text-gray-400 text-center mb-6">
          Enter your email to request recovery details
        </Typography>

        {error && (
          <Alert severity="error" className="mb-4 bg-red-900/20 text-red-400 border border-red-900/50">
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" className="mb-4 bg-green-900/20 text-green-400 border border-green-900/50">
            If the account exists, a recovery link has been dispatched!
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

          <Button
            fullWidth
            variant="contained"
            type="submit"
            disabled={loading}
            className="py-3 bg-[#00E676] hover:bg-[#00c853] text-black font-semibold rounded-lg transition-colors mt-2"
          >
            {loading ? 'Dispatched Request...' : 'Send Verification'}
          </Button>
        </form>

        <Typography variant="body2" className="text-gray-400 text-center mt-6 text-sm">
          Remember credentials?{' '}
          <Link to="/login" className="text-[#2979FF] hover:underline">
            Login Here
          </Link>
        </Typography>
      </Card>
    </div>
  );
};
export default ForgotPassword;
