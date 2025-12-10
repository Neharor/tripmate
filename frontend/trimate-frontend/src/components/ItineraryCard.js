import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import MuseumIcon from '@mui/icons-material/Museum';
import NatureIcon from '@mui/icons-material/Nature';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import FlightIcon from '@mui/icons-material/Flight';

export default function ItineraryCard({ dayData, dayNumber }) {

  
  // Ensure dayData has required structure
  if (!dayData || !dayData.activities) {
    return (
      <Card sx={{ mb: 3, p: 2, borderRadius: '16px' }}>
        <Typography variant="body1" color="text.secondary">
          No activities found for Day {dayNumber}
        </Typography>
      </Card>
    );
  }
  // Parse activity text to extract time, activity, and location
  const parseActivityText = (activityText) => {
    // Clean up HTML tags and entities
    let cleaned = activityText
      .replace(/<[^>]+>/g, '') // Remove all HTML tags
      .replace(/&nbsp;/g, ' ') // Replace HTML entities
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/^[•\-\*]\s*/, '') // Remove bullet points
      .trim();
    
    // Extract time patterns - handle various formats
    let timeRange = '';
    let activityContent = cleaned;
    
    // Pattern 1: **9:00 AM - 12:00 PM** or **9:00 AM**
    let timeMatch = cleaned.match(/\*\*(\d+:\d+\s*(?:AM|PM))(?:\s*-\s*(\d+:\d+\s*(?:AM|PM)))?\*\*/i);
    if (timeMatch) {
      timeRange = timeMatch[2] ? `${timeMatch[1]} - ${timeMatch[2]}` : timeMatch[1];
      activityContent = cleaned.replace(timeMatch[0], '').replace(/^[:\s-]*/, '').trim();
    } else {
      // Pattern 2: 9:00 AM - 12:00 PM (without asterisks)
      timeMatch = cleaned.match(/^(\d+:\d+\s*(?:AM|PM))(?:\s*-\s*(\d+:\d+\s*(?:AM|PM)))?[:\s-]*(.*)/i);
      if (timeMatch) {
        timeRange = timeMatch[2] ? `${timeMatch[1]} - ${timeMatch[2]}` : timeMatch[1];
        activityContent = timeMatch[3] ? timeMatch[3].trim() : '';
      }
    }
    
    // Clean remaining content
    activityContent = activityContent
      .replace(/^[:\s-]+/, '') // Remove leading colons, spaces, dashes
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim();
    
    // If content is empty, use a default
    if (!activityContent) {
      activityContent = 'Activity';
    }
    
    // Extract location/rating info (text after dash, rating pattern)
    const locationMatch = activityContent.match(/^(.+?)\s*(?:-\s*(.+?))?(?:\s*(\d+\.?\d*)\s*⭐\s*\((\d+)\s*reviews\))?(.*)/);
    
    let activityName = activityContent;
    let location = '';
    let description = '';
    let rating = null;
    let reviews = null;
    
    if (locationMatch) {
      activityName = locationMatch[1].trim();
      if (locationMatch[2]) location = locationMatch[2].trim();
      if (locationMatch[3]) rating = parseFloat(locationMatch[3]);
      if (locationMatch[4]) reviews = parseInt(locationMatch[4]);
      if (locationMatch[5]) description = locationMatch[5].trim();
    }
    
    // Final cleanup
    activityName = activityName.replace(/^\*\*|\*\*$/g, '').trim();
    location = location.replace(/^\*\*|\*\*$/g, '').trim();
    
    // Determine activity type for icon
    const activityType = getActivityType(activityName + ' ' + location + ' ' + description);
    
    return {
      time: timeRange,
      name: activityName || 'Activity',
      location: location,
      description: description,
      rating: rating,
      reviews: reviews,
      type: activityType
    };
  };

  // Get activity type for appropriate icon
  const getActivityType = (text) => {
    const lowerText = text.toLowerCase();
    if (lowerText.includes('food') || lowerText.includes('restaurant') || lowerText.includes('dinner') || lowerText.includes('lunch') || lowerText.includes('cuisine') || lowerText.includes('eat') || lowerText.includes('breakfast') || lowerText.includes('café') || lowerText.includes('coffee')) {
      return 'food';
    } else if (lowerText.includes('temple') || lowerText.includes('museum') || lowerText.includes('cultural') || lowerText.includes('historic') || lowerText.includes('palace') || lowerText.includes('monument') || lowerText.includes('gallery') || lowerText.includes('art')) {
      return 'culture';
    } else if (lowerText.includes('nature') || lowerText.includes('park') || lowerText.includes('beach') || lowerText.includes('outdoor') || lowerText.includes('garden') || lowerText.includes('forest') || lowerText.includes('mountain') || lowerText.includes('hike') || lowerText.includes('trek')) {
      return 'nature';
    } else if (lowerText.includes('shopping') || lowerText.includes('market') || lowerText.includes('mall') || lowerText.includes('bazaar') || lowerText.includes('souvenir') || lowerText.includes('store')) {
      return 'shopping';
    } else if (lowerText.includes('arrive') || lowerText.includes('departure') || lowerText.includes('airport') || lowerText.includes('flight') || lowerText.includes('transfer') || lowerText.includes('taxi') || lowerText.includes('bus')) {
      return 'transport';
    } else {
      return 'general';
    }
  };

  // Get icon for activity type
  const getActivityIcon = (type) => {
    switch (type) {
      case 'food': return <RestaurantIcon sx={{ color: '#f59e0b' }} />;
      case 'culture': return <MuseumIcon sx={{ color: '#8b5cf6' }} />;
      case 'nature': return <NatureIcon sx={{ color: '#10b981' }} />;
      case 'shopping': return <ShoppingBagIcon sx={{ color: '#ec4899' }} />;
      case 'transport': return <FlightIcon sx={{ color: '#3b82f6' }} />;
      default: return <LocationOnIcon sx={{ color: '#6b7280' }} />;
    }
  };

  // Parse activities from dayData
  const activities = dayData.activities
    .filter(activity => activity && (typeof activity === 'string' ? activity.trim().length > 0 : true))
    .map((activity, idx) => {
      if (typeof activity === 'string') {
        const parsed = parseActivityText(activity);
        return { id: idx, ...parsed };
      }
      // Handle object activities
      return { 
        id: idx, 
        time: '',
        name: activity.name || activity.title || 'Activity',
        location: activity.location || '',
        description: activity.description || '',
        rating: activity.rating || null,
        reviews: activity.reviews || null,
        type: getActivityType((activity.name || activity.title || '') + ' ' + (activity.location || '')),
        ...activity 
      };
    });

  return (
    <Card sx={{ 
      mb: 3, 
      borderRadius: '16px', 
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      border: '1px solid #e2e8f0',
      overflow: 'visible',
      position: 'relative'
    }}>
      {/* Day Header */}
      <Box sx={{ 
        bgcolor: '#1e293b', 
        color: 'white', 
        p: 2.5,
        borderRadius: '16px 16px 0 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
            Day {dayNumber}
          </Typography>
          {dayData.date && (
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              {dayData.date
                .replace(/<[^>]+>/g, '') // Remove any HTML tags
                .replace(/&nbsp;/g, ' ')  // Replace HTML entities
                .trim()}
            </Typography>
          )}
        </Box>
        <Chip 
          label={`${activities.length} Activities`}
          sx={{ 
            bgcolor: 'rgba(255, 255, 255, 0.2)', 
            color: 'white',
            fontWeight: 600 
          }}
        />
      </Box>

      <CardContent sx={{ p: 0 }}>
        {activities.map((activity, idx) => (
          <Box 
            key={activity.id || idx}
            sx={{ 
              p: 3,
              borderBottom: idx < activities.length - 1 ? '1px solid #f1f5f9' : 'none',
              '&:hover': {
                bgcolor: '#f8fafc'
              }
            }}
          >
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
              {/* Activity Icon */}
              <Box sx={{ 
                flexShrink: 0,
                mt: 0.5
              }}>
                {getActivityIcon(activity.type)}
              </Box>

              {/* Activity Content */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                {/* Time */}
                {activity.time && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                    <AccessTimeIcon sx={{ fontSize: 16, color: '#64748b' }} />
                    <Typography variant="caption" sx={{ 
                      color: '#64748b', 
                      fontWeight: 600,
                      fontSize: '0.8rem'
                    }}>
                      {activity.time}
                    </Typography>
                  </Box>
                )}

                {/* Activity Name */}
                <Typography variant="h6" sx={{ 
                  fontWeight: 600, 
                  color: '#1e293b',
                  mb: 0.5,
                  lineHeight: 1.3
                }}>
                  {activity.name}
                </Typography>

                {/* Location */}
                {activity.location && (
                  <Typography variant="body2" sx={{ 
                    color: '#475569', 
                    mb: 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5
                  }}>
                    <LocationOnIcon sx={{ fontSize: 16 }} />
                    {activity.location}
                  </Typography>
                )}

                {/* Rating */}
                {activity.rating && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: '#f59e0b' }}>
                        {activity.rating}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#f59e0b' }}>
                        ⭐
                      </Typography>
                    </Box>
                    {activity.reviews && (
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        ({activity.reviews.toLocaleString()} reviews)
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Description */}
                {activity.description && (
                  <Typography variant="body2" sx={{ 
                    color: '#64748b',
                    fontStyle: 'italic',
                    lineHeight: 1.4
                  }}>
                    {activity.description}
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
}