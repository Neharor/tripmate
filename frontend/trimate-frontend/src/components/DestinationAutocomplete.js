import React, { useState, useEffect } from 'react';
import {
  Autocomplete,
  TextField,
  CircularProgress,
  Box,
  Typography
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const DestinationAutocomplete = ({ onSelect, placeholder = "Search destinations..." }) => {
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');

  // Fetch popular destinations on initial load
  useEffect(() => {
    const fetchPopular = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/locations/popular');
        const data = await response.json();
        if (data.locations) {
          setOptions(data.locations);
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
      return;
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://localhost:5002/api/locations/search?q=${encodeURIComponent(inputValue)}&limit=10`
        );
        const data = await response.json();
        if (data.locations) {
          setOptions(data.locations);
        } else {
          setOptions([]);
        }
      } catch (error) {
        console.error('Error searching destinations:', error);
        setOptions([]);
      } finally {
        setLoading(false);
      }
    }, 300); // 300ms debounce delay

    return () => clearTimeout(timeoutId);
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
        inputValue.length < 2
          ? "Type at least 2 characters to search"
          : "No destinations found"
      }
    />
  );
};

export default DestinationAutocomplete;
