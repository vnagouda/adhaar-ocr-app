import React from 'react';
import { Box, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import GroupIcon from '@mui/icons-material/Group';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';

const Sidebar = ({ role }) => {
  const navigate = useNavigate();

  const menuItems = role === 'admin'
    ? [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin' },
      ]
    : [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/agent' },
        { text: 'Customer Records', icon: <GroupIcon />, path: '/records' },
      ];

  return (
    <Box className="w-64 bg-white h-full shadow-md border-r">
      <List>
        {menuItems.map((item, index) => (
          <ListItem
            button
            key={index}
            onClick={() => navigate(item.path)}
            className="hover:bg-gray-100"
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default Sidebar;