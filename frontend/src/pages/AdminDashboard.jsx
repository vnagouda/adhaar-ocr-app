import React, { useState } from 'react';
import { Typography, Button, Paper, Box } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const AdminDashboard = () => {
  const [fileName, setFileName] = useState('');

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      // Upload logic will be added later
      console.log('File selected:', file);
    }
  };

  return (
    <Box className="p-8 bg-gray-50 min-h-screen">
      <Typography variant="h4" className="mb-6 font-bold text-gray-800">
        Admin Dashboard
      </Typography>

      <Paper elevation={3} className="p-6">
        <Typography variant="h6" className="mb-4">
          Upload Lead List (.xlsx or .csv)
        </Typography>

        <Button
          variant="contained"
          component="label"
          startIcon={<UploadFileIcon />}
          className="mb-4"
        >
          Choose File
          <input
            type="file"
            accept=".xlsx, .csv"
            hidden
            onChange={handleFileUpload}
          />
        </Button>

        {fileName && (
          <Typography variant="body2" className="text-green-600">
            Selected File: {fileName}
          </Typography>
        )}

        <Button
          variant="outlined"
          startIcon={<CloudUploadIcon />}
          disabled={!fileName}
          className="mt-4"
        >
          Upload to System
        </Button>
      </Paper>
    </Box>
  );
};

export default AdminDashboard;
