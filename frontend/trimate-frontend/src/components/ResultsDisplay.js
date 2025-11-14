import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Paper
} from '@mui/material';

export default function ResultsDisplay({ results, loading }) {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!results) return null;

  const destinations = Array.isArray(results.destinations?.plan)
    ? results.destinations.plan
    : results.destinations?.plan
      ? [String(results.destinations.plan)]
      : [];

  const stays = Array.isArray(results.stays?.stays)
    ? results.stays.stays
    : results.stays?.stays
      ? [String(results.stays.stays)]
      : [];

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        Travel Recommendations
      </Typography>

      {/* Destinations as cards */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Destinations
        </Typography>

        {destinations.length === 0 ? (
          <Paper sx={{ p: 2 }}><Typography>No destinations found.</Typography></Paper>
        ) : (
          <Grid container spacing={2}>
            {destinations.map((item, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {typeof item === 'string' ? item : String(item)}
                    </Typography>
                    {/* Example: we could parse details here if item was an object */}
                  </CardContent>
                  <CardActions>
                    <Button size="small">View</Button>
                    <Button size="small" variant="contained">Add to Plan</Button>
                    <Chip label={`#${idx + 1}`} size="small" sx={{ ml: 'auto' }} />
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* Stays as cards */}
      <Box>
        <Typography variant="h6" color="primary" gutterBottom>
          Recommended Stays
        </Typography>

        {stays.length === 0 ? (
          <Paper sx={{ p: 2 }}><Typography>No stays found.</Typography></Paper>
        ) : (
          <Grid container spacing={2}>
            {stays.map((stay, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {stay}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Sample description for {stay}. Add pricing, rating or distance here.
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Details</Button>
                    <Button size="small" variant="contained">Book</Button>
                    <Chip label={`#${idx + 1}`} size="small" sx={{ ml: 'auto' }} />
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Box>
  );
}