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
  const [validationError, setValidationError] = useState('');

  const handleConfirm = () => {
    if (startDate && endDate) {
      // Calculate duration in days
      const start = new Date(startDate);
      const end = new Date(endDate);
      const durationDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
      
      // Validate maximum duration (90 days)
      if (durationDays > 90) {
        setValidationError(`⚠️ Trip duration is ${durationDays} days! Maximum allowed is 90 days (3 months). Please select a shorter date range.`);
        return;
      }
      
      // Clear any previous errors
      setValidationError('');
      
      // Format: "Jan 15, 2025 to Jan 20, 2025"
      const formattedStart = new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      const formattedEnd = new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      const dateString = `${formattedStart} to ${formattedEnd}`;
      onSelectDates(dateString);
    }
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const isValidRange = startDate && endDate && new Date(endDate) > new Date(startDate);

  // Calculate trip duration
  const getTripDuration = () => {
    if (!startDate || !endDate) return null;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    return days;
  };

  const tripDuration = getTripDuration();
  const isTooLong = tripDuration && tripDuration > 90;

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
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5, opacity: 0.9, fontWeight: 600 }}>
                Start Date (Year: 2025)
              </Typography>
              <TextField
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                inputProps={{ min: getTodayDate() }}
                placeholder="DD/MM/YYYY"
                fullWidth
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '8px',
                  '& .MuiInputBase-input': {
                    padding: '12px',
                    fontSize: '16px',
                    fontWeight: 500
                  }
                }}
              />
              {startDate && (
                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.9, fontSize: '12px' }}>
                  Selected: {new Date(startDate).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                </Typography>
              )}
            </Box>

            <Box sx={{ flex: 1, minWidth: '200px' }}>
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5, opacity: 0.9, fontWeight: 600 }}>
                End Date (Year: 2025)
              </Typography>
              <TextField
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                inputProps={{ min: startDate || getTodayDate() }}
                placeholder="DD/MM/YYYY"
                fullWidth
                disabled={!startDate}
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '8px',
                  '& .MuiInputBase-input': {
                    padding: '12px',
                    fontSize: '16px',
                    fontWeight: 500
                  }
                }}
              />
              {endDate && (
                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.9, fontSize: '12px' }}>
                  Selected: {new Date(endDate).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Validation Error Message */}
          {validationError && (
            <Box sx={{
              mt: 2,
              p: 2,
              bgcolor: 'rgba(239, 68, 68, 0.2)',
              border: '2px solid rgba(239, 68, 68, 0.5)',
              borderRadius: '12px'
            }}>
              <Typography variant="body2" sx={{ 
                color: '#fff',
                fontWeight: 600,
                textAlign: 'center'
              }}>
                {validationError}
              </Typography>
            </Box>
          )}

          {/* Trip Duration Display */}
          {isValidRange && tripDuration && (
            <Box sx={{
              mt: 2,
              p: 2,
              bgcolor: isTooLong ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
              border: `2px solid ${isTooLong ? 'rgba(239, 68, 68, 0.5)' : 'rgba(34, 197, 94, 0.5)'}`,
              borderRadius: '12px'
            }}>
              <Typography variant="body2" sx={{ 
                color: '#fff',
                fontWeight: 600,
                textAlign: 'center'
              }}>
                {isTooLong ? '⚠️' : '✅'} Trip Duration: <strong>{tripDuration} days</strong>
                {isTooLong && ' (Maximum: 90 days)'}
              </Typography>
            </Box>
          )}

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
