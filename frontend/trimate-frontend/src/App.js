import React, { useState } from 'react';
import { fetchItinerary } from './api';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import Avatar from '@mui/material/Avatar';
import Paper from '@mui/material/Paper';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  
  const formatTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatMessage = (rawMessage) => {
    try {
      console.log('Raw message received:', rawMessage);
      console.log('Type of message:', typeof rawMessage);
      
      if (typeof rawMessage === 'string') return rawMessage;
      
      const data = rawMessage;
      
      if (data.destinations || data.stays) {
        const destinations = data.destinations?.plan || [];
        const stays = data.stays?.stays || [];
        
        let response = '';
        if (destinations.length > 0) {
          response += '🌍 Suggested Destinations:\n' + destinations.map(d => `• ${d}`).join('\n');
        }
        if (stays.length > 0) {
          if (response) response += '\n\n';
          response += '🏨 Recommended Stays:\n' + stays.map(s => `• ${s}`).join('\n');
        }
        return response || 'No recommendations available';
      }
      
      return JSON.stringify(data, null, 2);
    } catch (error) {
      console.error('Error formatting message:', error);
      return String(rawMessage);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;
    
    const query = inputValue;
    setInputValue('');
    
    const userMessage = {
      message: query,
      sentTime: formatTimestamp(),
      sender: "user",
      direction: "outgoing"
    };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const result = await fetchItinerary(query);
      console.log('API result:', result);
      
      const formattedMessage = formatMessage(result);
      
      const assistantMessage = {
        message: formattedMessage,
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (e) {
      console.error('API error:', e);
      const errorMessage = {
        message: `Sorry, I encountered an error: ${e.message || 'Failed to fetch itinerary'}`,
        sentTime: formatTimestamp(),
        sender: "TripMate",
        direction: "incoming"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
      bgcolor: '#f8fafc',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <AppBar 
        position="static" 
        elevation={0}
        sx={{ 
          bgcolor: '#1e293b',
          borderBottom: '1px solid #334155'
        }}
      >
        <Toolbar sx={{ py: 1 }}>
          <SmartToyIcon sx={{ mr: 2, fontSize: 32, color: '#60a5fa' }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: '-0.5px' }}>
            TripMate
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8, fontWeight: 400 }}>
            AI Travel Planner
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Chat Messages Area */}
      <Box sx={{ 
        flexGrow: 1,
        overflow: 'auto',
        p: 3,
        bgcolor: '#ffffff'
      }}>
        {messages.length === 0 && (
          <Box sx={{ 
            textAlign: 'center', 
            color: '#94a3b8', 
            mt: 12,
            px: 4
          }}>
            <SmartToyIcon sx={{ fontSize: 72, opacity: 0.2, mb: 3, color: '#cbd5e1' }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 2, color: '#334155' }}>
              Welcome to TripMate
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b', maxWidth: '500px', mx: 'auto' }}>
              Your intelligent travel planning assistant. Ask me about destinations, accommodations, or create a complete itinerary.
            </Typography>
          </Box>
        )}
        
        {messages.map((msg, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              gap: 2, 
              mb: 3,
              justifyContent: msg.direction === 'outgoing' ? 'flex-end' : 'flex-start'
            }}
          >
            {msg.direction === 'incoming' && (
              <Avatar sx={{ 
                bgcolor: '#ef4444',
                width: 40,
                height: 40
              }}>
                <SmartToyIcon sx={{ fontSize: 22 }} />
              </Avatar>
            )}
            
            <Box sx={{ maxWidth: '70%' }}>
              <Paper sx={{ 
                background: msg.direction === "outgoing" ? '#3b82f6' : '#f1f5f9',
                color: msg.direction === "outgoing" ? '#ffffff' : '#1e293b',
                padding: '14px 18px',
                borderRadius: '16px',
                boxShadow: msg.direction === "outgoing" 
                  ? '0 2px 8px rgba(59, 130, 246, 0.25)'
                  : '0 1px 3px rgba(0,0,0,0.08)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                <Typography sx={{
                  fontSize: '15px',
                  lineHeight: '1.6',
                  fontWeight: 400
                }}>
                  {msg.message}
                </Typography>
              </Paper>
              <Typography sx={{
                fontSize: '13px',
                color: '#64748b',
                marginTop: '8px',
                padding: '0 6px',
                textAlign: msg.direction === "outgoing" ? 'right' : 'left',
                fontWeight: 500
              }}>
                {msg.sender === "user" ? "You" : "TripMate"} • {msg.sentTime}
              </Typography>
            </Box>
            
            {msg.direction === 'outgoing' && (
              <Avatar sx={{ 
                bgcolor: '#3b82f6',
                width: 40,
                height: 40
              }}>
                <PersonIcon sx={{ fontSize: 22 }} />
              </Avatar>
            )}
          </Box>
        ))}
        
        {loading && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2,
            color: '#64748b'
          }}>
            <Avatar sx={{ 
              bgcolor: '#ef4444',
              width: 40,
              height: 40
            }}>
              <SmartToyIcon sx={{ fontSize: 22 }} />
            </Avatar>
            <Typography variant="body1" sx={{ fontStyle: 'italic', fontWeight: 500 }}>
              TripMate is thinking...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Input Area - Fixed at Bottom */}
      <Box 
        component="form"
        onSubmit={handleSubmit}
        sx={{ 
          borderTop: '2px solid #e2e8f0',
          bgcolor: '#ffffff',
          p: 2,
          display: 'flex',
          gap: 1,
          alignItems: 'center'
        }}
      >
        <TextField
          fullWidth
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask me about your trip..."
          disabled={loading}
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
              backgroundColor: '#ffffff',
              fontSize: '15px',
              '& fieldset': {
                borderColor: '#e2e8f0',
              },
              '&:hover fieldset': {
                borderColor: '#cbd5e1',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#3b82f6',
              }
            }
          }}
        />
        <IconButton 
          type="submit"
          disabled={loading || !inputValue.trim()}
          sx={{ 
            bgcolor: '#3b82f6',
            color: '#ffffff',
            '&:hover': {
              bgcolor: '#2563eb'
            },
            '&:disabled': {
              bgcolor: '#e2e8f0',
              color: '#94a3b8'
            },
            width: 48,
            height: 48
          }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
