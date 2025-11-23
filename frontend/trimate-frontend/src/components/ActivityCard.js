import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import InfoIcon from '@mui/icons-material/Info';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

export default function ActivityCard({ activity }) {

  // Parse activity from text format
  // Example: "🎫 Tanah Lot Temple Sunset Tour - Skip lines, guided tour, sunset views ($30-45)"
  const parseActivity = (activityText) => {
    // Remove emoji and split
    const cleaned = activityText.replace(/^[🎫🎯🌊🍜🏛️🚶]\s*/, '').trim();
    
    // Extract name (before dash)
    const dashIndex = cleaned.indexOf(' - ');
    if (dashIndex === -1) {
      return {
        name: cleaned,
        description: '',
        price: ''
      };
    }
    
    const name = cleaned.substring(0, dashIndex).trim();
    const rest = cleaned.substring(dashIndex + 3).trim();
    
    // Extract price (in parentheses at end)
    const priceMatch = rest.match(/\((\$[\d-]+)\)$/);
    const price = priceMatch ? priceMatch[1] : '';
    const description = priceMatch ? rest.substring(0, rest.lastIndexOf('(')).trim() : rest;
    
    return { name, description, price };
  };

  const activityData = typeof activity === 'string' ? parseActivity(activity) : activity;
  
  if (!activityData) return null;

  // Generate Viator search URL
  const getViatorUrl = () => {
    const searchQuery = encodeURIComponent(activityData.name);
    return `https://www.viator.com/searchResults/all?text=${searchQuery}`;
  };

  return (
      <Card sx={{
        mb: 2,
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        border: '2px solid #f1f5f9',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 16px rgba(59, 130, 246, 0.15)',
          borderColor: '#3b82f6'
        }
      }}>
        <Box sx={{ display: 'flex' }}>
          {/* Icon */}
          <Box sx={{
            width: 80,
            bgcolor: '#3b82f6',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            p: 2
          }}>
            <ConfirmationNumberIcon sx={{ color: '#ffffff', fontSize: 40 }} />
          </Box>
          
          {/* Activity Details */}
          <Box sx={{ flexGrow: 1 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5, fontSize: '16px', color: '#1e293b' }}>
                {activityData.name}
              </Typography>
              
              {activityData.description && (
                <Typography variant="body2" sx={{ color: '#64748b', mb: 1.5, lineHeight: 1.5 }}>
                  {activityData.description}
                </Typography>
              )}
              
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                {activityData.price && (
                  <Chip
                    icon={<AttachMoneyIcon sx={{ fontSize: 14 }} />}
                    label={activityData.price}
                    size="small"
                    sx={{
                      bgcolor: '#dcfce7',
                      color: '#16a34a',
                      fontSize: '12px',
                      fontWeight: 600
                    }}
                  />
                )}
                
                <Chip
                  icon={<InfoIcon sx={{ fontSize: 14 }} />}
                  label="Pre-booking recommended"
                  size="small"
                  sx={{
                    bgcolor: '#fef3c7',
                    color: '#d97706',
                    fontSize: '11px',
                    fontWeight: 600
                  }}
                />
                
                <Button
                  variant="contained"
                  size="small"
                  endIcon={<OpenInNewIcon />}
                  onClick={() => window.open(getViatorUrl(), '_blank')}
                  sx={{
                    ml: 'auto',
                    bgcolor: '#3b82f6',
                    fontSize: '12px',
                    fontWeight: 600,
                    textTransform: 'none',
                    px: 2,
                    '&:hover': {
                      bgcolor: '#2563eb'
                    }
                  }}
                >
                  Book on Viator
                </Button>
              </Box>
            </CardContent>
          </Box>
        </Box>
      </Card>
  );
}
