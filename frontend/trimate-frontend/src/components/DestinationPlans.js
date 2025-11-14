import React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';

export default function DestinationPlans({ plan }) {
  const items = Array.isArray(plan) ? plan : (plan ? [String(plan)] : []);

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Typography variant="h6" color="primary" gutterBottom>
        Destinations
      </Typography>

      {items.length > 0 ? (
        <List dense>
          {items.map((item, idx) => (
            <ListItem key={idx} divider>
              <ListItemText primary={item} />
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2">No destinations found.</Typography>
      )}
    </Paper>
  );
}
