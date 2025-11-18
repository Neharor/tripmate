import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import HotelIcon from '@mui/icons-material/Hotel';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import StarIcon from '@mui/icons-material/Star';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';

export default function HotelCard({ hotel }) {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [guestInfo, setGuestInfo] = useState({
    name: '',
    email: '',
    checkIn: '',
    checkOut: '',
    guests: 1
  });

  const handleBooking = () => {
    // In production, this would call your backend booking API
    alert(`Booking request sent!\n\nHotel: ${hotelData.name}\nGuest: ${guestInfo.name}\nCheck-in: ${guestInfo.checkIn}\nCheck-out: ${guestInfo.checkOut}\n\nYou will receive confirmation shortly.`);
    setBookingOpen(false);
  };

  // Parse hotel data from text format
  // Example: "🏨 Puri Lumbung Cottages - Cultural village stay, $25/night"
  const parseHotel = (hotelText) => {
    const match = hotelText.match(/🏨\s*(.+?)\s*-\s*(.+?),\s*\$(\d+)\/night/);
    if (match) {
      return {
        name: match[1].trim(),
        description: match[2].trim(),
        price: parseInt(match[3]),
        image: `https://source.unsplash.com/400x300/?hotel,${encodeURIComponent(match[1])}`
      };
    }
    return null;
  };

  const hotelData = typeof hotel === 'string' ? parseHotel(hotel) : hotel;
  
  if (!hotelData) return null;

  return (
    <>
      <Card sx={{
        display: 'flex',
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
      {/* Hotel Image */}
      <CardMedia
        component="img"
        sx={{ width: 180, objectFit: 'cover' }}
        image={hotelData.image}
        alt={hotelData.name}
      />
      
      {/* Hotel Details */}
      <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <CardContent sx={{ flex: '1 0 auto', pb: 1 }}>
          {/* Hotel Name */}
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
            {hotelData.name}
          </Typography>
          
          {/* Rating (mock data for now) */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <StarIcon sx={{ fontSize: 16, color: '#fbbf24' }} />
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              4.5
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b', ml: 0.5 }}>
              (128 reviews)
            </Typography>
          </Box>
          
          {/* Description */}
          <Typography variant="body2" sx={{ color: '#64748b', mb: 1.5 }}>
            {hotelData.description}
          </Typography>
          
          {/* Amenities */}
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1.5 }}>
            <Chip label="Free WiFi" size="small" sx={{ fontSize: '11px' }} />
            <Chip label="Breakfast" size="small" sx={{ fontSize: '11px' }} />
            <Chip label="Pool" size="small" sx={{ fontSize: '11px' }} />
          </Box>
          
          {/* Price and Book Button */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6" sx={{ color: '#3b82f6', fontWeight: 700 }}>
                ${hotelData.price}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                per night
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="small"
              sx={{
                bgcolor: '#3b82f6',
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': { bgcolor: '#2563eb' }
              }}
              onClick={() => setBookingOpen(true)}
            >
              Book Now
            </Button>
          </Box>
        </CardContent>
      </Box>
      </Card>

      {/* Booking Dialog */}
      <Dialog open={bookingOpen} onClose={() => setBookingOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>
        Book {hotelData.name}
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: 3, color: '#64748b' }}>
          ${hotelData.price} per night
        </Typography>
        
        <TextField
          fullWidth
          label="Full Name"
          value={guestInfo.name}
          onChange={(e) => setGuestInfo({...guestInfo, name: e.target.value})}
          sx={{ mb: 2 }}
        />
        
        <TextField
          fullWidth
          label="Email Address"
          type="email"
          value={guestInfo.email}
          onChange={(e) => setGuestInfo({...guestInfo, email: e.target.value})}
          sx={{ mb: 2 }}
        />
        
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            fullWidth
            label="Check-in Date"
            type="date"
            value={guestInfo.checkIn}
            onChange={(e) => setGuestInfo({...guestInfo, checkIn: e.target.value})}
            InputLabelProps={{ shrink: true }}
          />
          
          <TextField
            fullWidth
            label="Check-out Date"
            type="date"
            value={guestInfo.checkOut}
            onChange={(e) => setGuestInfo({...guestInfo, checkOut: e.target.value})}
            InputLabelProps={{ shrink: true }}
          />
        </Box>
        
        <TextField
          fullWidth
          label="Number of Guests"
          type="number"
          value={guestInfo.guests}
          onChange={(e) => setGuestInfo({...guestInfo, guests: parseInt(e.target.value)})}
          inputProps={{ min: 1, max: 10 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setBookingOpen(false)}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={handleBooking}
          disabled={!guestInfo.name || !guestInfo.email || !guestInfo.checkIn || !guestInfo.checkOut}
          sx={{ bgcolor: '#3b82f6', '&:hover': { bgcolor: '#2563eb' } }}
        >
          Confirm Booking
        </Button>
      </DialogActions>
      </Dialog>
    </>
  );
}
