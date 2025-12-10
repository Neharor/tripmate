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
import ItineraryCard from './components/ItineraryCard';

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

  // Parse itinerary text into structured format
  const parseItineraryText = (text, duration) => {
    const days = [];
    const dayPattern = /Day (\d+)[:\s-]*(.*?)(?=Day \d+|$)/gis;
    let match;
    
    while ((match = dayPattern.exec(text)) !== null) {
      const dayNum = parseInt(match[1]);
      const dayContent = match[2].trim();
      
      // Extract activities from day content
      const activities = dayContent
        .split(/[•\-\n]/) // Split by bullet points, dashes, or newlines
        .map(activity => activity.trim())
        .filter(activity => activity.length > 0 && !activity.match(/^\*\*|^#/))
        .slice(0, 5); // Limit to 5 activities per day
      
      if (activities.length > 0) {
        days.push({
          day: dayNum,
          date: null, // Can be calculated from start_date if needed
          activities: activities
        });
      }
    }
    
    // If no structured days found, create simple structure
    if (days.length === 0) {
      for (let i = 1; i <= (duration || 3); i++) {
        days.push({
          day: i,
          date: null,
          activities: [`Day ${i} activities`, 'Explore destination', 'Local cuisine']
        });
      }
    }
    
    return days;
  };
  
  // Popular destination options for autocomplete
  const destinationOptions = [
    'Bali, Indonesia', 'Tokyo, Japan', 'Bangkok, Thailand', 'Singapore', 'Dubai, UAE', 
    'Maldives', 'Seoul, South Korea', 'Hong Kong', 'Phuket, Thailand', 'Mumbai, India',
    'Delhi, India', 'Kuala Lumpur, Malaysia', 'Hanoi, Vietnam',
    'Paris, France', 'London, UK', 'Rome, Italy', 'Barcelona, Spain', 'Amsterdam, Netherlands',
    'Berlin, Germany', 'Prague, Czech Republic', 'Vienna, Austria', 'Athens, Greece', 
    'Lisbon, Portugal', 'Iceland', 'Switzerland', 'Santorini, Greece', 'Venice, Italy',
    'New York, USA', 'Los Angeles, USA', 'Miami, USA', 'Las Vegas, USA', 'San Francisco, USA',
    'Cancun, Mexico', 'Rio de Janeiro, Brazil', 'Buenos Aires, Argentina', 'Toronto, Canada',
    'Vancouver, Canada', 'Costa Rica', 'Peru', 'Colombia',
    'Cairo, Egypt', 'Cape Town, South Africa', 'Marrakech, Morocco', 'Tel Aviv, Israel',
    'Istanbul, Turkey', 'Jordan', 'Kenya', 'Tanzania',
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
  
  // State for travel companion selection
  const [showTravelCompanion, setShowTravelCompanion] = React.useState(false);
  
  // State for dietary preferences selection
  const [showDietaryPreference, setShowDietaryPreference] = React.useState(false);
  
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
      
      // Check if this is a complete trip (has flights AND itinerary) - hotels optional
      const hasCompleteTrip = (flights || flightText) && itineraryText;
      
      // Only show Trip Summary in the LAST message with visual data to avoid repetition
      const visualMessages = messages.filter(m => m.messageType === 'visual' && m.visualData);
      const isLastVisualMessage = visualMessages.length > 0 && visualMessages[visualMessages.length - 1] === msg;
      
      return (
        <Box>
          {/* 0. Trip Summary - Optional - Only show in last visual message */}
          {isLastVisualMessage && (destination || departureCity || travelDates) && (
            <Box sx={{ mb: 3 }}>
              <Paper sx={{ p: 2, borderRadius: 2, border: '1px solid #e2e8f0', bgcolor: '#f8fafc' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>🧭 Trip Summary</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                  {departureCity && (
                    <Chip label={`From: ${departureCity}`} sx={{ bgcolor: '#fff', border: '1px solid #e2e8f0' }} />
                  )}
                  {destination && (
                    <Chip label={`To: ${destination}`} sx={{ bgcolor: '#fff', border: '1px solid #e2e8f0' }} />
                  )}
                  {travelDates && (
                    <Chip label={`Dates: ${travelDates}`} sx={{ bgcolor: '#fff', border: '1px solid #e2e8f0' }} />
                  )}
                </Box>
              </Paper>
            </Box>
          )}

          {/* 1. Flight Cards - First */}
          {(flights || flightText) && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                ✈️ Flight Options {travelDates ? `(${travelDates})` : ''}
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
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                📅 Your Daily Itinerary
              </Typography>
              {/* Parse and render formatted itinerary cards */}
              <Box>
                {(() => {
                  // Parse structured itinerary from currentTripData if available
                  if (currentTripData && currentTripData.itinerary && Array.isArray(currentTripData.itinerary)) {
                    return currentTripData.itinerary.map((day, idx) => (
                      <ItineraryCard 
                        key={idx} 
                        dayData={day} 
                        dayNumber={day.day || idx + 1} 
                      />
                    ));
                  }
                  
                  // Fallback: Parse from itinerary text with better HTML cleaning
                  const cleanText = itineraryText
                    .replace(/<br\s*\/?>/gi, '\n') // Convert <br> tags to newlines
                    .replace(/<[^>]+>/g, '') // Remove all other HTML tags
                    .replace(/&nbsp;/g, ' ') // Replace HTML entities
                    .replace(/&amp;/g, '&')
                    .replace(/&lt;/g, '<')
                    .replace(/&gt;/g, '>')
                    .replace(/\n\s*\n/g, '\n'); // Normalize line breaks
                  
                  // Find the "Daily Itinerary" section
                  const itineraryMatch = cleanText.match(/##\s*📅\s*Daily Itinerary\s*([\s\S]*?)(?=\n##|$)/i);
                  
                  if (!itineraryMatch) {
                    // Try to find any Day patterns in the full text - more flexible pattern
                    const dayPattern = /(?:###\s*)?(?:\*\*)?Day\s*(\d+)(?:\*\*)?\s*(?:-\s*)?([^\n]*)([\s\S]*?)(?=(?:###\s*)?(?:\*\*)?Day\s*\d+|$)/gi;
                    const days = [];
                    let match;
                    
                    while ((match = dayPattern.exec(cleanText)) !== null) {
                      const dayNum = parseInt(match[1]);
                      let date = match[2] ? match[2].trim() : '';
                      const content = match[3].trim();
                      
                      // Clean up date - remove HTML remnants
                      date = date
                        .replace(/<[^>]+>/g, '')
                        .replace(/&nbsp;/g, ' ')
                        .trim();
                      
                      // Extract activities from content - more flexible patterns
                      const activities = content
                        .split('\n')
                        .map(line => line.trim())
                        .filter(line => 
                          line.startsWith('-') || 
                          line.startsWith('•') || 
                          line.startsWith('*') ||
                          (line.includes(':') && line.match(/\d+:\d+/)) // Include time-based activities
                        )
                        .map(line => line.replace(/^[-•*]\s*/, '').trim())
                        .filter(item => item.length > 0 && !item.match(/^#+/)); // Filter out headers
                      
                      if (activities.length > 0) {
                        days.push({
                          day: dayNum,
                          date: date,
                          activities: activities
                        });
                      }
                    }
                    
                    return days.map((day, idx) => (
                      <ItineraryCard 
                        key={idx} 
                        dayData={day} 
                        dayNumber={day.day} 
                      />
                    ));
                  }
                  
                  return null;
                })()}
              </Box>
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

                }}
              />
              
              {/* Plan New Trip Button */}
              <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #d1fae5' }}>
                <Typography variant="body2" sx={{ mb: 2, color: '#64748b' }}>
                  Ready for another adventure?
                </Typography>
                <Button 
                  variant="contained" 
                  size="large"
                  onClick={() => window.location.reload()}
                  sx={{ 
                    bgcolor: '#3b82f6',
                    '&:hover': { bgcolor: '#2563eb' },
                    textTransform: 'none',
                    fontWeight: 600,
                    px: 4,
                    py: 1.5,
                    borderRadius: '10px'
                  }}
                >
                  🚀 Plan New Trip
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      );
    }
    
    // Handle plain text messages with HTML support for booking carousels
    return (
      <Box sx={{
        fontSize: '15px',
        lineHeight: '1.6',
        fontWeight: 400,
        '& a': {
          color: '#1976d2',
          textDecoration: 'underline',
          position: 'relative',
          '&:hover': {
            color: '#115293',
          },
          '&[title]:hover::after': {
            content: 'attr(title)',
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            zIndex: 1000,
            marginBottom: '5px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
            pointerEvents: 'none',
          },
          '&[title]:hover::before': {
            content: '""',
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            borderWidth: '5px',
            borderStyle: 'solid',
            borderColor: 'rgba(0, 0, 0, 0.9) transparent transparent transparent',
            marginBottom: '0px',
            zIndex: 1000,
          }
        },
        '& h3': {
          marginTop: '20px',
          marginBottom: '10px',
          color: '#1976d2',
          fontWeight: 600,
        },
        '& .booking-carousel': {
          margin: '20px 0',
          padding: '15px',
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          borderRadius: '15px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        },
        '& .booking-buttons': {
          display: 'flex',
          gap: '15px',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
        },
        '& .book-btn': {
          flex: 1,
          minWidth: '200px',
          padding: '15px 20px',
          borderRadius: '12px',
          textDecoration: 'none',
          color: 'inherit',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          cursor: 'pointer',
          border: '2px solid transparent',
          background: 'rgba(255,255,255,0.9)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          '&:hover': {
            transform: 'translateY(-5px) scale(1.02)',
            boxShadow: '0 15px 40px rgba(0,0,0,0.2)',
          }
        },
        '& .expedia-btn:hover': {
          background: 'linear-gradient(135deg, #ffd700, #ffb347)',
        },
        '& .kayak-btn:hover': {
          background: 'linear-gradient(135deg, #ff6b35, #f7931e)',
        },
        '& .skyscanner-btn:hover': {
          background: 'linear-gradient(135deg, #00b4d8, #0077b6)',
        }
      }}
      dangerouslySetInnerHTML={{ 
        __html: msg.message.includes('<a ') || msg.message.includes('<div') 
          ? msg.message  // If HTML detected, don't modify
          : msg.message.replace(/\n/g, '<br/>')  // Otherwise convert newlines
      }}
      />
    );
  };

  const formatMessage = (rawMessage) => {
    try {

      
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
            setShowTravelCompanion(false);
            setQuickOptions([]);
          } else if (fields.duration && fields.travel_dates) {
            setShowDatePicker(true);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
            setQuickOptions(durationOptions);
          } else if (fields.budget) {
            // Show budget chips only
            setQuickOptions(budgetOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
          } else if (fields.interests) {
            // Show interests multi-select
            console.log('✅ Showing interests multi-select from show_form_fields');
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(true);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
          } else if (fields.food_preference) {
            // Show food preference dropdown only
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(true);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
          } else if (fields.cuisine_preference) {
            // Show cuisine preference dropdown only
            setQuickOptions([]);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(true);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
          } else if (fields.travel_companion) {
            // Show travel companion radio buttons
            const options = fields.travel_companion.options || [];
            const companionOptions = options.map(opt => opt.label || opt.value);
            setQuickOptions(companionOptions);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(true);
            setShowDietaryPreference(false);
          } else if (fields.dietary_preference) {
            // Show dietary preference multi-select
            const options = fields.dietary_preference.options || [];
            setQuickOptions(options);
            setShowDatePicker(false);
            setShowDestinationAutocomplete(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(true);

          } else if (fields.departure_city) {
            setShowDestinationAutocomplete(true);
            setShowDatePicker(false);
            setShowInterestMultiSelect(false);
            setShowFoodPreference(false);
            setShowCuisinePreference(false);
            setShowTravelCompanion(false);
            setShowDietaryPreference(false);
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
      setShowDestinationAutocomplete(false);
      setShowFoodPreference(false);
      setShowCuisinePreference(false);
      setShowTravelCompanion(false);
      setShowDietaryPreference(false);

      // Handle fallback/error responses
      if (data.agent_type === 'fallback' || data.debug_error) {
        console.error('Backend error:', data.debug_error);
        return { 
          type: 'text', 
          content: data.message || "I encountered an issue planning your trip. Let me try again - could you please confirm your travel details?" 
        };
      }

      // Client-side safety net: if backend didn't ask, infer UI from last user message
      // This preserves the old "we used to select" experience.
      // BUT: Don't show forms if trip is already complete (has visual cards or trip_complete)
      const lastUserMsg = messages.filter(m => m.sender === 'user').slice(-1)[0]?.message?.toLowerCase() || '';
      if (!data.needs_clarification && !data.show_form_fields && 
          data.agent_type !== 'visual_cards_with_data' && 
          data.agent_type !== 'trip_complete') {
        if (/where|destination|go to|travel to/.test(lastUserMsg)) {
          setShowDestinationAutocomplete(true);
        } else if (/date|when|start|end|days|duration/.test(lastUserMsg)) {
          setShowDatePicker(true);
        } else if (/budget|cost|price/.test(lastUserMsg)) {
          setQuickOptions(budgetOptions);
        } else if (/interest|interested|hobbies|activities/.test(lastUserMsg)) {
          setShowInterestMultiSelect(true);
        } else if (/vegan|vegetarian|diet|food preference/.test(lastUserMsg)) {
          setShowFoodPreference(true);
        } else if (/cuisine|food type/.test(lastUserMsg)) {
          setShowCuisinePreference(true);
        } else if (/solo|partner|family|friends|companion/.test(lastUserMsg)) {
          setShowTravelCompanion(true);
        } else if (/dietary/.test(lastUserMsg)) {
          setShowDietaryPreference(true);
        }
      }
      
      // NEW: Handle agent_type structure (visual_cards_with_data)
      if (data.agent_type === 'visual_cards_with_data' || data.agent_type === 'trip_complete') {
        // CLEAR ALL FORMS - Trip is complete, no more questions needed!
        setShowDestinationAutocomplete(false);
        setShowDatePicker(false);
        setShowInterestMultiSelect(false);
        setShowFoodPreference(false);
        setShowCuisinePreference(false);
        setShowTravelCompanion(false);
        setShowDietaryPreference(false);
        setQuickOptions([]);
        
        const flights = data.flights || [];  // Direct array
        const stays = data.stays || [];  // Direct array
        const itineraryText = data.itinerary_text || data.message || '';
        const destinations = [];
        const activities = [];
        
        // Extract departure city and destination from memory entities
        if (data.memory_entities) {
          if (data.memory_entities.departure_city) {
            setDepartureCity(data.memory_entities.departure_city);
          }
          if (data.memory_entities.destination) {
            setDestination(data.memory_entities.destination);
            setCurrentDestination(data.memory_entities.destination);
          }
          if (data.memory_entities.travel_dates) {
            setTravelDates(data.memory_entities.travel_dates);
          }
        }
        
        // Store hotels for map
        if (stays.length > 0) {
          setCurrentHotels(stays);
        }
        
        // Prepare trip data for saving
        if (flights.length > 0 && itineraryText && stays.length > 0 && data.memory_entities) {
          // Calculate duration from dates if duration is a date string
          let durationDays = parseInt(data.memory_entities.duration || '5');
          if (isNaN(durationDays) && data.memory_entities.travel_dates) {
            const dates = data.memory_entities.travel_dates.split(/ to /i);
            if (dates.length === 2) {
              const start = new Date(dates[0].trim());
              const end = new Date(dates[1].trim());
              durationDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
            }
          }
          
          // Extract budget properly
          let budgetPerDay = 100;
          const budgetStr = data.memory_entities.budget || '';
          const budgetMatch = budgetStr.match(/\$?(\d+)/);
          if (budgetMatch) {
            budgetPerDay = parseInt(budgetMatch[1]);
          }
          
          // Create structured itinerary from text
          const structuredItinerary = parseItineraryText(itineraryText, durationDays);
          
          const tripData = {
            destination: data.memory_entities.destination || '',
            departure_city: data.memory_entities.departure_city || '',
            duration_days: durationDays || 5,  // Changed from 'duration' to 'duration_days'
            start_date: data.memory_entities.travel_dates?.split(/ to /i)[0]?.trim() || null,
            end_date: data.memory_entities.travel_dates?.split(/ to /i)[1]?.trim() || null,
            budget: {
              per_day: budgetPerDay,
              total: budgetPerDay * (durationDays || 5),
              currency: 'USD'
            },
            preferences: {
              interests: data.memory_entities.interests || [],
              food_preference: data.memory_entities.food_preference || 'Any',
              travel_style: data.memory_entities.companions || 'Solo Travel'
            },
            flights: {
              departure: flights[0] ? {
                airline: flights[0].airline || 'Unknown',
                flight: flights[0].flight || '',
                price: flights[0].price || 0,
                duration: flights[0].duration || ''
              } : {}
            },
            stays: stays.map(hotel => ({
              name: hotel.name || 'Hotel',
              rating: hotel.rating || 4.5,
              price_per_night: hotel.price || 65,
              nights: durationDays || 5
            })),
            itinerary: structuredItinerary,
            itinerary_text: itineraryText,  // Keep the full text for modal display
            bookable_activities: []
          };
          
          setCurrentTripData(tripData);
        }
        
        // Return structured data for visual rendering
        return {
          type: 'visual',
          data: {
            destinations: [],
            stays,
            activities: [],
            itineraryText,
            flights,  // Structured array
            flightText: '',
            departureCity: data.memory_entities?.departure_city,
            destination: data.memory_entities?.destination,
            travelDates: data.memory_entities?.travel_dates
          }
        };
      }
      
      // LEGACY: Handle old structure
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
          // Calculate duration from dates if duration is a date string
          let durationDays = parseInt(data.memory_entities.duration || '5');
          if (isNaN(durationDays) && data.memory_entities.travel_dates) {
            const dates = data.memory_entities.travel_dates.split(/ to /i);
            if (dates.length === 2) {
              const start = new Date(dates[0].trim());
              const end = new Date(dates[1].trim());
              durationDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
            }
          }
          
          const tripData = {
            destination: data.memory_entities.destination || '',
            departure_city: data.memory_entities.departure_city || '',
            duration: durationDays || 5,
            start_date: data.memory_entities.travel_dates?.split(/ to /i)[0]?.trim() || null,
            end_date: data.memory_entities.travel_dates?.split(/ to /i)[1]?.trim() || null,
            budget_per_day: parseInt(data.memory_entities.budget?.replace(/[^0-9]/g, '') || '100'),
            budget_total: parseInt(data.memory_entities.budget?.replace(/[^0-9]/g, '') || '100') * parseInt(data.memory_entities.duration || '5'),
            interests: data.memory_entities.interests || [],
            food_preference: data.memory_entities.food_preference || 'Any',
            companions: data.memory_entities.companions || 'solo',
            flights: {
              outbound: flightText || JSON.stringify(flights)
            },
            stays: stays.map(hotel => ({
              name: hotel.name || hotel,
              price_per_night: 65, // Default, will be extracted from hotel string
              total_nights: parseInt(data.memory_entities.duration || '5')
            })),
            itinerary: data.itinerary_text || itineraryText, // Save the full itinerary text
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
    
    // OPTIMIZATION: When UI selections are present, send simple "ok" to skip entity extraction
    // The backend will use ui_selections directly instead of extracting from text
    const hasUiSelections = Object.keys(uiSelections).length > 0;
    const queryToSend = hasUiSelections ? 'ok' : query;
    
    const userMessage = {
      message: query,  // Show actual selection to user
      sentTime: formatTimestamp(),
      sender: "user",
      direction: "outgoing"
    };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const result = await fetchItinerary(queryToSend, uiSelections);  // Send "ok" with ui_selections

      
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
                  // Track UI selections based on current form context
                  if (budgetOptions.includes(option)) {
                    setUiSelections(prev => ({
                      ...prev,
                      budget: option
                    }));
                  } else if (showDietaryPreference) {
                    // Track dietary preferences (multi-select)
                    setUiSelections(prev => ({
                      ...prev,
                      dietary_preference: prev.dietary_preference 
                        ? [...prev.dietary_preference, option]
                        : [option]
                    }));
                  } else if (showCuisinePreference) {
                    // Track cuisine preference
                    setUiSelections(prev => ({
                      ...prev,
                      cuisine_preference: option
                    }));
                  } else if (showTravelCompanion) {
                    // Track travel companion
                    setUiSelections(prev => ({
                      ...prev,
                      travel_companion: option
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
