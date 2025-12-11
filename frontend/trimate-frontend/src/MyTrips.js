import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import ItineraryCard from './components/ItineraryCard';
import './styles/MyTrips.css';

const MyTrips = ({ onBackToHome }) => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState(null);

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5002/api/trips', {
        withCredentials: true
      });
      
      // Check if there's a database error but empty trips returned
      if (response.data.error && response.data.trips.length === 0) {
        setError('⚠️ Database temporarily unavailable. Your saved trips will appear here once the connection is restored.');
        setTrips([]);
      } else {
        setTrips(response.data.trips || []);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching trips:', err);
      if (err.response?.status === 401) {
        setError('🔒 Please log in to view your saved trips.');
      } else {
        setError('⚠️ Unable to load trips. The database connection is currently unavailable.');
      }
      setTrips([]);
    } finally {
      setLoading(false);
    }
  };

  const deleteTrip = async (tripId) => {
    if (!window.confirm('Are you sure you want to delete this trip?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:5002/api/trips/${tripId}`, {
        withCredentials: true
      });
      setTrips(trips.filter(trip => trip.id !== tripId));
    } catch (err) {
      console.error('Error deleting trip:', err);
      alert('Failed to delete trip. Please try again.');
    }
  };

  const openItineraryModal = (trip) => {
    setSelectedTrip(trip);
    setModalOpen(true);
  };

  const closeItineraryModal = () => {
    setModalOpen(false);
    setSelectedTrip(null);
  };

  // Helper function to clean corrupted characters
  const cleanCorruptedText = (text) => {
    if (!text) return text;
    
    // Replace corrupted character sequences with proper emojis/text
    let cleaned = text
      // Common emoji patterns that get corrupted
      .replace(/�\s*�/g, '🛬') // Plane landing
      .replace(/�\s*�️/g, '🍽️') // Fork and knife
      .replace(/�\s*�/g, '🗺️') // World map  
      .replace(/☀\s*️/g, '☀️') // Sun
      .replace(/�\s*�/g, '🎯') // Target
      .replace(/�\s*�/g, '🛍️') // Shopping bags
      .replace(/�\s*�/g, '📦') // Package
      .replace(/✈\s*️/g, '✈️') // Airplane
      .replace(/�\s*�/g, '🌙') // Moon
      .replace(/�\s*�/g, '🌅') // Sunrise
      // Common text patterns
      .replace(/�\s*\*/g, '**') // Bold markers
      .replace(/\*\s*�/g, '**') // Bold markers reverse
      .replace(/�\s*C/g, 'C') // "Comfortable" word start
      .replace(/�\s*W/g, 'W') // "Weather" word start  
      .replace(/�\s*B/g, 'B') // "Best" word start
      .replace(/�\s*S/g, 'S') // Various words starting with S
      .replace(/�\s*R/g, 'R') // Various words starting with R
      // Clean up remaining corruption
      .replace(/�+/g, ' ') // Replace remaining corrupted chars with space
      .replace(/\s{2,}/g, ' ') // Normalize multiple spaces
      .trim();
    
    // Fix specific word splitting issues
    const wordFixes = {
      'C omfortable': 'Comfortable',
      'W eather': 'Weather', 
      'C amera': 'Camera',
      'T ravel': 'Travel',
      'B asic': 'Basic',
      'S unscreen': 'Sunscreen',
      'R eusable': 'Reusable',
      'B each': 'Beach',
      'W aterproof': 'Waterproof'
    };
    
    Object.entries(wordFixes).forEach(([corrupted, proper]) => {
      cleaned = cleaned.replace(new RegExp(corrupted, 'g'), proper);
    });
    
    // COMPLETELY REMOVE unwanted content patterns
    const removePatterns = [
      /Best time to visit.*?\n/gi,
      /Getting around.*?\n/gi,
      /Currency.*?\n/gi,
      /Language.*?\n/gi,
      /Safety.*?\n/gi,
      /Food & Dining.*?\$\d+.*?\n/gi,
      /Comfortable walking shoes.*?\n/gi,
      /Weather-appropriate clothing.*?\n/gi,
      /Camera\/phone for photos.*?\n/gi,
      /Travel adapter.*?\n/gi,
      /Basic first aid kit.*?\n/gi,
      /Sunscreen and sunglasses.*?\n/gi,
      /Reusable water bottle.*?\n/gi,
      /Beach towel.*?\n/gi,
      /Waterproof bag.*?\n/gi
    ];
    
    removePatterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, '');
    });
    
    return cleaned;
  };

  const parseItinerary = (itinerary) => {
    // Handle array with nested structure
    if (Array.isArray(itinerary)) {
      // Check if it's already in the right format
      if (itinerary.length > 0 && itinerary[0].activities && Array.isArray(itinerary[0].activities)) {
        // Check if activities contain a single string with full itinerary
        if (itinerary[0].activities.length === 1 && typeof itinerary[0].activities[0] === 'object' && itinerary[0].activities[0].name) {
          // Extract the string and parse it
          return parseItinerary(cleanCorruptedText(itinerary[0].activities[0].name));
        }
      }
      // If it's already properly structured, return as is but clean text
      if (itinerary.length > 1 || (itinerary.length === 1 && itinerary[0].day && itinerary[0].activities && itinerary[0].activities.length > 1)) {
        return itinerary.map(day => ({
          ...day,
          activities: day.activities ? day.activities.map(activity => cleanCorruptedText(activity)) : []
        }));
      }
    }
    
    if (typeof itinerary === 'string') {
      // Clean the text first
      const cleanText = cleanCorruptedText(itinerary);
      // Parse string itinerary into structured format
      const days = [];
      // Try multiple patterns for day headers
      let dayMatches = cleanText.match(/\*\*Day \d+:.*?\*\*/g);
      
      // Fallback pattern for corrupted headers
      if (!dayMatches || dayMatches.length === 0) {
        dayMatches = cleanText.match(/Day \d+/g);
      }
      
      if (dayMatches) {
        dayMatches.forEach((dayHeader, idx) => {
          const dayNum = idx + 1;
          const dayTitle = dayHeader.replace(/\*\*/g, '').trim();
          
          // Find content between this day and the next day (or any end marker)
          const startIdx = cleanText.indexOf(dayHeader);
          let endIdx = cleanText.length;
          
          // Look for next day first
          if (dayMatches[idx + 1]) {
            const nextDayIdx = cleanText.indexOf(dayMatches[idx + 1]);
            if (nextDayIdx > startIdx) endIdx = nextDayIdx;
          }
          
          // Look for section end markers to prevent mixing travel tips etc into activities
          const endMarkers = [
            '**Budget Breakdown:**', 
            '## Budget Estimate', 
            '## Travel Tips', 
            '## Suggested Packing List',
            '---', 
            'Travel Tips',
            'Budget Estimate',
            'Packing List'
          ];
          
          for (const marker of endMarkers) {
            const markerIdx = cleanText.indexOf(marker);
            if (markerIdx > startIdx && markerIdx < endIdx) {
              endIdx = markerIdx;
            }
          }
          
          const dayContent = cleanText.substring(startIdx + dayHeader.length, endIdx);
          
          // Extract activities (lines that start with time)
          const activities = [];
          const lines = dayContent.split('\n');
          
          lines.forEach(line => {
            line = line.trim();
            
            // Skip section headers and travel information that shouldn't be activities
            const skipPatterns = [
              // Section headers
              'Travel Tips', 'Budget Estimate', 'Packing List', 'Suggested Packing List',
              'Budget Breakdown', 'Total Estimated Budget', 'Ready for your', 'Have an amazing trip',
              
              // Travel advice patterns
              'Best time to visit', 'Getting around', 'Currency', 'Language', 'Safety',
              'Check seasonal weather', 'Use local transport', 'Bring local currency',
              'Keep valuables secure', 'Learn basic local phrases', 'ride-sharing apps',
              'rent vehicles', 'well-lit areas',
              
              // Budget items
              'Accommodation:', 'Food & Dining:', 'Activities:', 'Transport:',
              '/day (', 'total)', '/day ($', '$', 'per day',
              
              // Packing list items (exact matches)
              'Comfortable walking shoes', 'Weather-appropriate clothing', 'Camera/phone for photos',
              'Travel adapter', 'Basic first aid kit', 'Sunscreen and sunglasses', 'Reusable water bottle',
              'Beach towel', 'Waterproof bag', 'Swimwear', 'Sports shoes', 'Quick-dry clothes',
              'Action camera', 'Sandals', 'Hat', 'Insect repellent',
              
              // Partial matches for corrupted text
              'omfortable walking', 'eather-appropriate', 'amera/phone', 'ravel adapter',
              'asic first aid', 'unscreen and sun', 'eusable water', 'each towel',
              'aterproof bag'
            ];
            
            if (skipPatterns.some(pattern => line.includes(pattern))) {
              return; // Skip this line
            }
            
            // Skip lines that are clearly budget/tips/packing items (single words or short phrases)
            if (line.length < 10 && !line.includes('AM') && !line.includes('PM') && !line.includes(':**')) {
              return;
            }
            
            // ULTRA AGGRESSIVE FILTERING: Only allow clear activities with time markers
            if (line.match(/^\w+$/)) return; // Single words
            if (line.match(/^\*+\s*$/)) return; // Just asterisks
            if (line.includes('$')) return; // Any budget-related content
            if (line.includes('/day')) return; // Budget patterns
            if (line.includes('total)')) return; // Budget totals
            if (line.length < 20) return; // Too short to be a meaningful activity
            
            // STRICT: Only include if it has time markers AND looks like an activity
            const hasTimeMarker = line.includes('AM') || line.includes('PM') || line.includes(':**');
            const isActivity = line.includes('Visit') || line.includes('Explore') || line.includes('Check out') ||
                             line.includes('Depart') || line.includes('Arrive') || line.includes('shopping');
            
            if (hasTimeMarker && isActivity && !line.startsWith('**') && !line.startsWith('##') && !line.startsWith('•') && !line.startsWith('*')) {
              const cleanLine = line.replace(/→/g, '→').replace(/\s+/g, ' ').trim();
              if (cleanLine && cleanLine.length > 20) {
                activities.push(cleanLine);
              }
            }
          });
          
          days.push({
            day: dayNum,
            title: dayTitle,
            activities: activities
          });
        });
      }
      
      // If no days parsed, try alternative parsing for corrupted text
      if (days.length === 0) {
        // Look for "Day X" pattern but stop at section markers
        const alternativeMatches = cleanText.match(/Day \d+[\s\S]*?(?=Day \d+|\d+ Activities|## Travel Tips|## Budget Estimate|## Suggested Packing List|Travel Tips|Budget Estimate|Packing List|$)/g);
        
        if (alternativeMatches) {
          alternativeMatches.forEach((daySection, idx) => {
            const dayNum = idx + 1;
            
            // Extract activities from this section
            const activities = [];
            const lines = daySection.split('\n');
            
            lines.forEach(line => {
              line = line.trim();
              
              // Skip section headers and travel information that shouldn't be activities
              const skipPatterns = [
                // Section headers
                'Travel Tips', 'Budget Estimate', 'Packing List', 'Suggested Packing List',
                'Budget Breakdown', 'Total Estimated Budget', 'Ready for your', 'Have an amazing trip',
                
                // Travel advice patterns
                'Best time to visit', 'Getting around', 'Currency', 'Language', 'Safety',
                'Check seasonal weather', 'Use local transport', 'Bring local currency',
                'Keep valuables secure', 'Learn basic local phrases', 'ride-sharing apps',
                'rent vehicles', 'well-lit areas',
                
                // Budget items
                'Accommodation:', 'Food & Dining:', 'Activities:', 'Transport:',
                '/day (', 'total)', '/day ($', '$', 'per day',
                
                // Packing list items (exact matches)
                'Comfortable walking shoes', 'Weather-appropriate clothing', 'Camera/phone for photos',
                'Travel adapter', 'Basic first aid kit', 'Sunscreen and sunglasses', 'Reusable water bottle',
                'Beach towel', 'Waterproof bag', 'Swimwear', 'Sports shoes', 'Quick-dry clothes',
                'Action camera', 'Sandals', 'Hat', 'Insect repellent',
                
                // Partial matches for corrupted text
                'omfortable walking', 'eather-appropriate', 'amera/phone', 'ravel adapter',
                'asic first aid', 'unscreen and sun', 'eusable water', 'each towel',
                'aterproof bag'
              ];
              
              if (skipPatterns.some(pattern => line.includes(pattern))) {
                return; // Skip this line
              }
              
              // ULTRA STRICT: Only include time-based activities
              const hasTimeMarker = line.includes(':**') || line.includes('AM') || line.includes('PM');
              const hasActivityMarker = line.startsWith('🛬') || line.startsWith('🍽️') || line.startsWith('🗺️') ||
                                      line.startsWith('☀️') || line.startsWith('🎯') || line.startsWith('🛍️');
              const isActivity = line.includes('Visit') || line.includes('Explore') || line.includes('Check out') ||
                               line.includes('Depart') || line.includes('Arrive') || line.includes('shopping');
              
              if ((hasTimeMarker || hasActivityMarker) && isActivity) {
                const cleanActivity = line
                  .replace(/^\*+|\*+$/g, '') // Remove asterisks
                  .replace(/^Day \d+\s*/, '') // Remove day prefix
                  .replace(/^\d+\s*Activities?\s*/, '') // Remove activity count
                  .trim();
                
                if (cleanActivity && cleanActivity.length > 20) { // Must be substantial
                  activities.push(cleanActivity);
                }
              }
            });
            
            if (activities.length > 0) {
              days.push({
                day: dayNum,
                title: `Day ${dayNum}`,
                activities: activities
              });
            }
          });
        }
      }
      
      return days.length > 0 ? days : null;
    }
    
    return null;
  };

  if (loading) {
    return (
      <div className="my-trips-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your trips...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-trips-container">
        <div className="error-message">
          <h2>😕 Oops!</h2>
          <p>{error}</p>
          <button onClick={fetchTrips} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="my-trips-container">
      <div className="my-trips-header">
        <button 
          onClick={() => onBackToHome && onBackToHome()}
          className="back-button"
        >
          ← Back to Home
        </button>
        <h1>🗺️ My Trips</h1>
        <p className="subtitle">Your saved travel adventures</p>
      </div>

      {trips.length === 0 ? (
        <div className="no-trips">
          <div className="no-trips-icon">✈️</div>
          <h2>No trips yet!</h2>
          <p>Start planning your next adventure and save your trips here.</p>
          <button 
            onClick={() => window.location.href = '/'}
            className="plan-trip-button"
          >
            Plan a Trip
          </button>
        </div>
      ) : (
        <div className="trips-grid">
          {trips.map((trip) => (
            <div key={trip.id} className="trip-card">
              <div className="trip-card-header">
                <h3>
                  {trip.departure_city && trip.destination ? (
                    <>
                      {trip.departure_city} <span style={{color: '#667eea', fontSize: '1.2rem'}}>→</span> {trip.destination}
                    </>
                  ) : (
                    trip.destination
                  )}
                </h3>
                <button 
                  onClick={() => deleteTrip(trip.id)}
                  className="delete-button"
                  title="Delete trip"
                >
                  🗑️
                </button>
              </div>

              <div className="trip-details">
                <div className="detail-item">
                  <span className="detail-icon">📅</span>
                  <div className="detail-content">
                    <span className="detail-label">Dates</span>
                    <span className="detail-value">
                      {trip.dates?.start && trip.dates?.end ? (
                        `${new Date(trip.dates.start).toLocaleDateString()} - ${new Date(trip.dates.end).toLocaleDateString()}`
                      ) : trip.start_date && trip.end_date ? (
                        `${new Date(trip.start_date).toLocaleDateString()} - ${new Date(trip.end_date).toLocaleDateString()}`
                      ) : (
                        'Not specified'
                      )}
                    </span>
                  </div>
                </div>

                <div className="detail-item">
                  <span className="detail-icon">⏱️</span>
                  <div className="detail-content">
                    <span className="detail-label">Duration</span>
                    <span className="detail-value">
                      {trip.duration_days} {trip.duration_days === 1 ? 'day' : 'days'}
                    </span>
                  </div>
                </div>

                {trip.budget && (
                  <div className="detail-item">
                    <span className="detail-icon">💰</span>
                    <div className="detail-content">
                      <span className="detail-label">Budget</span>
                      <span className="detail-value">
                        {typeof trip.budget === 'object' 
                          ? `$${trip.budget.per_day}/day (Total: $${trip.budget.total})`
                          : trip.budget
                        }
                      </span>
                    </div>
                  </div>
                )}

                {trip.interests && trip.interests.length > 0 && (
                  <div className="detail-item">
                    <span className="detail-icon">🎯</span>
                    <div className="detail-content">
                      <span className="detail-label">Interests</span>
                      <div className="interests-tags">
                        {trip.interests.map((interest, idx) => (
                          <span key={idx} className="interest-tag">
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="trip-card-footer">
                <button 
                  onClick={() => openItineraryModal(trip)}
                  className="view-itinerary-button"
                >
                  📋 View Itinerary
                </button>
                <span className="created-date">
                  Created {new Date(trip.created_at).toLocaleDateString()}
                </span>
              </div>


            </div>
          ))}
        </div>
      )}

      {/* Itinerary Preview Modal */}
      <Dialog
        open={modalOpen}
        onClose={closeItineraryModal}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: '16px',
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          bgcolor: '#f8fafc',
          borderBottom: '1px solid #e2e8f0'
        }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1e293b' }}>
              📅 Trip Itinerary
            </Typography>
            {selectedTrip && (
              <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
                {selectedTrip.departure_city && selectedTrip.destination ? (
                  <>{selectedTrip.departure_city} → {selectedTrip.destination}</>
                ) : (
                  selectedTrip.destination
                )}
              </Typography>
            )}
          </Box>
          <IconButton onClick={closeItineraryModal}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          {selectedTrip && selectedTrip.itinerary && (
            <Box>
              {(() => {
                const parsedItinerary = parseItinerary(selectedTrip.itinerary);
                
                if (parsedItinerary && parsedItinerary.length > 0) {
                  return (
                    <Box sx={{ mt: 2 }}>
                      {parsedItinerary.map((day, idx) => (
                        <ItineraryCard 
                          key={idx}
                          dayData={day}
                          dayNumber={day.day || idx + 1}
                        />
                      ))}
                    </Box>
                  );
                } else {
                  return (
                    <Box sx={{ 
                      textAlign: 'center', 
                      py: 4,
                      color: '#64748b'
                    }}>
                        <Typography variant="h6">📝 No detailed itinerary available</Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        This trip doesn't have a structured daily itinerary.
                      </Typography>
                    </Box>
                  );
                }
              })()
              }
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={closeItineraryModal}
            variant="contained"
            sx={{
              bgcolor: '#667eea',
              '&:hover': { bgcolor: '#5a6fd8' },
              borderRadius: '8px',
              px: 3
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default MyTrips;
