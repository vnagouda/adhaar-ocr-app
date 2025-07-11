import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

const Navbar = ({ onLogout, user }) => {
  return (
    <AppBar position="static" className="bg-blue-600">
      <Toolbar className="flex justify-between">
        <Typography variant="h6" className="flex items-center gap-2">
          <AccountCircleIcon /> Sayas Insurance Portal
        </Typography>

        <Box className="flex items-center gap-4">
          {user && (
            <Typography variant="body1" className="text-white">
              Logged in as: <strong>{user.role}</strong>
            </Typography>
          )}
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
