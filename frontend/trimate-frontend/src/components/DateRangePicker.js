import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocationOnIcon from '@mui/icons-material/LocationOn';

export default function DateRangePicker({ onSelectDates, destination }) {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleConfirm = () => {
    if (startDate && endDate) {
      // Format: "Jan 15 to Jan 20" or "2025-01-15 to 2025-01-20"
      const formattedStart = new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      const formattedEnd = new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      const dateString = `${formattedStart} to ${formattedEnd}`;
      onSelectDates(dateString);
    }
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const isValidRange = startDate && endDate && new Date(endDate) > new Date(startDate);

  // Generate Google Maps embed URL
  const getMapEmbedUrl = () => {
    if (!destination) return null;
    const encodedDestination = encodeURIComponent(destination);
    return `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${encodedDestination}&zoom=11`;
  };

  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      {/* Date Picker Section */}
      <Grid item xs={12} md={destination ? 6 : 12}>
        <Paper 
          elevation={3}
          sx={{ 
            p: 3, 
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            height: '100%'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <CalendarTodayIcon sx={{ fontSize: 24 }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              📅 Select Your Travel Dates
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
            <Box sx={{ flex: 1, minWidth: '200px' }}>
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5, opacity: 0.9 }}>
                Start Date
              </Typography>
              <TextField
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                inputProps={{ min: getTodayDate() }}
                fullWidth
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: '8px',
                  '& .MuiInputBase-input': {
                    padding: '12px',
                    fontSize: '15px'
                  }
                }}
              />
            </Box>

            <Box sx={{ flex: 1, minWidth: '200px' }}>
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5, opacity: 0.9 }}>
                End Date
              </Typography>
              <TextField
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                inputProps={{ min: startDate || getTodayDate() }}
                fullWidth
                disabled={!startDate}
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: '8px',
                  '& .MuiInputBase-input': {
                    padding: '12px',
                    fontSize: '15px'
                  }
                }}
              />
            </Box>
          </Box>

          <Button
            variant="contained"
            fullWidth
            disabled={!isValidRange}
            onClick={handleConfirm}
            startIcon={<CheckCircleIcon />}
            sx={{
              bgcolor: isValidRange ? '#16a34a' : 'rgba(255, 255, 255, 0.3)',
              color: 'white',
              py: 1.5,
              fontSize: '15px',
              fontWeight: 600,
              textTransform: 'none',
              '&:hover': {
                bgcolor: isValidRange ? '#15803d' : 'rgba(255, 255, 255, 0.3)'
              },
              '&:disabled': {
                color: 'rgba(255, 255, 255, 0.5)'
              }
            }}
          >
            {!startDate ? 'Select start date first' : !endDate ? 'Select end date' : 'Confirm Dates ✓'}
          </Button>

          {isValidRange && (
            <Typography variant="body2" sx={{ mt: 2, textAlign: 'center', opacity: 0.9 }}>
              ✓ Selected: {new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} 
              {' → '}
              {new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              {' '}
              ({Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24))} days)
            </Typography>
          )}
        </Paper>
      </Grid>

      {/* Google Maps Section */}
      {destination && (
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={3}
            sx={{ 
              p: 2, 
              borderRadius: '16px',
              background: '#ffffff',
              height: '100%',
              minHeight: '400px'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <LocationOnIcon sx={{ fontSize: 24, color: '#ef4444' }} />
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
                📍 {destination}
              </Typography>
            </Box>
            
            <Box sx={{ 
              position: 'relative', 
              width: '100%', 
              height: 'calc(100% - 50px)',
              minHeight: '320px',
              borderRadius: '12px',
              overflow: 'hidden',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}>
              <iframe
                width="100%"
                height="100%"
                frameBorder="0"
                style={{ border: 0 }}
                src={getMapEmbedUrl()}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title={`Map of ${destination}`}
              />
            </Box>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
}
