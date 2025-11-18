import React, { useEffect, useRef, useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import HotelIcon from '@mui/icons-material/Hotel';
import RestaurantIcon from '@mui/icons-material/Restaurant';

// Mapbox access token (you'll need to get one from https://mapbox.com)
const MAPBOX_TOKEN = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'; // Demo token - replace with your own

export default function MapView({ destination, hotels = [], activities = [], onClose }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!destination || map.current) return;

    // Geocode the destination to get coordinates
    geocodeLocation(destination).then(coords => {
      if (!coords) return;

      // Initialize map
      map.current = new window.mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: [coords.lng, coords.lat],
        zoom: 11,
        accessToken: MAPBOX_TOKEN
      });

      map.current.on('load', () => {
        setMapLoaded(true);

        // Add destination marker
        new window.mapboxgl.Marker({ color: '#ef4444', scale: 1.2 })
          .setLngLat([coords.lng, coords.lat])
          .setPopup(new window.mapboxgl.Popup().setHTML(`
            <div style="padding: 8px;">
              <strong style="font-size: 16px;">${destination}</strong>
              <p style="margin: 4px 0 0 0; color: #666;">Your destination</p>
            </div>
          `))
          .addTo(map.current);

        // Add hotel markers
        hotels.forEach((hotel, idx) => {
          if (hotel.coordinates) {
            const el = document.createElement('div');
            el.className = 'hotel-marker';
            el.innerHTML = '🏨';
            el.style.fontSize = '24px';
            el.style.cursor = 'pointer';

            new window.mapboxgl.Marker(el)
              .setLngLat([hotel.coordinates.lng, hotel.coordinates.lat])
              .setPopup(new window.mapboxgl.Popup().setHTML(`
                <div style="padding: 8px;">
                  <strong>${hotel.name}</strong>
                  <p style="margin: 4px 0 0 0;">${hotel.price}</p>
                </div>
              `))
              .addTo(map.current);
          }
        });

        // Add activity markers
        activities.forEach((activity, idx) => {
          if (activity.coordinates) {
            const el = document.createElement('div');
            el.className = 'activity-marker';
            el.innerHTML = '📍';
            el.style.fontSize = '24px';
            el.style.cursor = 'pointer';

            new window.mapboxgl.Marker(el)
              .setLngLat([activity.coordinates.lng, activity.coordinates.lat])
              .setPopup(new window.mapboxgl.Popup().setHTML(`
                <div style="padding: 8px;">
                  <strong>${activity.name}</strong>
                  <p style="margin: 4px 0 0 0;">${activity.description}</p>
                </div>
              `))
              .addTo(map.current);
          }
        });
      });

      // Add navigation controls
      map.current.addControl(new window.mapboxgl.NavigationControl());
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [destination, hotels, activities]);

  return (
    <Paper sx={{
      position: 'fixed',
      top: '80px',
      right: '20px',
      width: '400px',
      height: '500px',
      borderRadius: '12px',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
      zIndex: 1000
    }}>
      {/* Header */}
      <Box sx={{
        bgcolor: '#1e293b',
        color: '#ffffff',
        p: 2,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocationOnIcon />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Map View
          </Typography>
        </Box>
        <IconButton size="small" onClick={onClose} sx={{ color: '#ffffff' }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Map Container */}
      <Box
        ref={mapContainer}
        sx={{
          width: '100%',
          height: 'calc(100% - 64px)'
        }}
      />

      {/* Legend */}
      <Box sx={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        bgcolor: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '8px',
        p: 1.5,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, mb: 0.5 }}>
          Legend:
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span style={{ fontSize: '16px' }}>📍</span>
            <Typography variant="caption">Destination</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span style={{ fontSize: '16px' }}>🏨</span>
            <Typography variant="caption">Hotels</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span style={{ fontSize: '16px' }}>🍽️</span>
            <Typography variant="caption">Activities</Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}

// Helper function to geocode location names to coordinates
async function geocodeLocation(locationName) {
  try {
    // Using Mapbox Geocoding API
    const response = await fetch(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(locationName)}.json?access_token=${MAPBOX_TOKEN}`
    );
    const data = await response.json();
    
    if (data.features && data.features.length > 0) {
      const [lng, lat] = data.features[0].center;
      return { lng, lat };
    }
    return null;
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
}
