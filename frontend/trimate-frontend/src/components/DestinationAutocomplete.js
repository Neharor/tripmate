import React, { useState, useEffect } from 'react';
import {
  Autocomplete,
  TextField,
  CircularProgress,
  Box,
  Typography
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002';

const DestinationAutocomplete = ({ onSelect, placeholder = "Search destinations..." }) => {
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');

  // Fetch popular destinations on initial load
  useEffect(() => {
    const fetchPopular = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/locations/popular`);
        const data = await response.json();
        if (data.locations) {
          setOptions(data.locations);
          console.log('✅ Popular destinations loaded:', data.locations.length);
        }
      } catch (error) {
        console.error('Error fetching popular destinations:', error);
      }
    };
    fetchPopular();
  }, []);

  // Debounced search effect
  useEffect(() => {
    // Don't search for queries shorter than 2 characters
    if (inputValue.length < 2) {
      // If no input, show popular destinations
      if (inputValue.length === 0 && options.length === 0) {
        const fetchPopular = async () => {
          try {
            const response = await fetch(`${BACKEND_URL}/api/locations/popular`);
            const data = await response.json();
            if (data.locations) {
              setOptions(data.locations);
            }
          } catch (error) {
            console.error('Error fetching popular destinations:', error);
          }
        };
        fetchPopular();
      }
      return;
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${BACKEND_URL}/api/locations/search?q=${encodeURIComponent(inputValue)}&limit=10`
        );
        const data = await response.json();
        if (data.locations && data.locations.length > 0) {
          setOptions(data.locations);
        } else {
          // Fallback to popular destinations if search returns nothing
          try {
            const popularResponse = await fetch(`${BACKEND_URL}/api/locations/popular`);
            const popularData = await popularResponse.json();
            if (popularData.locations) {
              setOptions(popularData.locations);
            } else {
              setOptions([]);
            }
          } catch (error) {
            console.error('Error fetching fallback destinations:', error);
            setOptions([]);
          }
        }
      } catch (error) {
        console.error('Error searching destinations:', error);
        // Fallback to popular destinations on error
        try {
          const response = await fetch(`${BACKEND_URL}/api/locations/popular`);
          const data = await response.json();
          if (data.locations) {
            setOptions(data.locations);
          }
        } catch (e) {
          console.error('Error fetching fallback destinations:', e);
          setOptions([]);
        }
      } finally {
        setLoading(false);
      }
    }, 300); // 300ms debounce delay

    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inputValue]);

  const handleSelect = (event, value) => {
    if (value && onSelect) {
      onSelect(value);
    }
  };

  return (
    <Autocomplete
      open={open}
      onOpen={() => setOpen(true)}
      onClose={() => setOpen(false)}
      options={options}
      loading={loading}
      getOptionLabel={(option) => option.display || ''}
      onChange={handleSelect}
      onInputChange={(event, newInputValue) => {
        setInputValue(newInputValue);
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={placeholder}
          variant="outlined"
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <Box
          component="li"
          {...props}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            py: 1.5,
            px: 2,
            '&:hover': {
              backgroundColor: 'rgba(63, 81, 181, 0.08)',
            },
          }}
        >
          <LocationOnIcon sx={{ color: '#3f51b5', fontSize: 20 }} />
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              {option.name}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              {option.country}
              {option.iata_code && ` • ${option.iata_code}`}
            </Typography>
          </Box>
        </Box>
      )}
      sx={{
        width: '100%',
        '& .MuiOutlinedInput-root': {
          '& fieldset': {
            borderColor: '#ddd',
          },
          '&:hover fieldset': {
            borderColor: '#3f51b5',
          },
          '&.Mui-focused fieldset': {
            borderColor: '#3f51b5',
          },
        },
      }}
      noOptionsText={
        inputValue.length === 0
          ? "Popular destinations will appear here"
          : inputValue.length < 2
          ? "Type at least 2 characters to search"
          : "No destinations found"
      }
    />
  );
};

export default DestinationAutocomplete;
