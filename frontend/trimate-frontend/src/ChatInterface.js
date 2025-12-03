import React, { useState } from 'react';
import { fetchItinerary, API_BASE_URL } from './api';
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
import HomeIcon from '@mui/icons-material/Home';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';
import HotelCard from './components/HotelCardCompact';
import FlightCard from './components/FlightCardCompact';
import ActivityCard from './components/ActivityCard';
import MapView from './components/MapView';
import DestinationAutocomplete from './components/DestinationAutocomplete';
import DateRangePicker from './components/DateRangePicker';
import SaveTripButton from './components/SaveTripButton';

export default function ChatInterface({ onBackToHome }) {
  // Generate unique session ID for this chat session
  const [sessionId] = useState(() => 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9));
  
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [quickOptions, setQuickOptions] = useState([]);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showDestinationAutocomplete, setShowDestinationAutocomplete] = useState(false);
  const [showMap, setShowMap] = useState(false);
  const [currentDestination, setCurrentDestination] = useState(null);
  const [currentHotels, setCurrentHotels] = useState([]);
  const [currentActivities, setCurrentActivities] = useState([]);
  const [departureCity, setDepartureCity] = useState(null);
  const [destination, setDestination] = useState(null);
  const [travelDates, setTravelDates] = useState(null);
  const [currentTripData, setCurrentTripData] = useState(null); // For saving trip
  
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
    'Beach', 
    'Culture', 
    'Adventure', 
    'Food', 
    'Shopping', 
    'Nightlife', 
    'Nature', 
    'History', 
    'Relaxation',
    'Photography',
    'Wildlife',
    'Spirituality'
  ];
  const foodPrefOptions = ['Vegetarian', 'Non-vegetarian', 'Vegan', 'Any'];
  const cuisineOptions = ['Local cuisine', 'Indian', 'Chinese', 'Japanese', 'Thai', 'Italian', 'Any'];
  const timePreferenceOptions = ['Morning flights', 'Afternoon flights', 'Evening flights', 'Anytime'];
  
  // State for multi-select interests
  const [selectedInterests, setSelectedInterests] = React.useState([]);
  const [showInterestMultiSelect, setShowInterestMultiSelect] = React.useState(false);
  
  // State for food and cuisine preferences
  const [showFoodPreference, setShowFoodPreference] = React.useState(false);
  const [showCuisinePreference, setShowCuisinePreference] = React.useState(false);
  
  // Track UI selections for conflict detection
  const [uiSelections, setUiSelections] = React.useState({});
  
  // Show welcome message on first load
  React.useEffect(() => {
    if (messages.length === 0) {
      // Check if destination was selected from landing page
      const selectedDestination = localStorage.getItem('selectedDestination');
      if (selectedDestination) {
        // Clear it from localStorage
        localStorage.removeItem('selectedDestination');
        // Set it as input value
        setInputValue(selectedDestination);
      } else {
        // Fetch welcome message with popular destinations from backend
        fetchWelcomeMessage();
      }
    }
  }, []);

  const fetchWelcomeMessage = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: "hello", 
          session_id: sessionId 
        })
      });
      
      const data = await response.json();
      
      if (data.response) {
        const welcomeMessage = {
          message: data.response,
          sentTime: formatTimestamp(),
          sender: "TripMate",
          direction: "incoming"
        };
        setMessages([welcomeMessage]);
        setShowDestinationAutocomplete(true);
      } else {
        // Fallback to static message
        const welcomeMessage = {
          message: "👋 Welcome to TripMate! I'm your AI travel assistant.\n\nLet's plan your perfect trip! Where do you want to go?",
          sentTime: formatTimestamp(),
          sender: "TripMate",
          direction: "incoming"
        };
        setMessages([welcomeMessage]);
        setShowDestinationAutocomplete(true);
      }
    } catch (error) {
      console.error('Error fetching welcome message:', error);
      // Fallback to static message
      const welcomeMessage = {
        message: "👋 Welcome to TripMate! I'm your AI travel assistant.\n\nLet's plan your perfect trip! Where do you want to go?",
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages([welcomeMessage]);
      setShowDestinationAutocomplete(true);
    }
  };
  
  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessageContent = (msg) => {
    // Handle visual message type (hotels, itinerary cards)
    if (msg.messageType === 'visual' && msg.visualData) {
      const { stays, itineraryText, flights, flightText, activities, departureCity, destination, travelDates } = msg.visualData;
      
      // Check if this is a complete trip (has flights AND itinerary AND stays)
      const hasCompleteTrip = (flights || flightText) && itineraryText && stays && stays.length > 0;
      
      return (
        <Box>
          {/* 1. Flight Cards - First */}
          {(flights || flightText) && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                ✈️ Flight Options
              </Typography>
              <FlightCard 
                flights={flights || flightText}
                departureCity={departureCity}
                destination={destination}
                travelDates={travelDates}
              />
            </Box>
          )}
          
          {/* 2. Hotel Cards - Second */}
          {stays && stays.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                🏨 Recommended Stays
              </Typography>
              {stays.map((hotel, idx) => (
                <HotelCard key={idx} hotel={hotel} travelDates={travelDates} />
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
          
          {/* 5. Save Trip Button - Show if complete trip */}
          {hasCompleteTrip && currentTripData && (
            <Box sx={{ mt: 4, textAlign: 'center', p: 3, bgcolor: '#f0fdf4', borderRadius: '12px', border: '2px dashed #10b981' }}>
              <Typography variant="h6" sx={{ mb: 1, fontWeight: 600, color: '#059669' }}>
                ✨ Love this trip?
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, color: '#64748b' }}>
                Save it to your account and get personalized recommendations!
              </Typography>
              <SaveTripButton 
                tripData={currentTripData}
                onSaved={(savedTrip) => {
                  console.log('Trip saved:', savedTrip);
                }}
              />
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
      
      // Handle skip_recommendations (when user says "No" to saving trip)
      if (data.skip_recommendations) {
        // Clear options and pickers
        setQuickOptions([]);
        setShowDatePicker(false);
        setShowInterestMultiSelect(false);
        setShowDestinationAutocomplete(false);
        
        return {
          type: 'text',
          content: data.message || "No problem! Let me know if you'd like to plan a new trip. 🌍"
        };
      }
      
      // Check if AI needs clarification
      if (data.needs_clarification) {
        // Extract destination from memory if available (for showing map with date picker)
        if (data.memory_entities?.destination && !destination) {
          setDestination(data.memory_entities.destination);
        }
        
        // NEW: Handle structured form fields from backend
        if (data.show_form_fields) {
          console.log('📋 Showing form fields:', data.show_form_fields);
          
          // Determine which UI elements to show based on form field types
          const fields = data.show_form_fields;
          
          if (fields.destination) {
            setShowDestinationAutocomplete(true);
            setShowDatePicker(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setQuickOptions([]);
          } else if (fields.duration && fields.travel_dates) {
            setShowDatePicker(true);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setQuickOptions(durationOptions);
          } else if (fields.budget) {
            // Show budget chips only
            setQuickOptions(budgetOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
          } else if (fields.interests) {
            // Show interests multi-select
            console.log('✅ Showing interests multi-select from show_form_fields');
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(true);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
          } else if (fields.food_preference) {
            // Show food preference dropdown only
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(true);
            setShowCuisinePreference(false);
          } else if (fields.cuisine_preference) {
            // Show cuisine preference dropdown only
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(true);
          } else if (fields.departure_city) {
            setShowDestinationAutocomplete(true);
            setShowDatePicker(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setQuickOptions([]);
          }
          
          return {
            type: 'text',
            content: '🤔 ' + (data.message || 'Let me help you plan your trip!')
          };
        }
        
        // LEGACY: Handle old question-based format
        let response = '🤔 ' + (data.message || 'I need more details to plan your trip!') + '\n\n';
        if (data.questions && Array.isArray(data.questions)) {
          response += 'Please tell me:\n';
          data.questions.forEach((q, idx) => {
            response += `${idx + 1}. ${q}\n`;
          });
          
          // Set quick options based on what's being asked
          // Priority: Check FIRST question to avoid confusion when multiple questions shown
          const questionText = data.questions.join(' ').toLowerCase();
          const firstQuestion = data.questions[0]?.toLowerCase() || '';
          console.log('🔍 Question detection:', questionText); // Debug log
          console.log('🔍 First question:', firstQuestion); // Debug log
          
          if (questionText.includes('destination') || questionText.includes('where')) {
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(true); // Show autocomplete for destinations
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('days') || questionText.includes('weeks') || questionText.includes('duration')) {
            setQuickOptions(durationOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('when') || questionText.includes('travel dates') || questionText.includes('date')) {
            setQuickOptions([]);
            setShowDatePicker(true); // Show calendar for date selection
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('time') && questionText.includes('fly')) {
            setQuickOptions(timePreferenceOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('budget')) {
            setQuickOptions(budgetOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (firstQuestion.includes('interested') || firstQuestion.includes('what are you interested')) {
            // Check first question to prioritize interests over food/cuisine
            console.log('✅ Setting multi-select interests (from first question)');
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(true);
          } else if (firstQuestion.includes('food preference') || firstQuestion.includes('vegetarian') || firstQuestion.includes('vegan') || firstQuestion.includes('dietary')) {
            // First question is about food preference
            console.log('✅ Setting food preference options (from first question)');
            setQuickOptions(foodPrefOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('food preference') || questionText.includes('vegetarian') || questionText.includes('vegan') || questionText.includes('dietary')) {
            // Food preference is somewhere in the questions (numbered list)
            console.log('✅ Setting food preference options (from question list)');
            setQuickOptions(foodPrefOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('cuisine') || questionText.includes('preferred cuisine')) {
            // Cuisine question (only show if food preference not found)
            console.log('✅ Setting cuisine options');
            setQuickOptions(cuisineOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          } else if (questionText.includes('interested') || questionText.includes('interests')) {
            console.log('✅ Setting multi-select interests');
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(true);
          } else {
            console.log('⚠️ No matching question pattern found');
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
          }
        }
        return { type: 'text', content: response };
      }
      
      // Clear options and date picker when showing results
      setQuickOptions([]);
      setShowDatePicker(false);
      setShowInterestMultiSelect(false);
      
      if (data.destinations || data.stays || data.activities || data.itinerary || data.flights) {
        const destinations = data.destinations?.plan || [];
        const stays = data.stays?.stays || [];
        const activities = data.activities?.activities || [];
        const itineraryText = data.itinerary?.itinerary_text || '';
        
        // Handle both flight formats: structured array or text
        const flights = data.flights?.flights || null;  // Structured array
        const flightText = data.flights?.flight_text || '';  // Fallback text
        
        // Extract departure city and destination from memory entities
        if (data.memory_entities) {
          if (data.memory_entities.departure_city) {
            setDepartureCity(data.memory_entities.departure_city);
          }
          if (data.memory_entities.destination) {
            setDestination(data.memory_entities.destination);
          }
          if (data.memory_entities.travel_dates) {
            setTravelDates(data.memory_entities.travel_dates);
          }
        }
        
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
        
        // Prepare trip data for saving (if complete trip)
        if ((flights || flightText) && itineraryText && stays.length > 0 && data.memory_entities) {
          const tripData = {
            destination: data.memory_entities.destination || '',
            departure_city: data.memory_entities.departure_city || '',
            duration_days: parseInt(data.memory_entities.duration || '5'),
            start_date: data.memory_entities.travel_dates?.split(' to ')[0] || null,
            end_date: data.memory_entities.travel_dates?.split(' to ')[1] || null,
            budget: {
              per_day: parseInt(data.memory_entities.budget?.replace(/[^0-9]/g, '') || '100'),
              total: parseInt(data.memory_entities.budget?.replace(/[^0-9]/g, '') || '100') * parseInt(data.memory_entities.duration || '5')
            },
            preferences: {
              interests: data.memory_entities.interests || [],
              food_preference: data.memory_entities.food_preference || 'Any',
              flight_time_preference: data.memory_entities.travel_time_preference || 'Anytime'
            },
            flights: {
              outbound: flightText || JSON.stringify(flights)
            },
            stays: stays.map(hotel => ({
              name: hotel.name || hotel,
              price_per_night: 65, // Default, will be extracted from hotel string
              total_nights: parseInt(data.memory_entities.duration || '5')
            })),
            itinerary: [{
              day: 1,
              activities: [{ name: itineraryText }] // Simplified for now
            }],
            bookable_activities: activities.map(activity => ({
              name: activity.name || activity,
              description: activity.description || '',
              price: 0
            }))
          };
          
          setCurrentTripData(tripData);
        }
        
        // Return structured data for visual rendering
        return {
          type: 'visual',
          data: {
            destinations,
            stays,
            activities,
            itineraryText,
            flights,  // Structured array (if available)
            flightText,  // Fallback text
            departureCity: data.memory_entities?.departure_city,
            destination: data.memory_entities?.destination,
            travelDates: data.memory_entities?.travel_dates
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
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    const query = quickReply || inputValue;
    if (!query.trim() || loading) return;
    
    setInputValue('');
    setQuickOptions([]); // Clear options when user sends message
    setShowDatePicker(false); // Hide date picker
    setShowInterestMultiSelect(false); // Hide multi-select interests
    
    const userMessage = {
      message: query,
      sentTime: formatTimestamp(),
      sender: "user",
      direction: "outgoing"
    };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const result = await fetchItinerary(query, uiSelections);
      console.log('API result:', result);
      
      // Clear UI selections after sending (they've been used for this query)
      setUiSelections({});
      
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

  const handleDateSelection = (dateString) => {
    // Track UI selection
    setUiSelections(prev => ({
      ...prev,
      travel_dates: dateString
    }));
    // Automatically submit the selected dates
    handleSubmit({ preventDefault: () => {} }, dateString);
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
          <IconButton
            onClick={onBackToHome}
            sx={{
              mr: 2,
              color: '#ffffff',
              '&:hover': {
                bgcolor: 'rgba(255, 255, 255, 0.1)'
              }
            }}
          >
            <HomeIcon />
          </IconButton>
          
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
                onClick={(e) => {
                  // Track UI selection for budget options
                  if (budgetOptions.includes(option)) {
                    setUiSelections(prev => ({
                      ...prev,
                      budget: option
                    }));
                  }
                  handleSubmit(e, option);
                }}
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

      {/* Destination Autocomplete */}
      {showDestinationAutocomplete && (
        <Box sx={{
          bgcolor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          p: 2
        }}>
          <DestinationAutocomplete 
            onSelect={(location) => {
              if (location && location.display) {
                // Track UI selection
                setUiSelections(prev => ({
                  ...prev,
                  destination: location.display
                }));
                handleSubmit(null, location.display);
                setShowDestinationAutocomplete(false);
              }
            }}
            placeholder="Search for any destination worldwide..."
          />
        </Box>
      )}

      {/* Multi-Select Interests */}
      {showInterestMultiSelect && (
        <Box sx={{ 
          bgcolor: '#f8fafc', 
          borderTop: '1px solid #e2e8f0', 
          p: 2 
        }}>
          <Typography variant="body2" sx={{ 
            color: '#64748b', 
            fontWeight: 600, 
            mb: 1.5,
            fontSize: '0.875rem'
          }}>
            Select your interests (choose multiple):
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: 1, 
            mb: 2 
          }}>
            {interestOptions.map((option) => (
              <Chip
                key={option}
                label={option}
                onClick={() => {
                  setSelectedInterests(prev => 
                    prev.includes(option) 
                      ? prev.filter(i => i !== option)
                      : [...prev, option]
                  );
                }}
                sx={{
                  bgcolor: selectedInterests.includes(option) ? '#3b82f6' : '#ffffff',
                  color: selectedInterests.includes(option) ? '#ffffff' : '#334155',
                  border: '1.5px solid',
                  borderColor: selectedInterests.includes(option) ? '#3b82f6' : '#cbd5e1',
                  fontWeight: selectedInterests.includes(option) ? 600 : 400,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    bgcolor: selectedInterests.includes(option) ? '#2563eb' : '#f1f5f9',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
              />
            ))}
          </Box>
          <Button 
            variant="contained" 
            onClick={() => {
              if (selectedInterests.length > 0) {
                handleSubmit(null, selectedInterests.join(', '));
                setSelectedInterests([]);
                setShowInterestMultiSelect(false);
              }
            }}
            disabled={selectedInterests.length === 0}
            fullWidth
            sx={{ 
              bgcolor: '#3b82f6',
              color: '#ffffff',
              fontWeight: 600,
              py: 1.25,
              '&:hover': {
                bgcolor: '#2563eb'
              },
              '&:disabled': {
                bgcolor: '#cbd5e1',
                color: '#94a3b8'
              }
            }}
          >
            Done ({selectedInterests.length} selected)
          </Button>
        </Box>
      )}

      {/* Food Preference Dropdown */}
      {showFoodPreference && (
        <Box sx={{
          bgcolor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          p: 2
        }}>
          <Typography variant="body2" sx={{ 
            color: '#64748b', 
            fontWeight: 600,
            mb: 1.5
          }}>
            🍽️ Food Preference:
          </Typography>
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
            gap: 1
          }}>
            {foodPrefOptions.map((option, idx) => (
              <Chip
                key={idx}
                label={option}
                onClick={(e) => {
                  handleSubmit(e, option);
                  setShowFoodPreference(false);
                }}
                sx={{
                  bgcolor: '#ffffff',
                  border: '1.5px solid #cbd5e1',
                  color: '#334155',
                  fontWeight: 500,
                  fontSize: '13px',
                  height: 'auto',
                  py: 1,
                  px: 1.5,
                  '&:hover': {
                    bgcolor: '#10b981',
                    color: '#ffffff',
                    borderColor: '#10b981',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
                  },
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Cuisine Preference Dropdown */}
      {showCuisinePreference && (
        <Box sx={{
          bgcolor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          p: 2
        }}>
          <Typography variant="body2" sx={{ 
            color: '#64748b', 
            fontWeight: 600,
            mb: 1.5
          }}>
            🍜 Cuisine Preference:
          </Typography>
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
            gap: 1
          }}>
            {cuisineOptions.map((option, idx) => (
              <Chip
                key={idx}
                label={option}
                onClick={(e) => {
                  handleSubmit(e, option);
                  setShowCuisinePreference(false);
                }}
                sx={{
                  bgcolor: '#ffffff',
                  border: '1.5px solid #cbd5e1',
                  color: '#334155',
                  fontWeight: 500,
                  fontSize: '13px',
                  height: 'auto',
                  py: 1,
                  px: 1.5,
                  '&:hover': {
                    bgcolor: '#f59e0b',
                    color: '#ffffff',
                    borderColor: '#f59e0b',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)'
                  },
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Date Range Picker */}
      {showDatePicker && (
        <Box sx={{
          bgcolor: '#f8fafc',
          borderTop: '1px solid #e2e8f0',
          p: 2
        }}>
          <DateRangePicker 
            onSelectDates={handleDateSelection} 
            destination={destination}
          />
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
