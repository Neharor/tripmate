import React from 'react';
import { Box, Avatar, Typography } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

function ChatBubble({ message, type, timestamp }) {
  const isUser = type === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 1,
        mb: 2,
        alignItems: 'flex-start',
      }}
    >
      <Avatar
        sx={{
          bgcolor: isUser ? 'primary.main' : 'secondary.main',
          width: 32,
          height: 32,
        }}
      >
        {isUser ? <PersonIcon /> : <SmartToyIcon />}
      </Avatar>
      
      <Box sx={{ maxWidth: '70%' }}>
        <Box
          sx={{
            bgcolor: isUser ? 'primary.main' : 'grey.100',
            color: isUser ? 'white' : 'text.primary',
            p: 2,
            borderRadius: 3,
            borderTopLeftRadius: !isUser ? 0 : 3,
            borderTopRightRadius: isUser ? 0 : 3,
          }}
        >
          {message}
        </Box>
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 0.5,
            color: 'text.secondary',
            textAlign: isUser ? 'right' : 'left',
          }}
        >
          {timestamp}
        </Typography>
      </Box>
    </Box>
  );
}

export default ChatBubble;