import React, { useState } from 'react';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import StarIcon from '@mui/icons-material/Star';
import WifiIcon from '@mui/icons-material/Wifi';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import PoolIcon from '@mui/icons-material/Pool';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

export default function HotelCardCompact({ hotel, travelDates }) {
  const [expanded, setExpanded] = useState(false);

  // Handle both string format and object format
  const parseHotel = (hotelData) => {
    // If already an object, return it
    if (typeof hotelData === 'object' && hotelData.name) {
      return {
        name: hotelData.name || 'Hotel',
        description: hotelData.area || hotelData.amenities || '',
        price: hotelData.price || 0,
        rating: hotelData.rating || 4.5,
        amenities: hotelData.amenities || 'WiFi, Pool, Gym',
        booking_url: hotelData.booking_url || `https://www.booking.com/search.html?ss=${encodeURIComponent(hotelData.name || 'hotel')}`
      };
    }
    
    // Otherwise parse string format
    const match = hotelData.match(/🏨\s*(.+?)\s*-\s*(.+?),?\s*\$(\d+)\/night/);
    if (match) {
      return {
        name: match[1].trim(),
        description: match[2].trim(),
        price: match[3],
        rating: 4.5,
        amenities: 'WiFi, Pool, Gym',
        booking_url: `https://www.booking.com/search.html?ss=${encodeURIComponent(match[1].trim())}`
      };
    }
    return { name: 'Hotel', description: '', price: '0', rating: 4.5, amenities: '', booking_url: 'https://www.booking.com/' };
  };

  // Parse travel dates to get checkin/checkout
  const parseDates = (dates) => {
    if (!dates) return { checkin: '', checkout: '' };
    
    // Try to extract dates like "2025-12-25 to 2025-12-30" or "Jan 15 to Jan 20"
    const dateMatch = dates.match(/(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
      return { checkin: dateMatch[1], checkout: dateMatch[2] };
    }
    
    return { checkin: '', checkout: '' };
  };

  const hotelData = parseHotel(hotel);
  const { checkin, checkout } = parseDates(travelDates);

  return (
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
      onClick={(e) => {
        if (e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
          setExpanded(!expanded);
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', p: 2, gap: 2 }}>
        <Box
          component="img"
          src={`https://source.unsplash.com/120x120/?hotel,${hotelData.name.replace(/\s+/g, '+')}`}
          alt={hotelData.name}
          sx={{ width: 80, height: 80, objectFit: 'cover', borderRadius: '8px', flexShrink: 0 }}
        />
        
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '16px', mb: 0.5, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {hotelData.name}
          </Typography>
          
          <Typography variant="body2" sx={{ color: '#64748b', mb: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {hotelData.description}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" sx={{ color: '#16a34a', fontWeight: 700, fontSize: '18px' }}>
              ${hotelData.price}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              per night
            </Typography>
          </Box>
        </Box>
        
        <Typography className="expand-hint" variant="caption" 
          sx={{ color: '#3b82f6', fontSize: '11px', opacity: 0, transition: 'opacity 0.3s', position: 'absolute', right: 16, top: 8, bgcolor: '#eff6ff', px: 1.5, py: 0.5, borderRadius: '6px', fontWeight: 600 }}>
          Click to see details
        </Typography>
      </Box>

      {expanded && (
        <Box sx={{ borderTop: '1px solid #e2e8f0', p: 2, bgcolor: '#f8fafc' }}>
          <Box component="img" src={`https://source.unsplash.com/800x400/?hotel,resort,${hotelData.name.replace(/\s+/g, '+')}`} alt={hotelData.name}
            sx={{ width: '100%', height: 300, objectFit: 'cover', borderRadius: '8px', mb: 2 }} />
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 2 }}>
            <StarIcon sx={{ color: '#fbbf24', fontSize: 20 }} />
            <StarIcon sx={{ color: '#fbbf24', fontSize: 20 }} />
            <StarIcon sx={{ color: '#fbbf24', fontSize: 20 }} />
            <StarIcon sx={{ color: '#fbbf24', fontSize: 20 }} />
            <StarIcon sx={{ color: '#d1d5db', fontSize: 20 }} />
            <Typography variant="body2" sx={{ ml: 1, color: '#64748b' }}>4.5 (128 reviews)</Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip icon={<WifiIcon />} label="Free WiFi" size="small" sx={{ bgcolor: '#ffffff' }} />
            <Chip icon={<RestaurantIcon />} label="Breakfast" size="small" sx={{ bgcolor: '#ffffff' }} />
            <Chip icon={<PoolIcon />} label="Pool" size="small" sx={{ bgcolor: '#ffffff' }} />
          </Box>
          
          <Button variant="contained" fullWidth endIcon={<OpenInNewIcon />}
            onClick={(e) => {
              e.stopPropagation();
              let bookingUrl = `https://www.booking.com/search.html?ss=${encodeURIComponent(hotelData.name)}`;
              if (checkin && checkout) {
                bookingUrl += `&checkin=${checkin}&checkout=${checkout}`;
              }
              window.open(bookingUrl, '_blank');
            }}
            sx={{ bgcolor: '#3b82f6', py: 1.5, fontSize: '15px', fontWeight: 600, textTransform: 'none', '&:hover': { bgcolor: '#2563eb' } }}>
            View on Booking.com
          </Button>
        </Box>
      )}
    </Card>
  );
}
