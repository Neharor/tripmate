import React from 'react';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import FlightLandIcon from '@mui/icons-material/FlightLand';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

export default function FlightCardCompact({ flights, departureCity, destination, travelDates }) {
  // If flights is an array of structured data, use that
  // Otherwise fall back to old text format
  const isStructured = Array.isArray(flights);

  if (!isStructured) {
    // Fallback: Show simple card with booking links
    const extractPrice = (flightStr) => {
      const priceMatch = flightStr.match(/Estimated Total:\*\*\s*\$(\d+)-\$?(\d+)?/);
      if (priceMatch) {
        const min = parseInt(priceMatch[1]);
        const max = priceMatch[2] ? parseInt(priceMatch[2]) : min;
        return `$${min}-$${max}`;
      }
      return 'View Prices';
    };

    const getGoogleFlightsUrl = () => {
      if (departureCity && destination) {
        const origin = departureCity.split(',')[0].trim();
        const dest = destination.split(',')[0].trim();
        return `https://www.google.com/flights?hl=en#flt=${encodeURIComponent(origin)}.${encodeURIComponent(dest)}`;
      }
      return 'https://www.google.com/flights';
    };

    return (
      <Card sx={{ mb: 2, borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', p: 2.5, gap: 2, borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ width: 50, height: 50, bgcolor: '#3b82f6', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FlightTakeoffIcon sx={{ color: '#ffffff', fontSize: 28 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '18px', mb: 0.3 }}>
              {departureCity && destination ? `${departureCity.split(',')[0]} → ${destination.split(',')[0]}` : 'Flight Options'}
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>Round trip · Economy</Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="h5" sx={{ color: '#16a34a', fontWeight: 700 }}>{extractPrice(flights)}</Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>estimated</Typography>
          </Box>
        </Box>
        <Box sx={{ p: 2.5, bgcolor: '#f8fafc' }}>
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5, color: '#475569' }}>
            Compare prices and book:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1.5 }}>
            <Button variant="contained" endIcon={<OpenInNewIcon />} onClick={() => window.open(getGoogleFlightsUrl(), '_blank')}
              sx={{ flex: 1, bgcolor: '#3b82f6', py: 1.3, fontSize: '14px', fontWeight: 600, textTransform: 'none', '&:hover': { bgcolor: '#2563eb' } }}>
              Google Flights
            </Button>
            <Button variant="outlined" endIcon={<OpenInNewIcon />} onClick={() => window.open('https://www.skyscanner.com', '_blank')}
              sx={{ flex: 1, borderColor: '#0770E3', color: '#0770E3', py: 1.3, fontSize: '14px', fontWeight: 600, textTransform: 'none', '&:hover': { borderColor: '#0554B3', bgcolor: '#f0f7ff' } }}>
              Skyscanner
            </Button>
          </Box>
        </Box>
      </Card>
    );
  }

  // New: Show structured flight cards with complete details
  return (
    <Box>
      <Typography variant="body2" sx={{ mb: 2, color: '#64748b', fontWeight: 500 }}>
        ✅ Found {flights.length} direct flight{flights.length > 1 ? 's' : ''} • Ready to book now
      </Typography>
      
      {flights.map((flight, idx) => (
        <Card key={idx} sx={{ mb: 2, borderRadius: '12px', boxShadow: '0 2px 12px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
          {/* Flight Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2, gap: 2, bgcolor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <Box sx={{ width: 48, height: 48, bgcolor: '#3b82f6', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FlightTakeoffIcon sx={{ color: '#ffffff', fontSize: 26 }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '17px', color: '#1e293b', mb: 0.3 }}>
                {flight.airline}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                {flight.flight_number} · {flight.cabin_class} · {flight.departure_date || 'Flexible dates'}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="h4" sx={{ color: '#16a34a', fontWeight: 800, fontSize: '28px', lineHeight: 1 }}>
                ${flight.price_round_trip || flight.price_one_way * 2}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                round trip
              </Typography>
            </Box>
          </Box>

          {/* Outbound Flight */}
          <Box sx={{ p: 2.5, borderBottom: '1px solid #e2e8f0' }}>
            <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, mb: 1.5, display: 'block', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              ✈️ Outbound Flight
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              {/* Departure */}
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#1e293b', mb: 0.5, fontSize: '32px' }}>
                  {flight.departure_time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 600 }}>
                  {departureCity ? departureCity.split(',')[0] : 'Departure'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                  {flight.departure_date || ''}
                </Typography>
              </Box>

              {/* Duration */}
              <Box sx={{ flex: 1.5, mx: 3, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                  <Box sx={{ height: '3px', flex: 1, bgcolor: '#cbd5e1', borderRadius: '2px' }} />
                  <FlightTakeoffIcon sx={{ color: '#3b82f6', fontSize: 22 }} />
                  <Box sx={{ height: '3px', flex: 1, bgcolor: '#cbd5e1', borderRadius: '2px' }} />
                </Box>
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 700, fontSize: '15px' }}>
                  {flight.duration}
                </Typography>
                {flight.stops === 0 ? (
                  <Chip label="Direct • Non-stop" size="small" sx={{ mt: 1, bgcolor: '#dcfce7', color: '#16a34a', fontWeight: 700, fontSize: '11px' }} />
                ) : (
                  <Chip label={`${flight.stops} stop${flight.stops > 1 ? 's' : ''}`} size="small" sx={{ mt: 1, bgcolor: '#fef3c7', color: '#d97706', fontWeight: 700 }} />
                )}
              </Box>

              {/* Arrival */}
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#1e293b', mb: 0.5, fontSize: '32px' }}>
                  {flight.arrival_time}
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 600 }}>
                  {destination ? destination.split(',')[0] : 'Arrival'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                  Same day
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Return Flight Info */}
          <Box sx={{ px: 2.5, py: 1.5, bgcolor: '#f8fafc' }}>
            <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600 }}>
              🔄 Return flight: {flight.return_date || 'Based on your dates'} • Same airline • Similar schedule
            </Typography>
          </Box>

          {/* Book Button */}
          <Box sx={{ p: 2.5, bgcolor: '#ffffff' }}>
            <Button 
              variant="contained" 
              fullWidth 
              size="large"
              endIcon={<OpenInNewIcon />}
              onClick={() => window.open(flight.booking_url, '_blank')}
              sx={{ 
                bgcolor: '#16a34a', 
                py: 1.8, 
                fontSize: '16px', 
                fontWeight: 800, 
                textTransform: 'none',
                boxShadow: '0 4px 14px rgba(22, 163, 74, 0.4)',
                borderRadius: '10px',
                '&:hover': { 
                  bgcolor: '#15803d',
                  boxShadow: '0 6px 20px rgba(22, 163, 74, 0.5)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.2s'
              }}>
              Book Now on {flight.airline} Website
            </Button>
            
            <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: '#64748b', mt: 1.5 }}>
              💳 Pay directly to airline • Instant confirmation • ${flight.price_one_way || Math.round(flight.price_round_trip / 2)} one-way
            </Typography>
          </Box>
        </Card>
      ))}
      
      {/* Alternative booking sites */}
      <Box sx={{ mt: 2, p: 2, bgcolor: '#f8fafc', borderRadius: '8px' }}>
        <Typography variant="body2" sx={{ color: '#64748b', mb: 1.5, fontWeight: 600 }}>
          Or compare prices on:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" size="small" endIcon={<OpenInNewIcon />}
            onClick={() => window.open(`https://www.skyscanner.com/transport/flights/${departureCity?.split(',')[0]}/${destination?.split(',')[0]}`, '_blank')}
            sx={{ borderColor: '#0770E3', color: '#0770E3', textTransform: 'none', fontWeight: 600 }}>
            Skyscanner
          </Button>
          <Button variant="outlined" size="small" endIcon={<OpenInNewIcon />}
            onClick={() => window.open(`https://www.kayak.com/flights/${departureCity?.split(',')[0]}-${destination?.split(',')[0]}`, '_blank')}
            sx={{ borderColor: '#FF690F', color: '#FF690F', textTransform: 'none', fontWeight: 600 }}>
            Kayak
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
