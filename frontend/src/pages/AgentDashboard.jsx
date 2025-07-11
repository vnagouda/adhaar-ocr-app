import React, { useState } from 'react';
import { Typography, Box, Card, CardContent, Button, Grid, Chip } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import VisibilityIcon from '@mui/icons-material/Visibility';

const mockLeads = [
  { id: 1, name: 'Ramesh Kumar', phone: '+91 9876543210', status: 'OCR Done' },
  { id: 2, name: 'Priya Sharma', phone: '+91 9123456780', status: 'Pending' },
  { id: 3, name: 'Alok Verma', phone: '+91 9988776655', status: 'OCR Done' },
];

const AgentDashboard = () => {
  const [leads, setLeads] = useState(mockLeads);

  const handleView = (lead) => {
    console.log('View lead:', lead);
    // Navigate to CustomerRecord.jsx later
  };

  return (
    <Box className="p-8 bg-gray-50 min-h-screen">
      <Typography variant="h4" className="mb-6 font-bold text-gray-800">
        Agent Dashboard
      </Typography>

      <Grid container spacing={3}>
        {leads.map((lead) => (
          <Grid item xs={12} md={6} lg={4} key={lead.id}>
            <Card className="shadow">
              <CardContent>
                <Box className="flex items-center justify-between mb-2">
                  <Typography variant="h6" className="flex items-center gap-2">
                    <PersonIcon /> {lead.name}
                  </Typography>
                  <Chip
                    label={lead.status}
                    color={lead.status === 'OCR Done' ? 'success' : 'warning'}
                    variant="outlined"
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  📞 {lead.phone}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<VisibilityIcon />}
                  fullWidth
                  className="mt-4"
                  onClick={() => handleView(lead)}
                >
                  View Record
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AgentDashboard;
