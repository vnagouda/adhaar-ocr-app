import React from 'react';
import { Card, CardContent, Typography, Button, Box, Chip } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PersonIcon from '@mui/icons-material/Person';

const CustomerCard = ({ name, phone, status, onView }) => {
  return (
    <Card className="shadow">
      <CardContent>
        <Box className="flex items-center justify-between mb-2">
          <Typography variant="h6" className="flex items-center gap-2">
            <PersonIcon /> {name}
          </Typography>
          <Chip
            label={status}
            color={status === 'OCR Done' ? 'success' : 'warning'}
            variant="outlined"
            size="small"
          />
        </Box>
        <Typography variant="body2" color="textSecondary">
          📞 {phone}
        </Typography>
        <Button
          variant="contained"
          startIcon={<VisibilityIcon />}
          fullWidth
          className="mt-4"
          onClick={onView}
        >
          View Record
        </Button>
      </CardContent>
    </Card>
  );
};

export default CustomerCard;