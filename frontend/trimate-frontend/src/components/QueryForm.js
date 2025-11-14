import React, { useState } from 'react';
import { 
  TextField, 
  Button, 
  Paper, 
  Box,
  InputAdornment,
  useTheme,
  useMediaQuery
} from '@mui/material';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import SendIcon from '@mui/icons-material/Send';

function QueryForm({ onSubmit, loading }) {
  const [query, setQuery] = useState('');
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <Paper 
      elevation={0}
      sx={{ 
        p: isSmallScreen ? 2 : 3,
        mb: 3,
        borderRadius: 3,
        background: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
      }}
    >
      <Box 
        component="form" 
        onSubmit={handleSubmit} 
        sx={{ 
          display: 'flex', 
          alignItems: 'center',
          flexDirection: isSmallScreen ? 'column' : 'row',
          gap: 2 
        }}
      >
        <TextField
          variant="outlined"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="please help me plan a trip"
          disabled={loading}
          sx={{
            flexBasis: isSmallScreen ? '100%' : '70%',
            flexGrow: 0,
            '& .MuiOutlinedInput-root': {
              borderRadius: '14px',
              backgroundColor: '#ffffff',
              minHeight: isSmallScreen ? 48 : 56,
              boxShadow: '0 6px 20px rgba(3, 169, 244, 0.06)',
              '&:hover': {
                '& > fieldset': {
                  borderColor: theme.palette.primary.main,
                }
              },
              '& .MuiOutlinedInput-input': {
                padding: isSmallScreen ? '10px 12px' : '12px 16px',
                fontSize: isSmallScreen ? 15 : 16,
              }
            },
            '& .MuiOutlinedInput-notchedOutline': {
              borderRadius: '14px'
            }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <TravelExploreIcon color="primary" />
              </InputAdornment>
            ),
          }}
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={!query.trim() || loading}
          endIcon={<SendIcon sx={{ transform: 'rotate(0deg)' }} />}
          sx={{
            flexBasis: isSmallScreen ? '100%' : '30%',
            flexGrow: 0,
            height: isSmallScreen ? 48 : 56,
            borderRadius: '14px',
            px: 2,
            fontSize: 15,
            textTransform: 'none',
            background: loading 
              ? theme.palette.grey[300]
              : 'linear-gradient(135deg, #1976d2 0%, #00bcd4 100%)',
            boxShadow: loading 
              ? 'none' 
              : '0 8px 24px rgba(3, 169, 244, 0.18)',
            '&:hover': {
              background: loading
                ? theme.palette.grey[300]
                : 'linear-gradient(135deg, #1565c0 0%, #00acc1 100%)',
            }
          }}
        >
          {loading ? 'Processing...' : 'PLAN TRIP'}
        </Button>
      </Box>
    </Paper>
  );
}

export default QueryForm;