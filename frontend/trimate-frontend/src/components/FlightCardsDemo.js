import React, { useState } from 'react';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import FlightLandIcon from '@mui/icons-material/FlightLand';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

// Mock flight data to demonstrate the enhanced flight cards
const mockFlights = [
  {
    "airline": "Emirates",
    "flight_number": "EK506",
    "aircraft": "Airbus A380",
    "departure_time": "07:30",
    "arrival_time": "11:45",
    "duration": "4h 15m",
    "price_round_trip": "$286",
    "departure_date": "Dec 9, 2025",
    "return_date": "Dec 12, 2025",
    "cabin_class": "Economy",
    "stops": "Direct",
    "booking_links": [
      {"name": "Book on Expedia", "url": "https://www.expedia.com/flights"},
      {"name": "Book on Kayak", "url": "https://www.kayak.com/flights"},
      {"name": "Book on Skyscanner", "url": "https://www.skyscanner.com/"}
    ]
  },
  {
    "airline": "Singapore Airlines",
    "flight_number": "SQ317",
    "aircraft": "Boeing 787-9",
    "departure_time": "14:45",
    "arrival_time": "19:30",
    "duration": "4h 45m",
    "price_round_trip": "$316",
    "departure_date": "Dec 9, 2025",
    "return_date": "Dec 12, 2025",
    "cabin_class": "Economy",
    "stops": "Direct",
    "booking_links": [
      {"name": "Book on Expedia", "url": "https://www.expedia.com/flights"},
      {"name": "Book on Kayak", "url": "https://www.kayak.com/flights"},
      {"name": "Book on Skyscanner", "url": "https://www.skyscanner.com/"}
    ]
  },
  {
    "airline": "Qatar Airways",
    "flight_number": "QR570",
    "aircraft": "Boeing 777-300ER",
    "departure_time": "19:15",
    "arrival_time": "23:45",
    "duration": "4h 30m",
    "price_round_trip": "$345",
    "departure_date": "Dec 9, 2025",
    "return_date": "Dec 12, 2025",
    "cabin_class": "Economy",
    "stops": "Direct",
    "booking_links": [
      {"name": "Book on Expedia", "url": "https://www.expedia.com/flights"},
      {"name": "Book on Kayak", "url": "https://www.kayak.com/flights"},
      {"name": "Book on Skyscanner", "url": "https://www.skyscanner.com/"}
    ]
  }
];

export default function FlightCardsDemo({ departureCity = "Mumbai, India", destination = "Dubai, UAE", onClose }) {
  const [selectedFlight, setSelectedFlight] = useState(null);

  return (
    <Box sx={{ p: 3, maxWidth: '900px', mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b' }}>
          ✈️ Flight Options
        </Typography>
        {onClose && (
          <Button onClick={onClose} variant="outlined">Close</Button>
        )}
      </Box>
      
      <Typography variant="h6" sx={{ mb: 2, color: '#64748b' }}>
        {departureCity} → {destination}
      </Typography>
      
      <Typography variant="body2" sx={{ mb: 3, color: '#64748b', fontWeight: 500 }}>
        ✅ Found {mockFlights.length} direct flights • Ready to book now
      </Typography>
      
      {mockFlights.map((flight, idx) => (
        <Card key={idx} sx={{ mb: 3, borderRadius: '16px', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #e2e8f0', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
          
          {/* Flight Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', p: 3, gap: 2, bgcolor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <Box sx={{ width: 56, height: 56, bgcolor: '#3b82f6', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FlightTakeoffIcon sx={{ color: '#ffffff', fontSize: 28 }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 700, fontSize: '20px', color: '#1e293b', mb: 0.5 }}>
                {flight.airline}
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
                {flight.flight_number} • {flight.cabin_class} • {flight.aircraft}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="h3" sx={{ color: '#16a34a', fontWeight: 800, fontSize: '32px', lineHeight: 1 }}>
                {flight.price_round_trip}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                round trip
              </Typography>
            </Box>
          </Box>

          {/* Flight Details */}
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              
              {/* Departure */}
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 0.5 }}>
                  {flight.departure_time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
                  {flight.departure_date}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  {departureCity.split(',')[0]}
                </Typography>
              </Box>

              {/* Flight Info */}
              <Box sx={{ textAlign: 'center', flex: 1, position: 'relative' }}>
                <Box sx={{ 
                  width: '100%', 
                  height: '2px', 
                  bgcolor: '#e2e8f0', 
                  position: 'relative',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    right: 0,
                    top: '-4px',
                    width: 0,
                    height: 0,
                    borderLeft: '8px solid #e2e8f0',
                    borderTop: '5px solid transparent',
                    borderBottom: '5px solid transparent'
                  }
                }} />
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 600, mt: 1 }}>
                  {flight.duration}
                </Typography>
                <Chip label={flight.stops} size="small" sx={{ mt: 0.5, bgcolor: '#f1f5f9', color: '#475569' }} />
              </Box>

              {/* Arrival */}
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 0.5 }}>
                  {flight.arrival_time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
                  {flight.departure_date}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  {destination.split(',')[0]}
                </Typography>
              </Box>
            </Box>

            {/* Return Flight Info */}
            <Box sx={{ bgcolor: '#f8fafc', p: 2, borderRadius: '8px', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CalendarTodayIcon sx={{ fontSize: 16, color: '#64748b' }} />
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 600 }}>
                  Return Flight: {flight.return_date}
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                Same aircraft and service level • Flexible date changes available
              </Typography>
            </Box>

            {/* Booking Buttons */}
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 2, color: '#475569' }}>
              Book this flight:
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              {flight.booking_links.map((link, linkIdx) => (
                <Button
                  key={linkIdx}
                  variant="contained"
                  endIcon={<OpenInNewIcon />}
                  onClick={() => window.open(link.url, '_blank')}
                  sx={{
                    flex: 1,
                    bgcolor: linkIdx === 0 ? '#fbbf24' : linkIdx === 1 ? '#f97316' : '#0ea5e9',
                    py: 1.5,
                    fontSize: '14px',
                    fontWeight: 600,
                    textTransform: 'none',
                    borderRadius: '8px',
                    '&:hover': {
                      bgcolor: linkIdx === 0 ? '#f59e0b' : linkIdx === 1 ? '#ea580c' : '#0284c7',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                    },
                    transition: 'all 0.2s'
                  }}
                >
                  {link.name.replace('Book on ', '')}
                </Button>
              ))}
            </Box>
          </Box>
        </Card>
      ))}
      
      <Box sx={{ mt: 4, p: 3, bgcolor: '#f0fdf4', borderRadius: '12px', border: '2px dashed #16a34a' }}>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600, color: '#15803d' }}>
          ✨ Enhanced Flight Cards Demo
        </Typography>
        <Typography variant="body2" sx={{ color: '#166534', mb: 2 }}>
          This demonstrates the visual flight cards with:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label="📅 Real dates" size="small" sx={{ bgcolor: '#dcfce7' }} />
          <Chip label="⏰ Precise timing" size="small" sx={{ bgcolor: '#dcfce7' }} />
          <Chip label="✈️ Aircraft details" size="small" sx={{ bgcolor: '#dcfce7' }} />
          <Chip label="💰 Live pricing" size="small" sx={{ bgcolor: '#dcfce7' }} />
          <Chip label="🔗 Direct booking" size="small" sx={{ bgcolor: '#dcfce7' }} />
        </Box>
      </Box>
    </Box>
  );
}