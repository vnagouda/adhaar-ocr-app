import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Divider,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

const CustomerRecord = () => {
  const [editing, setEditing] = useState(false);
  const [data, setData] = useState({
    name: 'Ramesh Kumar',
    dob: '1982-05-15',
    gender: 'Male',
    aadhaar: '1234 5678 9123',
    address: 'Flat 101, Rose Apartments, Andheri East, Mumbai',
    pincode: '400069',
  });

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const handleEditToggle = () => setEditing(!editing);
  const handleDelete = () => console.log('Delete record');
  const handleSave = () => {
    console.log('Updated data:', data);
    setEditing(false);
  };

  return (
    <Box className="p-8 bg-gray-50 min-h-screen">
      <Typography variant="h4" className="mb-6 font-bold text-gray-800">
        Customer Record
      </Typography>

      <Paper elevation={3} className="p-6">
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              label="Full Name"
              name="name"
              value={data.name}
              onChange={handleChange}
              fullWidth
              disabled={!editing}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Date of Birth"
              name="dob"
              type="date"
              value={data.dob}
              onChange={handleChange}
              fullWidth
              InputLabelProps={{ shrink: true }}
              disabled={!editing}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Gender"
              name="gender"
              value={data.gender}
              onChange={handleChange}
              fullWidth
              disabled={!editing}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Aadhaar Number"
              name="aadhaar"
              value={data.aadhaar}
              onChange={handleChange}
              fullWidth
              disabled={!editing}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Address"
              name="address"
              value={data.address}
              onChange={handleChange}
              fullWidth
              multiline
              rows={3}
              disabled={!editing}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              label="Pincode"
              name="pincode"
              value={data.pincode}
              onChange={handleChange}
              fullWidth
              disabled={!editing}
            />
          </Grid>
        </Grid>

        <Divider className="my-6" />

        <Box className="flex gap-4">
          <Button
            variant="contained"
            color={editing ? 'success' : 'primary'}
            startIcon={editing ? <SaveIcon /> : <EditIcon />}
            onClick={editing ? handleSave : handleEditToggle}
          >
            {editing ? 'Save Changes' : 'Edit Record'}
          </Button>

          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDelete}
          >
            Delete Record
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default CustomerRecord;
