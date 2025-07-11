import React, { useState } from 'react';
import { TextField, Button, Paper, Typography, Box } from '@mui/material';
import { LockOutlined } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Login = ({ onLogin }) => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const mockCredentials = {
      admin: {
        email: 'admin@sayas.in',
        password: 'admin123',
        role: 'admin',
      },
      agent: {
        email: 'agent@sayas.in',
        password: 'agent123',
        role: 'agent',
      },
    };

    if (
      form.email === mockCredentials.admin.email &&
      form.password === mockCredentials.admin.password
    ) {
      onLogin({ role: 'admin' });
      navigate('/admin');
    } else if (
      form.email === mockCredentials.agent.email &&
      form.password === mockCredentials.agent.password
    ) {
      onLogin({ role: 'agent' });
      navigate('/agent');
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <Box className="min-h-screen bg-gray-100 flex items-center justify-center">
      <Paper elevation={6} className="p-8 w-full max-w-md">
        <Box className="flex flex-col items-center">
          <LockOutlined fontSize="large" color="primary" />
          <Typography variant="h5" className="mt-2 mb-4 font-semibold">
            Sign In
          </Typography>
          <form onSubmit={handleSubmit} className="w-full">
            <TextField
              label="Email"
              name="email"
              value={form.email}
              onChange={handleChange}
              fullWidth
              required
              className="mb-4"
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              fullWidth
              required
              className="mb-6"
            />
            {error && (
              <Typography variant="body2" className="text-red-500 mb-4">
                {error}
              </Typography>
            )}
            <Button type="submit" variant="contained" color="primary" fullWidth>
              Login
            </Button>
          </form>
        </Box>
      </Paper>
    </Box>
  );
};

export default Login;
