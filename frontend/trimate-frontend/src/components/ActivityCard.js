import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import InfoIcon from '@mui/icons-material/Info';

export default function ActivityCard({ activity }) {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [bookingData, setBookingData] = useState({
    name: '',
    email: '',
    phone: '',
    date: '',
    guests: 1
  });

  // Parse activity from text format
  // Example: "🎫 Tanah Lot Temple Sunset Tour - Skip lines, guided tour, sunset views ($30-45)"
  const parseActivity = (activityText) => {
    // Remove emoji and split
    const cleaned = activityText.replace(/^[🎫🎯🌊🍜🏛️🚶]\s*/, '').trim();
    
    // Extract name (before dash)
    const dashIndex = cleaned.indexOf(' - ');
    if (dashIndex === -1) {
      return {
        name: cleaned,
        description: '',
        price: ''
      };
    }
    
    const name = cleaned.substring(0, dashIndex).trim();
    const rest = cleaned.substring(dashIndex + 3).trim();
    
    // Extract price (in parentheses at end)
    const priceMatch = rest.match(/\((\$[\d-]+)\)$/);
    const price = priceMatch ? priceMatch[1] : '';
    const description = priceMatch ? rest.substring(0, rest.lastIndexOf('(')).trim() : rest;
    
    return { name, description, price };
  };

  const activityData = typeof activity === 'string' ? parseActivity(activity) : activity;
  
  if (!activityData) return null;

  const handleBooking = () => {
    // TODO: Send booking to backend API
    alert(`Booking confirmed for ${activityData.name}!\n\nDetails:\nName: ${bookingData.name}\nEmail: ${bookingData.email}\nDate: ${bookingData.date}\nGuests: ${bookingData.guests}`);
    setBookingOpen(false);
    setBookingData({ name: '', email: '', phone: '', date: '', guests: 1 });
  };

  return (
    <>
      <Card sx={{
        mb: 2,
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        border: '2px solid #f1f5f9',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 16px rgba(59, 130, 246, 0.15)',
          borderColor: '#3b82f6'
        }
      }}>
        <Box sx={{ display: 'flex' }}>
          {/* Icon */}
          <Box sx={{
            width: 80,
            bgcolor: '#3b82f6',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            p: 2
          }}>
            <ConfirmationNumberIcon sx={{ color: '#ffffff', fontSize: 40 }} />
          </Box>
          
          {/* Activity Details */}
          <Box sx={{ flexGrow: 1 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5, fontSize: '16px', color: '#1e293b' }}>
                {activityData.name}
              </Typography>
              
              {activityData.description && (
                <Typography variant="body2" sx={{ color: '#64748b', mb: 1.5, lineHeight: 1.5 }}>
                  {activityData.description}
                </Typography>
              )}
              
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                {activityData.price && (
                  <Chip
                    icon={<AttachMoneyIcon sx={{ fontSize: 14 }} />}
                    label={activityData.price}
                    size="small"
                    sx={{
                      bgcolor: '#dcfce7',
                      color: '#16a34a',
                      fontSize: '12px',
                      fontWeight: 600
                    }}
                  />
                )}
                
                <Chip
                  icon={<InfoIcon sx={{ fontSize: 14 }} />}
                  label="Pre-booking recommended"
                  size="small"
                  sx={{
                    bgcolor: '#fef3c7',
                    color: '#d97706',
                    fontSize: '11px',
                    fontWeight: 600
                  }}
                />
                
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => setBookingOpen(true)}
                  sx={{
                    ml: 'auto',
                    bgcolor: '#3b82f6',
                    fontSize: '12px',
                    fontWeight: 600,
                    textTransform: 'none',
                    px: 2,
                    '&:hover': {
                      bgcolor: '#2563eb'
                    }
                  }}
                >
                  Book Now
                </Button>
              </Box>
            </CardContent>
          </Box>
        </Box>
      </Card>

      {/* Booking Dialog */}
      <Dialog open={bookingOpen} onClose={() => setBookingOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600, fontSize: '18px' }}>
          Book: {activityData.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2, color: '#64748b' }}>
            {activityData.description}
          </Typography>
          
          {activityData.price && (
            <Typography variant="body1" sx={{ mb: 3, fontWeight: 600, color: '#16a34a' }}>
              Price: {activityData.price}
            </Typography>
          )}
          
          <TextField
            fullWidth
            label="Full Name"
            value={bookingData.name}
            onChange={(e) => setBookingData({ ...bookingData, name: e.target.value })}
            sx={{ mb: 2 }}
            required
          />
          
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={bookingData.email}
            onChange={(e) => setBookingData({ ...bookingData, email: e.target.value })}
            sx={{ mb: 2 }}
            required
          />
          
          <TextField
            fullWidth
            label="Phone"
            type="tel"
            value={bookingData.phone}
            onChange={(e) => setBookingData({ ...bookingData, phone: e.target.value })}
            sx={{ mb: 2 }}
            required
          />
          
          <TextField
            fullWidth
            label="Preferred Date"
            type="date"
            value={bookingData.date}
            onChange={(e) => setBookingData({ ...bookingData, date: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ mb: 2 }}
            required
          />
          
          <TextField
            fullWidth
            label="Number of Guests"
            type="number"
            value={bookingData.guests}
            onChange={(e) => setBookingData({ ...bookingData, guests: parseInt(e.target.value) })}
            inputProps={{ min: 1, max: 20 }}
            required
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setBookingOpen(false)} sx={{ color: '#64748b' }}>
            Cancel
          </Button>
          <Button 
            onClick={handleBooking}
            variant="contained"
            disabled={!bookingData.name || !bookingData.email || !bookingData.date}
            sx={{
              bgcolor: '#3b82f6',
              '&:hover': { bgcolor: '#2563eb' }
            }}
          >
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
