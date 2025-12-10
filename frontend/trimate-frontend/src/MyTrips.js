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

  const parseItinerary = (itinerary) => {
    // Handle array with nested structure
    if (Array.isArray(itinerary)) {
      // Check if it's already in the right format
      if (itinerary.length > 0 && itinerary[0].activities && Array.isArray(itinerary[0].activities)) {
        // Check if activities contain a single string with full itinerary
        if (itinerary[0].activities.length === 1 && typeof itinerary[0].activities[0] === 'object' && itinerary[0].activities[0].name) {
          // Extract the string and parse it
          return parseItinerary(itinerary[0].activities[0].name);
        }
      }
      // If it's already properly structured, return as is
      if (itinerary.length > 1 || (itinerary.length === 1 && itinerary[0].day && itinerary[0].activities && itinerary[0].activities.length > 1)) {
        return itinerary;
      }
    }
    
    if (typeof itinerary === 'string') {
      // Parse string itinerary into structured format
      const days = [];
      const dayMatches = itinerary.match(/\*\*Day \d+:.*?\*\*/g);
      
      if (dayMatches) {
        dayMatches.forEach((dayHeader, idx) => {
          const dayNum = idx + 1;
          const dayTitle = dayHeader.replace(/\*\*/g, '').trim();
          
          // Find content between this day and the next day (or budget breakdown)
          const startIdx = itinerary.indexOf(dayHeader);
          const nextDayIdx = dayMatches[idx + 1] ? itinerary.indexOf(dayMatches[idx + 1]) : itinerary.indexOf('**Budget Breakdown:**');
          const dayContent = itinerary.substring(startIdx + dayHeader.length, nextDayIdx > startIdx ? nextDayIdx : itinerary.length);
          
          // Extract activities (lines that start with time)
          const activities = [];
          const lines = dayContent.split('\n');
          
          lines.forEach(line => {
            line = line.trim();
            if (line && !line.startsWith('**') && line.length > 0) {
              // Clean up the line
              const cleanLine = line.replace(/→/g, '→').replace(/\s+/g, ' ').trim();
              if (cleanLine) {
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
