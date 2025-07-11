import React from 'react';
import { Box } from '@mui/material';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';

const Layout = ({ children, user, onLogout }) => {
  return (
    <Box className="flex h-screen overflow-hidden">
      <Sidebar role={user?.role} />
      <Box className="flex flex-col flex-1">
        <Navbar user={user} onLogout={onLogout} />
        <Box className="flex-1 overflow-y-auto bg-gray-50 p-6">
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;