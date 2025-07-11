import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Box className="min-h-screen flex flex-col justify-center items-center bg-gray-100 text-center p-8">
      <ErrorOutlineIcon style={{ fontSize: 80 }} color="error" />
      <Typography variant="h3" className="mt-4 font-bold text-gray-800">
        404 - Page Not Found
      </Typography>
      <Typography variant="body1" className="mt-2 mb-6 text-gray-600">
        Sorry, the page you're looking for doesn't exist or has been moved.
      </Typography>
      <Button variant="contained" color="primary" onClick={() => navigate('/')}>Return to Home</Button>
    </Box>
  );
};

export default NotFound;