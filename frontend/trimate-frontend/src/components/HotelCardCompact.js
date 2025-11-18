import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import HotelIcon from '@mui/icons-material/Hotel';
import StarIcon from '@mui/icons-material/Star';
import WifiIcon from '@mui/icons-material/Wifi';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import PoolIcon from '@mui/icons-material/Pool';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';

export default function HotelCardCompact({ hotel }) {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [bookingInfo, setBookingInfo] = useState({
    name: '',
    email: '',
    checkIn: '',
    checkOut: '',
    guests: 1
  });

  // Parse hotel string: "🏨 Hotel Name - Description, $XX/night"
  const parseHotel = (hotelStr) => {
    const match = hotelStr.match(/🏨\s*(.+?)\s*-\s*(.+?),?\s*\$(\d+)\/night/);
    if (match) {
      return {
        name: match[1].trim(),
        description: match[2].trim(),
        price: match[3]
      };
    }
    return { name: 'Hotel', description: '', price: '0' };
  };

  const hotelData = parseHotel(hotel);

  const handleBooking = () => {
    alert(`Booking request sent!\n\nHotel: ${hotelData.name}\nGuest: ${bookingInfo.name}\nCheck-in: ${bookingInfo.checkIn}\nCheck-out: ${bookingInfo.checkOut}\n\nYou will receive confirmation shortly.`);
    setBookingOpen(false);
  };

  return (
    <>
      <Card 
        sx={{
          mb: 1.5,
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            '& .expand-hint': {
              opacity: 1
            }
          }
        }}
        onClick={() => setExpanded(!expanded)}
      >
        {/* Compact View */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          p: 2,
          gap: 2
        }}>
          {/* Hotel Image Thumbnail */}
          <Box
            component="img"
            src={`https://source.unsplash.com/120x120/?hotel,${hotelData.name.replace(/\s+/g, '+')}`}
            alt={hotelData.name}
            sx={{
              width: 80,
              height: 80,
              objectFit: 'cover',
              borderRadius: '8px',
              flexShrink: 0
            }}
          />
          
          {/* Hotel Info */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6" sx={{ 
              fontWeight: 600, 
              fontSize: '16px',
              mb: 0.5,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {hotelData.name}
            </Typography>
            
            <Typography variant="body2" sx={{ 
              color: '#64748b',
              fontSize: '13px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: expanded ? 'normal' : 'nowrap',
              mb: 0.5
            }}>
              {hotelData.description}
            </Typography>
            
            {/* Quick Features */}
            {!expanded && (
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <Chip label="WiFi" size="small" sx={{ height: '20px', fontSize: '10px' }} />
                <Chip label="Breakfast" size="small" sx={{ height: '20px', fontSize: '10px' }} />
              </Box>
            )}
          </Box>
          
          {/* Price */}
          <Box sx={{ textAlign: 'right', flexShrink: 0 }}>
            <Typography variant="h5" sx={{ 
              color: '#3b82f6', 
              fontWeight: 700,
              fontSize: '20px'
            }}>
              ${hotelData.price}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b', fontSize: '11px' }}>
              per night
            </Typography>
          </Box>
        </Box>

        {/* Expanded Details */}
        {expanded && (
          <Box sx={{ px: 2, pb: 2, pt: 0 }}>
            <Divider sx={{ mb: 2 }} />
            
            {/* Full Image */}
            <Box
              component="img"
              src={`https://source.unsplash.com/400x300/?hotel,${hotelData.name.replace(/\s+/g, '+')}`}
              alt={hotelData.name}
              sx={{
                width: '100%',
                height: 200,
                objectFit: 'cover',
                borderRadius: '8px',
                mb: 2
              }}
            />
            
            {/* Rating */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <StarIcon sx={{ color: '#fbbf24', fontSize: 20 }} />
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  4.5
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                (128 reviews)
              </Typography>
            </Box>

            {/* Full Features */}
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              <Chip 
                icon={<WifiIcon />} 
                label="Free WiFi" 
                size="small" 
                sx={{ bgcolor: '#f1f5f9' }}
              />
              <Chip 
                icon={<RestaurantIcon />} 
                label="Breakfast" 
                size="small" 
                sx={{ bgcolor: '#f1f5f9' }}
              />
              <Chip 
                icon={<PoolIcon />} 
                label="Pool" 
                size="small" 
                sx={{ bgcolor: '#f1f5f9' }}
              />
            </Box>

            {/* Book Button */}
            <Button
              variant="contained"
              fullWidth
              startIcon={<HotelIcon />}
              onClick={(e) => {
                e.stopPropagation();
                setBookingOpen(true);
              }}
              sx={{
                bgcolor: '#3b82f6',
                textTransform: 'none',
                fontWeight: 600,
                py: 1.5,
                '&:hover': { bgcolor: '#2563eb' }
              }}
            >
              Book Now - ${hotelData.price}/night
            </Button>
          </Box>
        )}
        
        {/* Expand Hint */}
        {!expanded && (
          <Typography 
            className="expand-hint"
            sx={{ 
              textAlign: 'center', 
              fontSize: '11px', 
              color: '#94a3b8',
              py: 0.5,
              opacity: 0,
              transition: 'opacity 0.3s'
            }}
          >
            Click to see details & book
          </Typography>
        )}
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
            value={bookingInfo.name}
            onChange={(e) => setBookingInfo({...bookingInfo, name: e.target.value})}
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={bookingInfo.email}
            onChange={(e) => setBookingInfo({...bookingInfo, email: e.target.value})}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              label="Check-in Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={bookingInfo.checkIn}
              onChange={(e) => setBookingInfo({...bookingInfo, checkIn: e.target.value})}
            />
            
            <TextField
              fullWidth
              label="Check-out Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={bookingInfo.checkOut}
              onChange={(e) => setBookingInfo({...bookingInfo, checkOut: e.target.value})}
            />
          </Box>
          
          <TextField
            fullWidth
            label="Number of Guests"
            type="number"
            value={bookingInfo.guests}
            onChange={(e) => setBookingInfo({...bookingInfo, guests: parseInt(e.target.value)})}
            inputProps={{ min: 1, max: 10 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookingOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleBooking}
            disabled={!bookingInfo.name || !bookingInfo.email || !bookingInfo.checkIn || !bookingInfo.checkOut}
            sx={{ bgcolor: '#3b82f6', '&:hover': { bgcolor: '#2563eb' } }}
          >
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
