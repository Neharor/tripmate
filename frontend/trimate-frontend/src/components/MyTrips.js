import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import FlightIcon from '@mui/icons-material/Flight';
import HotelIcon from '@mui/icons-material/Hotel';
import CalendarIcon from '@mui/icons-material/CalendarToday';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import DeleteIcon from '@mui/icons-material/Delete';
import ShareIcon from '@mui/icons-material/Share';
import { API_BASE_URL } from '../api';

export default function MyTrips({ onBackToChat }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkLoginAndLoadTrips();
  }, []);

  const checkLoginAndLoadTrips = async () => {
    try {
      // Check if user is logged in
      const authResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
        credentials: 'include'
      });

      if (!authResponse.ok) {
        setIsLoggedIn(false);
        setLoading(false);
        return;
      }

      const userData = await authResponse.json();
      setUser(userData);
      setIsLoggedIn(true);

      // Load trips
      const tripsResponse = await fetch(`${API_BASE_URL}/api/trips`, {
        credentials: 'include'
      });

      if (!tripsResponse.ok) {
        throw new Error('Failed to load trips');
      }

      const tripsData = await tripsResponse.json();
      setTrips(tripsData.trips || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTrip = async (tripId) => {
    if (!window.confirm('Are you sure you want to delete this trip?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/trips/${tripId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to delete trip');
      }

      // Remove from local state
      setTrips(trips.filter(trip => trip.id !== tripId));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleShareTrip = async (tripId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trips/${tripId}/share`, {
        method: 'POST',
        credentials: 'include'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to share trip');
      }

      // Copy share URL to clipboard
      navigator.clipboard.writeText(data.share_url);
      alert('Share link copied to clipboard! 📋');
    } catch (err) {
      alert(`Failed to share: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isLoggedIn) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <IconButton onClick={onBackToChat} sx={{ mb: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        
        <Alert severity="info">
          <Typography variant="h6" sx={{ mb: 1 }}>
            Please log in to view your trips
          </Typography>
          <Typography variant="body2">
            You need to log in to access your saved trips. Click "Save This Trip" after planning to create an account.
          </Typography>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
        <IconButton onClick={onBackToChat} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            My Trips
          </Typography>
          {user && (
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Welcome back, {user.name}! 👋
            </Typography>
          )}
        </Box>
        <Button variant="contained" onClick={onBackToChat}>
          Plan New Trip
        </Button>
      </Box>

      {/* User Stats */}
      {user && user.stats && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: '#eff6ff', border: '1px solid #bfdbfe' }}>
              <CardContent>
                <Typography variant="h4" sx={{ color: '#2563eb', fontWeight: 700 }}>
                  {user.stats.total_trips || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Total Trips
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
              <CardContent>
                <Typography variant="h4" sx={{ color: '#16a34a', fontWeight: 700 }}>
                  {user.stats.countries_visited || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Countries Visited
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card sx={{ bgcolor: '#fef3f2', border: '1px solid #fecaca' }}>
              <CardContent>
                <Typography variant="h4" sx={{ color: '#dc2626', fontWeight: 700 }}>
                  ${user.stats.total_spent || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Total Spent
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Trips List */}
      {trips.length === 0 ? (
        <Card sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" sx={{ color: '#64748b', mb: 2 }}>
            No trips saved yet
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8', mb: 3 }}>
            Start planning your next adventure and save it here!
          </Typography>
          <Button variant="contained" onClick={onBackToChat}>
            Plan Your First Trip
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {trips.map((trip) => (
            <Grid item xs={12} md={6} key={trip.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                  }
                }}
              >
                <CardContent>
                  {/* Destination Header */}
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                        {trip.destination}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#64748b' }}>
                        From {trip.departure_city || 'Unknown'}
                      </Typography>
                    </Box>
                    <Chip 
                      label={trip.status} 
                      size="small"
                      sx={{ 
                        bgcolor: trip.status === 'finalized' ? '#dbeafe' : '#fef3c7',
                        color: trip.status === 'finalized' ? '#2563eb' : '#d97706'
                      }}
                    />
                  </Box>

                  {/* Trip Details */}
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CalendarIcon sx={{ fontSize: 18, color: '#64748b' }} />
                      <Typography variant="body2" sx={{ color: '#475569' }}>
                        {trip.duration_days} days
                      </Typography>
                    </Box>
                    
                    {trip.budget && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <AttachMoneyIcon sx={{ fontSize: 18, color: '#64748b' }} />
                        <Typography variant="body2" sx={{ color: '#475569' }}>
                          ${trip.budget.per_day}/day
                        </Typography>
                      </Box>
                    )}
                    
                    {trip.dates?.start && (
                      <Typography variant="body2" sx={{ color: '#64748b' }}>
                        {new Date(trip.dates.start).toLocaleDateString()}
                      </Typography>
                    )}
                  </Box>

                  {/* Action Buttons */}
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button 
                      size="small" 
                      variant="outlined"
                      onClick={() => {/* View trip details */}}
                      sx={{ flex: 1 }}
                    >
                      View Details
                    </Button>
                    <IconButton 
                      size="small"
                      onClick={() => handleShareTrip(trip.id)}
                      sx={{ color: '#3b82f6' }}
                    >
                      <ShareIcon />
                    </IconButton>
                    <IconButton 
                      size="small"
                      onClick={() => handleDeleteTrip(trip.id)}
                      sx={{ color: '#ef4444' }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}
