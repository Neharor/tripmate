import React, { useState } from 'react';
import { fetchItinerary } from './api';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import MapIcon from '@mui/icons-material/Map';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import HotelCard from './components/HotelCardCompact';
import FlightCard from './components/FlightCardCompact';
import ActivityCard from './components/ActivityCard';
import MapView from './components/MapView';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [quickOptions, setQuickOptions] = useState([]);
  const [showMap, setShowMap] = useState(false);
  const [currentDestination, setCurrentDestination] = useState(null);
  const [currentHotels, setCurrentHotels] = useState([]);
  const [currentActivities, setCurrentActivities] = useState([]);
  
  // Comprehensive destination options - popular countries and cities worldwide
  const destinationOptions = [
    // Asia
    'Bali, Indonesia', 'Tokyo, Japan', 'Bangkok, Thailand', 'Singapore', 'Dubai, UAE', 
    'Maldives', 'Seoul, South Korea', 'Hong Kong', 'Phuket, Thailand', 'Mumbai, India',
    'Delhi, India', 'Bali, Indonesia', 'Kuala Lumpur, Malaysia', 'Hanoi, Vietnam',
    // Europe
    'Paris, France', 'London, UK', 'Rome, Italy', 'Barcelona, Spain', 'Amsterdam, Netherlands',
    'Berlin, Germany', 'Prague, Czech Republic', 'Vienna, Austria', 'Athens, Greece', 
    'Lisbon, Portugal', 'Iceland', 'Switzerland', 'Santorini, Greece', 'Venice, Italy',
    // Americas
    'New York, USA', 'Los Angeles, USA', 'Miami, USA', 'Las Vegas, USA', 'San Francisco, USA',
    'Cancun, Mexico', 'Rio de Janeiro, Brazil', 'Buenos Aires, Argentina', 'Toronto, Canada',
    'Vancouver, Canada', 'Costa Rica', 'Peru', 'Colombia',
    // Middle East & Africa
    'Cairo, Egypt', 'Cape Town, South Africa', 'Marrakech, Morocco', 'Tel Aviv, Israel',
    'Istanbul, Turkey', 'Jordan', 'Kenya', 'Tanzania',
    // Oceania
    'Sydney, Australia', 'Melbourne, Australia', 'Auckland, New Zealand', 'Fiji', 'Bora Bora'
  ];
  
  const durationOptions = ['3 days', '5 days', '7 days', '10 days', '2 weeks', '3 weeks', '1 month'];
  const budgetOptions = ['$20/day', '$50/day', '$100/day', '$200/day', '$500/day', '$1000/day'];
  const interestOptions = [
    'Beach + Food', 
    'Culture + Food', 
    'Adventure + Food', 
    'Shopping + Food',
    'Beach', 
    'Culture', 
    'Adventure', 
    'Food', 
    'Shopping', 
    'Nightlife', 
    'Nature', 
    'History', 
    'Relaxation'
  ];
  const foodPrefOptions = ['Vegetarian', 'Non-vegetarian', 'Vegan', 'Any'];
  
  // Show welcome message on first load
  React.useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        message: "👋 Welcome to TripMate! I'm your AI travel assistant.\n\nLet's plan your perfect trip! Where do you want to go?",
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages([welcomeMessage]);
      setQuickOptions(destinationOptions);
    }
  }, []);
  
  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Parse flight text into FlightCard-compatible objects
  const parseFlights = (flightText) => {
    if (!flightText) return [];
    
    const flights = [];
    
    // Try to extract flight info with flexible regex
    const outboundMatch = flightText.match(/\*\*Outbound Flight\*\*\s*\n([^\n]+)\s*\n(?:\[([^\]]+)\]|([^→\n]+))\s*→\s*(?:\[([^\]]+)\]|([^\n]+))\s*\nTypical flight time:\s*~?(\d+)\s*hours[^\n]*\nEstimated price:\s*\$(\d+)-?\$?(\d+)?/);
    
    const returnMatch = flightText.match(/\*\*Return Flight\*\*\s*\n([^\n]+)\s*\n(?:\[([^\]]+)\]|([^→\n]+))\s*→\s*(?:\[([^\]]+)\]|([^\n]+))\s*\nTypical flight time:\s*~?(\d+)\s*hours[^\n]*\nEstimated price:\s*\$(\d+)-?\$?(\d+)?/);
    
    if (outboundMatch) {
      const airline = outboundMatch[1].trim()
        .replace('Multiple airlines available (', '')
        .replace('Multiple airlines available', 'Various Airlines')
        .replace(')', '')
        .split(',')[0]
        .trim();
      
      const fromCity = (outboundMatch[2] || outboundMatch[3] || '').trim();
      const toCity = (outboundMatch[4] || outboundMatch[5] || '').trim();
      const duration = outboundMatch[6] + ' hours';
      const minPrice = parseInt(outboundMatch[7]);
      const maxPrice = outboundMatch[8] ? parseInt(outboundMatch[8]) : minPrice;
      const avgPrice = Math.round((minPrice + maxPrice) / 2);
      
      // Skip if it's a 0-hour flight (means same origin and destination)
      if (parseInt(outboundMatch[6]) === 0) {
        return [];
      }
      
      const flight = {
        airline: airline,
        price: avgPrice,
        departure: {
          time: '10:00 AM',
          airport: fromCity
        },
        arrival: {
          time: (10 + parseInt(outboundMatch[6])) % 24 + ':00 ' + ((10 + parseInt(outboundMatch[6])) >= 12 ? 'PM' : 'AM'),
          airport: toCity
        },
        duration: duration,
        seatsAvailable: '8',
        refundable: false
      };
      
      // Add return flight if exists
      if (returnMatch) {
        const returnAirline = returnMatch[1].trim();
        const returnFromCity = (returnMatch[2] || returnMatch[3] || '').trim();
        const returnToCity = (returnMatch[4] || returnMatch[5] || '').trim();
        const returnDuration = returnMatch[6] + ' hours';
        
        flight.return = {
          departure: {
            time: '2:00 PM',
            airport: returnFromCity
          },
          arrival: {
            time: (14 + parseInt(returnMatch[6])) % 24 + ':00 ' + ((14 + parseInt(returnMatch[6])) >= 12 ? 'PM' : 'AM'),
            airport: returnToCity
          },
          duration: returnDuration
        };
      }
      
      flights.push(flight);
    }
    
    return flights;
  };

  const renderMessageContent = (msg) => {
    // Handle visual message type (hotels, itinerary cards)
    if (msg.messageType === 'visual' && msg.visualData) {
      const { stays, itineraryText, flightText, activities } = msg.visualData;
      const flights = parseFlights(flightText);
      
      return (
        <Box>
          {/* 1. Flight Cards - First */}
          {flights && flights.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                ✈️ Flight Options
              </Typography>
              {flights.map((flight, idx) => (
                <FlightCard key={idx} flight={flight} />
              ))}
            </Box>
          )}
          
          {/* 2. Hotel Cards - Second */}
          {stays && stays.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                🏨 Recommended Stays
              </Typography>
              {stays.map((hotel, idx) => (
                <HotelCard key={idx} hotel={hotel} />
              ))}
            </Box>
          )}
          
          {/* 3. Itinerary - Third */}
          {itineraryText && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                📅 Your Itinerary
              </Typography>
              <Typography sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                {itineraryText}
              </Typography>
            </Box>
          )}
          
          {/* 4. Activities (Local Places to Visit) - Fourth */}
          {activities && activities.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                🎯 Local Places to Visit
              </Typography>
              {activities.map((activity, idx) => (
                <ActivityCard key={idx} activity={activity} />
              ))}
            </Box>
          )}
        </Box>
      );
    }
    
    // Handle plain text messages
    return (
      <Typography sx={{
        fontSize: '15px',
        lineHeight: '1.6',
        fontWeight: 400
      }}>
        {msg.message}
      </Typography>
    );
  };

  const formatMessage = (rawMessage) => {
    try {
      console.log('Raw message received:', rawMessage);
      console.log('Type of message:', typeof rawMessage);
      
      if (typeof rawMessage === 'string') return rawMessage;
      
      const data = rawMessage;
      
      // Check if AI needs clarification
      if (data.needs_clarification) {
        let response = '🤔 ' + (data.message || 'I need more details to plan your trip!') + '\n\n';
        if (data.questions && Array.isArray(data.questions)) {
          response += 'Please tell me:\n';
          data.questions.forEach((q, idx) => {
            response += `${idx + 1}. ${q}\n`;
          });
          
          // Set quick options based on what's being asked
          const questionText = data.questions.join(' ').toLowerCase();
          if (questionText.includes('destination') || questionText.includes('where')) {
            setQuickOptions(destinationOptions);
          } else if (questionText.includes('days') || questionText.includes('weeks') || questionText.includes('duration')) {
            setQuickOptions(durationOptions);
          } else if (questionText.includes('budget')) {
            setQuickOptions(budgetOptions);
          } else if (questionText.includes('interested') || questionText.includes('interests')) {
            setQuickOptions(interestOptions);
          } else if (questionText.includes('food') || questionText.includes('vegetarian') || questionText.includes('preference')) {
            setQuickOptions(foodPrefOptions);
          } else {
            setQuickOptions([]);
          }
        }
        return { type: 'text', content: response };
      }
      
      // Clear options when showing results
      setQuickOptions([]);
      
      if (data.destinations || data.stays || data.activities || data.itinerary || data.flights) {
        const destinations = data.destinations?.plan || [];
        const stays = data.stays?.stays || [];
        const activities = data.activities?.activities || [];
        const itineraryText = data.itinerary?.itinerary_text || '';
        const flightText = data.flights?.flight_text || '';
        
        // Extract destination for map
        if (destinations.length > 0) {
          const destMatch = destinations[0].match(/Perfect! Let's plan your trip to (.+?) 🌴/);
          if (destMatch) {
            setCurrentDestination(destMatch[1]);
          }
        }
        
        // Store hotels and activities for map
        if (stays.length > 0) {
          setCurrentHotels(stays);
        }
        
        // Return structured data for visual rendering
        return {
          type: 'visual',
          data: {
            destinations,
            stays,
            activities,
            itineraryText,
            flightText
          }
        };
      }
      
      return { type: 'text', content: JSON.stringify(data, null, 2) };
    } catch (error) {
      console.error('Error formatting message:', error);
      return { type: 'text', content: String(rawMessage) };
    }
  };

  const handleSubmit = async (e, quickReply = null) => {
    e.preventDefault();
    const query = quickReply || inputValue;
    if (!query.trim() || loading) return;
    
    setInputValue('');
    setQuickOptions([]); // Clear options when user sends message
    
    const userMessage = {
      message: query,
      sentTime: formatTimestamp(),
      sender: "user",
      direction: "outgoing"
    };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const result = await fetchItinerary(query);
      console.log('API result:', result);
      
      const formattedMessage = formatMessage(result);
      
      const assistantMessage = {
        message: formattedMessage.type === 'text' ? formattedMessage.content : 'See visual results below',
        messageType: formattedMessage.type,
        visualData: formattedMessage.type === 'visual' ? formattedMessage.data : null,
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (e) {
      console.error('API error:', e);
      const errorMessage = {
        message: `Sorry, I encountered an error: ${e.message || 'Failed to fetch itinerary'}`,
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
      bgcolor: '#f8fafc',
      overflow: 'hidden'
    }}>
      {/* Map View */}
      {showMap && currentDestination && (
        <MapView
          destination={currentDestination}
          hotels={currentHotels}
          activities={currentActivities}
          onClose={() => setShowMap(false)}
        />
      )}
      
      {/* Header */}
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          bgcolor: '#1e293b',
          borderBottom: '1px solid #334155'
        }}
      >
        <Toolbar sx={{ py: 1 }}>
          <SmartToyIcon sx={{ mr: 2, fontSize: 32, color: '#60a5fa' }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: '-0.5px' }}>
            TripMate
          </Typography>
          
          {/* Map Toggle Button */}
          {currentDestination && (
            <Button
              variant="outlined"
              startIcon={<MapIcon />}
              onClick={() => setShowMap(!showMap)}
              sx={{
                color: '#ffffff',
                borderColor: '#475569',
                mr: 2,
                '&:hover': {
                  borderColor: '#60a5fa',
                  bgcolor: 'rgba(96, 165, 250, 0.1)'
                }
              }}
            >
              {showMap ? 'Hide Map' : 'Show Map'}
            </Button>
          )}
          
          <Typography variant="body2" sx={{ opacity: 0.8, fontWeight: 400 }}>
            AI Travel Planner
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Chat Messages Area */}
      <Box sx={{ 
        flexGrow: 1,
        overflow: 'auto',
        p: 3,
        bgcolor: '#ffffff'
      }}>
        {messages.length === 0 && (
          <Box sx={{ 
            textAlign: 'center', 
            color: '#94a3b8', 
            mt: 12,
            px: 4
          }}>
            <SmartToyIcon sx={{ fontSize: 72, opacity: 0.2, mb: 3, color: '#cbd5e1' }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 2, color: '#334155' }}>
              Welcome to TripMate
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b', maxWidth: '500px', mx: 'auto' }}>
              Your intelligent travel planning assistant. Ask me about destinations, accommodations, or create a complete itinerary.
            </Typography>
          </Box>
        )}
        
        {messages.map((msg, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              gap: 2, 
              mb: 3,
              justifyContent: msg.direction === 'outgoing' ? 'flex-end' : 'flex-start'
            }}
          >
            {msg.direction === 'incoming' && (
              <Avatar sx={{ 
                bgcolor: '#ef4444',
                width: 40,
                height: 40
              }}>
                <SmartToyIcon sx={{ fontSize: 22 }} />
              </Avatar>
            )}
            
            <Box sx={{ maxWidth: '70%' }}>
              <Paper sx={{ 
                background: msg.direction === "outgoing" ? '#3b82f6' : (msg.messageType === 'visual' ? 'transparent' : '#f1f5f9'),
                color: msg.direction === "outgoing" ? '#ffffff' : '#1e293b',
                padding: msg.messageType === 'visual' ? 0 : '14px 18px',
                borderRadius: msg.messageType === 'visual' ? 0 : '16px',
                boxShadow: msg.messageType === 'visual' ? 'none' : (msg.direction === "outgoing" 
                  ? '0 2px 8px rgba(59, 130, 246, 0.25)'
                  : '0 1px 3px rgba(0,0,0,0.08)'),
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {renderMessageContent(msg)}
              </Paper>
              <Typography sx={{
                fontSize: '13px',
                color: '#64748b',
                marginTop: '8px',
                padding: '0 6px',
                textAlign: msg.direction === "outgoing" ? 'right' : 'left',
                fontWeight: 500
              }}>
                {msg.sender === "user" ? "You" : "TripMate"} • {msg.sentTime}
              </Typography>
            </Box>
            
            {msg.direction === 'outgoing' && (
              <Avatar sx={{ 
                bgcolor: '#3b82f6',
                width: 40,
                height: 40
              }}>
                <PersonIcon sx={{ fontSize: 22 }} />
              </Avatar>
            )}
          </Box>
        ))}
        
        {loading && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2,
            color: '#64748b'
          }}>
            <Avatar sx={{ 
              bgcolor: '#ef4444',
              width: 40,
              height: 40
            }}>
              <SmartToyIcon sx={{ fontSize: 22 }} />
            </Avatar>
            <Typography variant="body1" sx={{ fontStyle: 'italic', fontWeight: 500 }}>
              TripMate is thinking...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Quick Reply Options */}
      {quickOptions.length > 0 && (
        <Box sx={{
          bgcolor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          p: 2,
          maxHeight: '200px',
          overflowY: 'auto'
        }}>
          <Typography variant="body2" sx={{ 
            color: '#64748b', 
            fontWeight: 600,
            mb: 1.5
          }}>
            {quickOptions.length > 20 ? '🌍 Select your destination:' : 'Quick select:'}
          </Typography>
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: quickOptions.length > 20 ? 'repeat(auto-fill, minmax(180px, 1fr))' : 'repeat(auto-fill, minmax(120px, 1fr))',
            gap: 1
          }}>
            {quickOptions.map((option, idx) => (
              <Chip
                key={idx}
                label={option}
                onClick={(e) => handleSubmit(e, option)}
                sx={{
                  bgcolor: '#ffffff',
                  border: '1.5px solid #cbd5e1',
                  color: '#334155',
                  fontWeight: 500,
                  fontSize: quickOptions.length > 20 ? '12px' : '13px',
                  height: 'auto',
                  py: 1,
                  px: 1.5,
                  '& .MuiChip-label': {
                    whiteSpace: 'normal',
                    textAlign: 'center'
                  },
                  '&:hover': {
                    bgcolor: '#3b82f6',
                    color: '#ffffff',
                    borderColor: '#3b82f6',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
                  },
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Input Area - Fixed at Bottom */}
      <Box 
        component="form"
        onSubmit={handleSubmit}
        sx={{ 
          borderTop: '2px solid #e2e8f0',
          bgcolor: '#ffffff',
          p: 2,
          display: 'flex',
          gap: 1,
          alignItems: 'center'
        }}
      >
        <TextField
          fullWidth
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask me about your trip..."
          disabled={loading}
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
              backgroundColor: '#ffffff',
              fontSize: '15px',
              '& fieldset': {
                borderColor: '#e2e8f0',
              },
              '&:hover fieldset': {
                borderColor: '#cbd5e1',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#3b82f6',
              }
            }
          }}
        />
        <IconButton 
          type="submit"
          disabled={loading || !inputValue.trim()}
          sx={{ 
            bgcolor: '#3b82f6',
            color: '#ffffff',
            '&:hover': {
              bgcolor: '#2563eb'
            },
            '&:disabled': {
              bgcolor: '#e2e8f0',
              color: '#94a3b8'
            },
            width: 48,
            height: 48
          }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
