import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import SaveIcon from '@mui/icons-material/Save';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CloseIcon from '@mui/icons-material/Close';
import { API_BASE_URL } from '../api';

// ViewItineraryButton Component
function ViewItineraryButton({ tripData }) {
  const [open, setOpen] = useState(false);

  if (!tripData || !tripData.itinerary_text) return null;

  return (
    <>
      <Button
        startIcon={<VisibilityIcon />}
        variant="outlined"
        size="large"
        onClick={() => setOpen(true)}
        sx={{
          borderColor: '#3b82f6',
          color: '#3b82f6',
          fontWeight: 600,
          textTransform: 'none',
          px: 3,
          py: 1.5,
          borderRadius: '12px',
          '&:hover': {
            borderColor: '#2563eb',
            bgcolor: 'rgba(59, 130, 246, 0.04)'
          }
        }}
      >
        View Itinerary
      </Button>

      <Dialog 
        open={open} 
        onClose={() => setOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: '16px', maxHeight: '80vh' }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          bgcolor: '#f8fafc',
          borderBottom: '1px solid #e2e8f0'
        }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600, color: '#1e293b' }}>
              🗺️ Trip Itinerary
            </Typography>
            <Typography variant="subtitle2" sx={{ color: '#64748b', mt: 0.5 }}>
              {tripData.destination || 'Your Destination'}
            </Typography>
          </Box>
          <Button
            onClick={() => setOpen(false)}
            sx={{ minWidth: 'auto', p: 1, borderRadius: '8px' }}
          >
            <CloseIcon />
          </Button>
        </DialogTitle>
        
        <DialogContent sx={{ p: 0 }}>
          <Box sx={{ 
            p: 3, 
            maxHeight: '60vh', 
            overflow: 'auto',
            '& h1, & h2, & h3': { color: '#1e293b', fontWeight: 600 },
            '& p': { color: '#475569', lineHeight: 1.6 },
            '& ul, & ol': { color: '#475569' },
            '& strong': { color: '#1e293b' }
          }}>
            <div 
              dangerouslySetInnerHTML={{ 
                __html: tripData.itinerary_text
                  ?.replace(/\n/g, '<br/>')
                  ?.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  ?.replace(/#{1,6}\s*(.*?)\n/g, '<h3>$1</h3>')
                  ?.replace(/•/g, '•')
              }} 
            />
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 3, bgcolor: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
          <Button 
            onClick={() => setOpen(false)}
            variant="contained"
            sx={{ 
              bgcolor: '#3b82f6',
              px: 4,
              py: 1,
              borderRadius: '8px',
              textTransform: 'none'
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default function SaveTripButton({ tripData, onSaved }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  // Login/signup state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showSignup, setShowSignup] = useState(false);

  const handleOpen = async () => {
    setOpen(true);
    setError(null);
    setSuccess(false);
    
    // Check if user is logged in
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
      }
    } catch (err) {
      setIsLoggedIn(false);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }
      
      setIsLoggedIn(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, name })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Signup failed');
      }
      
      setIsLoggedIn(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTrip = async () => {
    setLoading(true);
    setError(null);
    
    console.log('🔍 FRONTEND: tripData type:', typeof tripData);
    console.log('🔍 FRONTEND: tripData:', tripData);
    console.log('🔍 FRONTEND: tripData.flights type:', typeof tripData.flights);
    console.log('🔍 FRONTEND: tripData.stays type:', typeof tripData.stays);
    
    try {
      // Clean trip data before sending
      const cleanTripData = { ...tripData };
      if (cleanTripData.itinerary && typeof cleanTripData.itinerary === 'string') {
        // Ensure proper character encoding
        cleanTripData.itinerary = cleanTripData.itinerary
          .replace(/[\u{1F600}-\u{1F64F}]/gu, (match) => match) // Keep emojis
          .replace(/[\u{1F300}-\u{1F5FF}]/gu, (match) => match) // Keep symbols
          .replace(/[\u{1F680}-\u{1F6FF}]/gu, (match) => match) // Keep transport
          .replace(/[\u{2600}-\u{26FF}]/gu, (match) => match);  // Keep misc symbols
      }
      
      const response = await fetch(`${API_BASE_URL}/api/trips`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json; charset=utf-8'
        },
        credentials: 'include',
        body: JSON.stringify(cleanTripData)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to save trip');
      }
      
      setSuccess(true);
      
      // Notify parent component
      if (onSaved) {
        onSaved(data.trip);
      }
      
      // Close dialog after 2 seconds
      setTimeout(() => {
        setOpen(false);
        setSuccess(false);
      }, 2000);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleOpen}
          sx={{
            bgcolor: '#10b981',
            color: '#ffffff',
            fontWeight: 600,
            textTransform: 'none',
            px: 3,
            py: 1.5,
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
            '&:hover': {
              bgcolor: '#059669',
              boxShadow: '0 6px 16px rgba(16, 185, 129, 0.4)'
            }
          }}
        >
          Save This Trip
        </Button>
        
        <ViewItineraryButton tripData={tripData} />
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {success ? '🎉 Trip Saved!' : isLoggedIn ? '💾 Save Your Trip' : '🔐 Login to Save Trip'}
        </DialogTitle>
        
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <CheckCircleIcon sx={{ fontSize: 64, color: '#10b981', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#059669', fontWeight: 600 }}>
                Your trip has been saved successfully!
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b', mt: 1 }}>
                You can view it in "My Trips" anytime.
              </Typography>
            </Box>
          )}
          
          {!success && !isLoggedIn && (
            <Box>
              <Typography variant="body2" sx={{ color: '#64748b', mb: 3 }}>
                {showSignup 
                  ? 'Create an account to save your trip and get personalized recommendations.'
                  : 'Log in to save this trip and access it anytime.'
                }
              </Typography>
              
              {showSignup && (
                <TextField
                  fullWidth
                  label="Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  sx={{ mb: 2 }}
                />
              )}
              
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                onClick={showSignup ? handleSignup : handleLogin}
                disabled={loading || !email || !password}
                sx={{ mb: 1 }}
              >
                {loading ? <CircularProgress size={24} /> : (showSignup ? 'Sign Up' : 'Log In')}
              </Button>
              
              <Button
                fullWidth
                variant="text"
                onClick={() => setShowSignup(!showSignup)}
                sx={{ textTransform: 'none' }}
              >
                {showSignup 
                  ? 'Already have an account? Log in'
                  : 'New user? Create an account'
                }
              </Button>
            </Box>
          )}
          
          {!success && isLoggedIn && (
            <Box>
              <Typography variant="body2" sx={{ color: '#64748b', mb: 2 }}>
                Save this trip to your account. You can view it later, share it with friends, and get personalized recommendations based on your travel history.
              </Typography>
              
              <Box sx={{ bgcolor: '#f1f5f9', p: 2, borderRadius: '8px' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Trip Details:
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  📍 {tripData.destination || 'Destination'}<br />
                  📅 {tripData.duration_days || 0} days<br />
                  💰 ${tripData.budget?.per_day || 0}/day
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          {!success && (
            <>
              <Button onClick={() => setOpen(false)}>Cancel</Button>
              {isLoggedIn && (
                <Button
                  variant="contained"
                  onClick={handleSaveTrip}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                  {loading ? 'Saving...' : 'Save Trip'}
                </Button>
              )}
            </>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}
