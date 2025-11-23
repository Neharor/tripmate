import React from 'react';
import { Box, Typography, Chip, Alert, Accordion, AccordionSummary, AccordionDetails, LinearProgress } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';

/**
 * FlightConfidenceIndicator
 * Shows users HOW we determined these are "best" flights
 * Transparency builds trust!
 */
export default function FlightConfidenceIndicator({ searchMetadata, insights, confidence }) {
  
  const getConfidenceColor = (score) => {
    if (score >= 80) return '#16a34a'; // Green - High confidence
    if (score >= 60) return '#eab308'; // Yellow - Medium
    return '#ef4444'; // Red - Low confidence
  };

  const getConfidenceLabel = (score) => {
    if (score >= 80) return 'High Confidence';
    if (score >= 60) return 'Medium Confidence';
    return 'Low Confidence - Estimates Only';
  };

  return (
    <Box sx={{ mb: 3 }}>
      {/* Main Confidence Score */}
      <Box sx={{ 
        p: 2, 
        bgcolor: '#f8fafc', 
        borderRadius: '12px', 
        border: '1px solid #e2e8f0',
        mb: 2 
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" sx={{ fontSize: '16px', fontWeight: 600 }}>
            Search Confidence
          </Typography>
          <Chip 
            label={getConfidenceLabel(confidence)}
            sx={{ 
              bgcolor: getConfidenceColor(confidence),
              color: 'white',
              fontWeight: 600
            }}
          />
        </Box>
        
        <LinearProgress 
          variant="determinate" 
          value={confidence} 
          sx={{ 
            height: 8, 
            borderRadius: '4px',
            bgcolor: '#e2e8f0',
            '& .MuiLinearProgress-bar': {
              bgcolor: getConfidenceColor(confidence),
              borderRadius: '4px'
            }
          }}
        />
        
        <Typography variant="caption" sx={{ color: '#64748b', mt: 1, display: 'block' }}>
          {confidence}% confidence that these are the best available options
        </Typography>
      </Box>

      {/* Warning if low confidence */}
      {confidence < 70 && (
        <Alert severity="warning" sx={{ mb: 2, borderRadius: '8px' }}>
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
            Limited Data Available
          </Typography>
          <Typography variant="caption">
            Real-time flight API not connected. Prices shown are estimates based on AI predictions. 
            Actual prices may vary. For guaranteed pricing, click "Search on Google Flights".
          </Typography>
        </Alert>
      )}

      {/* Search Details (Expandable) */}
      <Accordion sx={{ borderRadius: '12px', boxShadow: 'none', border: '1px solid #e2e8f0' }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InfoIcon sx={{ color: '#3b82f6', fontSize: 20 }} />
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              What we checked to find these flights
            </Typography>
          </Box>
        </AccordionSummary>
        
        <AccordionDetails>
          {/* Insights List */}
          <Box sx={{ mb: 2 }}>
            {insights && insights.map((insight, idx) => (
              <Box key={idx} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                {insight.startsWith('✅') ? (
                  <CheckCircleIcon sx={{ color: '#16a34a', fontSize: 18, mt: 0.2 }} />
                ) : (
                  <WarningIcon sx={{ color: '#eab308', fontSize: 18, mt: 0.2 }} />
                )}
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  {insight.replace(/^[✅⚠️🎉💰🔍📅⭐🏆]\s*/, '')}
                </Typography>
              </Box>
            ))}
          </Box>

          {/* Search Metadata */}
          {searchMetadata && (
            <Box sx={{ 
              bgcolor: '#f1f5f9', 
              p: 2, 
              borderRadius: '8px',
              border: '1px dashed #cbd5e1'
            }}>
              <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1, color: '#475569' }}>
                Search Coverage
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip 
                  label={`${searchMetadata.total_flights_checked || 0} flights analyzed`}
                  size="small"
                  sx={{ bgcolor: 'white' }}
                />
                <Chip 
                  label={`${(searchMetadata.airlines_searched || []).length} airlines`}
                  size="small"
                  sx={{ bgcolor: 'white' }}
                />
                {searchMetadata.date_range && (
                  <Chip 
                    label={`Dates: ${searchMetadata.date_range}`}
                    size="small"
                    sx={{ bgcolor: 'white' }}
                  />
                )}
              </Box>

              {searchMetadata.airlines_searched && searchMetadata.airlines_searched.length > 0 && (
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mt: 1 }}>
                  Airlines checked: {searchMetadata.airlines_searched.slice(0, 5).join(', ')}
                  {searchMetadata.airlines_searched.length > 5 && ` +${searchMetadata.airlines_searched.length - 5} more`}
                </Typography>
              )}
            </Box>
          )}

          {/* Data Source Transparency */}
          <Box sx={{ mt: 2, p: 1.5, bgcolor: '#fef3c7', borderRadius: '6px', border: '1px solid #fde047' }}>
            <Typography variant="caption" sx={{ color: '#92400e', display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <WarningIcon sx={{ fontSize: 14 }} />
              <strong>Data Source:</strong> {confidence >= 70 ? 'Live API' : 'AI Estimates'}
            </Typography>
            <Typography variant="caption" sx={{ color: '#78350f', display: 'block', mt: 0.5 }}>
              {confidence >= 70 
                ? 'Real-time pricing from airline APIs' 
                : 'Estimated prices based on historical data. Verify on airline websites before booking.'}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Alternative Options Hint */}
      {confidence >= 60 && (
        <Box sx={{ mt: 2, p: 2, bgcolor: '#eff6ff', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
          <Typography variant="body2" sx={{ color: '#1e40af', fontWeight: 600, mb: 0.5 }}>
            💡 Pro Tip
          </Typography>
          <Typography variant="caption" sx={{ color: '#1e3a8a' }}>
            We checked {searchMetadata?.total_flights_checked || 'multiple'} flights across different dates. 
            The options shown below offer the best value based on price, duration, and airline quality.
          </Typography>
        </Box>
      )}
    </Box>
  );
}
