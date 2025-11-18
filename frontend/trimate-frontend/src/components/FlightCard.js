import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import FlightLandIcon from '@mui/icons-material/FlightLand';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';

export default function FlightCard({ flight }) {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [passengerInfo, setPassengerInfo] = useState({
    name: '',
    email: '',
    phone: ''
  });

  const handleBooking = () => {
    // In production, this would call your backend booking API
    alert(`Booking request sent!\n\nFlight: ${flight.airline}\nPassenger: ${passengerInfo.name}\nEmail: ${passengerInfo.email}\n\nYou will receive confirmation shortly.`);
    setBookingOpen(false);
  };

  return (
    <>
      <Card sx={{
        mb: 2,
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)'
        }
      }}>
        <CardContent>
          {/* Airline and Price Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {flight.airline}
              </Typography>
              {flight.flightNumber && (
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Flight {flight.flightNumber}
                </Typography>
              )}
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="h5" sx={{ color: '#3b82f6', fontWeight: 700 }}>
                ${flight.price}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                per person
              </Typography>
            </Box>
          </Box>

          {/* Outbound Flight */}
          <Box sx={{ mb: 2, p: 2, bgcolor: '#f8fafc', borderRadius: '8px' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <FlightTakeoffIcon sx={{ fontSize: 20, color: '#3b82f6' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Outbound
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {flight.departure.time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  {flight.departure.airport}
                </Typography>
              </Box>
              
              <Box sx={{ flex: 1, mx: 2, textAlign: 'center' }}>
                <Box sx={{ 
                  height: '2px', 
                  bgcolor: '#cbd5e1', 
                  position: 'relative',
                  mb: 1
                }}>
                  <Box sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    bgcolor: '#ffffff',
                    px: 1
                  }}>
                    <AccessTimeIcon sx={{ fontSize: 16, color: '#64748b' }} />
                  </Box>
                </Box>
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  {flight.duration}
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {flight.arrival.time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  {flight.arrival.airport}
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Return Flight (if exists) */}
          {flight.return && (
            <Box sx={{ mb: 2, p: 2, bgcolor: '#f8fafc', borderRadius: '8px' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <FlightLandIcon sx={{ fontSize: 20, color: '#ef4444' }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Return
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {flight.return.departure.time}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    {flight.return.departure.airport}
                  </Typography>
                </Box>
                
                <Box sx={{ flex: 1, mx: 2, textAlign: 'center' }}>
                  <Box sx={{ 
                    height: '2px', 
                    bgcolor: '#cbd5e1', 
                    position: 'relative',
                    mb: 1
                  }}>
                    <Box sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      bgcolor: '#ffffff',
                      px: 1
                    }}>
                      <AccessTimeIcon sx={{ fontSize: 16, color: '#64748b' }} />
                    </Box>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#64748b' }}>
                    {flight.return.duration}
                  </Typography>
                </Box>
                
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {flight.return.arrival.time}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    {flight.return.arrival.airport}
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}

          {/* Features */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            {flight.seatsAvailable && (
              <Chip 
                label={`${flight.seatsAvailable} seats available`} 
                size="small" 
                sx={{ bgcolor: '#dcfce7', color: '#16a34a', fontSize: '11px' }}
              />
            )}
            <Chip label="Economy" size="small" sx={{ fontSize: '11px' }} />
            {flight.refundable && (
              <Chip label="Refundable" size="small" sx={{ bgcolor: '#dbeafe', color: '#2563eb', fontSize: '11px' }} />
            )}
          </Box>

          {/* Book Button */}
          <Button
            variant="contained"
            fullWidth
            sx={{
              bgcolor: '#3b82f6',
              textTransform: 'none',
              fontWeight: 600,
              py: 1.5,
              '&:hover': { bgcolor: '#2563eb' }
            }}
            onClick={() => setBookingOpen(true)}
          >
            Book This Flight - ${flight.price}
          </Button>
        </CardContent>
      </Card>

      {/* Booking Dialog */}
      <Dialog open={bookingOpen} onClose={() => setBookingOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Complete Your Booking
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 3, color: '#64748b' }}>
            Flight: {flight.airline} - ${flight.price} per person
          </Typography>
          
          <TextField
            fullWidth
            label="Full Name"
            value={passengerInfo.name}
            onChange={(e) => setPassengerInfo({...passengerInfo, name: e.target.value})}
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={passengerInfo.email}
            onChange={(e) => setPassengerInfo({...passengerInfo, email: e.target.value})}
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="Phone Number"
            value={passengerInfo.phone}
            onChange={(e) => setPassengerInfo({...passengerInfo, phone: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookingOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleBooking}
            disabled={!passengerInfo.name || !passengerInfo.email}
            sx={{ bgcolor: '#3b82f6', '&:hover': { bgcolor: '#2563eb' } }}
          >
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
