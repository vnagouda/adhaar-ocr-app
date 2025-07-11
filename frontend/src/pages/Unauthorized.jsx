import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import { useNavigate } from 'react-router-dom';

const Unauthorized = () => {
  const navigate = useNavigate();

  return (
    <Box className="min-h-screen flex flex-col justify-center items-center bg-gray-100 text-center p-8">
      <BlockIcon style={{ fontSize: 80 }} color="warning" />
      <Typography variant="h3" className="mt-4 font-bold text-gray-800">
        Unauthorized Access
      </Typography>
      <Typography variant="body1" className="mt-2 mb-6 text-gray-600">
        You do not have permission to view this page.
      </Typography>
      <Button variant="contained" color="primary" onClick={() => navigate('/')}>Go to Login</Button>
    </Box>
  );
};

export default Unauthorized;
