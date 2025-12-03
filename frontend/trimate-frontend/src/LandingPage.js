import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import HotelIcon from '@mui/icons-material/Hotel';
import ExploreIcon from '@mui/icons-material/Explore';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import SpeedIcon from '@mui/icons-material/Speed';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DestinationCarousel from './components/DestinationCarousel';
import './styles/carousel.css';

export default function LandingPage({ onStartPlanning, onViewTrips }) {
  const handleDestinationSelect = (destination) => {
    // Store destination and navigate to chat
    localStorage.setItem('selectedDestination', destination);
    onStartPlanning();
  };
  const features = [
    {
      icon: <SmartToyIcon sx={{ fontSize: 48, color: '#3b82f6' }} />,
      title: 'AI-Powered Planning',
      description: 'Our intelligent agents analyze your preferences and create personalized trip recommendations in seconds.'
    },
    {
      icon: <FlightTakeoffIcon sx={{ fontSize: 48, color: '#10b981' }} />,
      title: 'Real Flight Data',
      description: 'Get actual flight prices and availability from 200+ airlines worldwide via Amadeus API.'
    },
    {
      icon: <HotelIcon sx={{ fontSize: 48, color: '#f59e0b' }} />,
      title: 'Hotel Recommendations',
      description: 'Curated stays based on your budget, preferences, and travel style - from hostels to luxury resorts.'
    },
    {
      icon: <ExploreIcon sx={{ fontSize: 48, color: '#8b5cf6' }} />,
      title: 'Complete Itineraries',
      description: 'Day-by-day plans with activities, dining, and local experiences tailored to your interests.'
    },
    {
      icon: <AttachMoneyIcon sx={{ fontSize: 48, color: '#06b6d4' }} />,
      title: 'Smart Budgeting',
      description: 'Detailed cost breakdowns for flights, accommodations, food, and activities to match your budget.'
    },
    {
      icon: <WbSunnyIcon sx={{ fontSize: 48, color: '#ef4444' }} />,
      title: 'Weather Intelligence',
      description: 'Climate insights and seasonal recommendations to help you pick the perfect travel dates.'
    }
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Tell Us Your Preferences',
      description: 'Simply chat with TripMate about where you want to go, your budget, dates, and interests.'
    },
    {
      step: '2',
      title: 'AI Creates Your Plan',
      description: 'Our multi-agent system analyzes destinations, flights, hotels, weather, and activities in seconds.'
    },
    {
      step: '3',
      title: 'Review & Customize',
      description: 'Get a complete trip plan with flight options, hotel recommendations, and day-by-day itinerary.'
    },
    {
      step: '4',
      title: 'Book & Travel',
      description: 'Book your flights and hotels directly, then follow your personalized itinerary!'
    }
  ];

  return (
    <Box sx={{ bgcolor: '#ffffff', minHeight: '100vh' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#ffffff',
          py: { xs: 8, md: 16 },
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Animated background circles */}
        <Box sx={{
          position: 'absolute',
          top: '-10%',
          right: '-5%',
          width: '500px',
          height: '500px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          animation: 'float 6s ease-in-out infinite'
        }} />
        <Box sx={{
          position: 'absolute',
          bottom: '-15%',
          left: '-10%',
          width: '600px',
          height: '600px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.05)',
          animation: 'float 8s ease-in-out infinite reverse'
        }} />

        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          {/* My Trips Button - Top Right */}
          <Box sx={{ position: 'absolute', top: 20, right: 20 }}>
            <Button
              variant="contained"
              onClick={() => onViewTrips && onViewTrips()}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: '#ffffff',
                px: 3,
                py: 1.5,
                borderRadius: '25px',
                textTransform: 'none',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                fontWeight: 600,
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.3)',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s'
              }}
            >
              🗺️ My Trips
            </Button>
          </Box>

          <Box sx={{ textAlign: 'center', maxWidth: '800px', mx: 'auto' }}>
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '4rem' },
                fontWeight: 800,
                mb: 2,
                lineHeight: 1.2,
                textShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            >
              Plan Your Dream Trip in Seconds
            </Typography>
            <Typography
              variant="h5"
              sx={{
                fontSize: { xs: '1.1rem', md: '1.5rem' },
                mb: 4,
                opacity: 0.95,
                fontWeight: 400,
                lineHeight: 1.6
              }}
            >
              AI-powered travel planning that finds you the best flights, hotels, and experiences - all in one conversation.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                onClick={onStartPlanning}
                startIcon={<SmartToyIcon />}
                sx={{
                  bgcolor: '#ffffff',
                  color: '#667eea',
                  px: 4,
                  py: 2,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  borderRadius: '12px',
                  textTransform: 'none',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                  '&:hover': {
                    bgcolor: '#f8fafc',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 12px 32px rgba(0,0,0,0.2)'
                  },
                  transition: 'all 0.3s'
                }}
              >
                Start Planning Now
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => onStartPlanning && typeof onStartPlanning === 'function' ? onStartPlanning() : window.location.href = '/trips'}
                sx={{
                  borderColor: '#ffffff',
                  color: '#ffffff',
                  px: 4,
                  py: 2,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: '12px',
                  textTransform: 'none',
                  borderWidth: '2px',
                  '&:hover': {
                    borderWidth: '2px',
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    transform: 'translateY(-2px)'
                  },
                  transition: 'all 0.3s'
                }}
              >
                See How It Works
              </Button>
            </Box>
            
            {/* Stats */}
            <Box sx={{ mt: 8, display: 'flex', justifyContent: 'center', gap: 6, flexWrap: 'wrap' }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography sx={{ fontSize: '2.5rem', fontWeight: 800, mb: 0.5 }}>5 sec</Typography>
                <Typography sx={{ fontSize: '0.9rem', opacity: 0.9 }}>Average Planning Time</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography sx={{ fontSize: '2.5rem', fontWeight: 800, mb: 0.5 }}>200+</Typography>
                <Typography sx={{ fontSize: '0.9rem', opacity: 0.9 }}>Airlines Worldwide</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography sx={{ fontSize: '2.5rem', fontWeight: 800, mb: 0.5 }}>95%</Typography>
                <Typography sx={{ fontSize: '0.9rem', opacity: 0.9 }}>Confidence Score</Typography>
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Destination Carousel Section */}
      <DestinationCarousel onDestinationSelect={handleDestinationSelect} />

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 12 }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography variant="h2" sx={{ fontSize: { xs: '2rem', md: '3rem' }, fontWeight: 700, mb: 2, color: '#1e293b' }}>
            Everything You Need in One Place
          </Typography>
          <Typography variant="h6" sx={{ color: '#64748b', maxWidth: '700px', mx: 'auto', lineHeight: 1.6 }}>
            TripMate combines multiple AI agents to handle every aspect of your trip planning
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  borderRadius: '16px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 32px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5, color: '#1e293b' }}>
                    {feature.title}
                  </Typography>
                  <Typography sx={{ color: '#64748b', lineHeight: 1.7 }}>
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works Section */}
      <Box id="how-it-works" sx={{ bgcolor: '#f8fafc', py: 12 }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography variant="h2" sx={{ fontSize: { xs: '2rem', md: '3rem' }, fontWeight: 700, mb: 2, color: '#1e293b' }}>
              How It Works
            </Typography>
            <Typography variant="h6" sx={{ color: '#64748b', maxWidth: '700px', mx: 'auto', lineHeight: 1.6 }}>
              From conversation to complete itinerary in 4 simple steps
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {howItWorks.map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '2rem',
                      fontWeight: 800,
                      mx: 'auto',
                      mb: 3,
                      boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)'
                    }}
                  >
                    {item.step}
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5, color: '#1e293b' }}>
                    {item.title}
                  </Typography>
                  <Typography sx={{ color: '#64748b', lineHeight: 1.7, px: 2 }}>
                    {item.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Benefits Section */}
      <Container maxWidth="lg" sx={{ py: 12 }}>
        <Grid container spacing={8} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h2" sx={{ fontSize: { xs: '2rem', md: '2.5rem' }, fontWeight: 700, mb: 3, color: '#1e293b' }}>
              Why Choose TripMate?
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {[
                'Real-time flight prices from Amadeus API',
                'Personalized recommendations based on your preferences',
                'Complete itineraries with activities and dining',
                'Smart budget optimization',
                'Weather-aware travel planning',
                'Compare multiple options instantly'
              ].map((benefit, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <CheckCircleIcon sx={{ color: '#10b981', fontSize: 28 }} />
                  <Typography sx={{ fontSize: '1.1rem', color: '#334155', fontWeight: 500 }}>
                    {benefit}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                bgcolor: '#f1f5f9',
                borderRadius: '24px',
                p: 4,
                border: '2px solid #e2e8f0'
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1e293b' }}>
                🚀 Fast & Efficient
              </Typography>
              <Typography sx={{ mb: 3, color: '#64748b', lineHeight: 1.7 }}>
                Traditional trip planning takes hours of research across multiple websites. TripMate does it all in seconds.
              </Typography>
              
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1e293b' }}>
                💰 Save Money
              </Typography>
              <Typography sx={{ mb: 3, color: '#64748b', lineHeight: 1.7 }}>
                Our AI compares hundreds of options to find you the best deals on flights and accommodations.
              </Typography>
              
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1e293b' }}>
                ✨ Personalized Experience
              </Typography>
              <Typography sx={{ color: '#64748b', lineHeight: 1.7 }}>
                Every recommendation is tailored to your budget, interests, and travel style.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#ffffff',
          py: 10
        }}
      >
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h2" sx={{ fontSize: { xs: '2rem', md: '3rem' }, fontWeight: 800, mb: 3 }}>
              Ready to Plan Your Next Adventure?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.95, lineHeight: 1.6 }}>
              Start chatting with TripMate now and get a complete trip plan in seconds - completely free!
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={onStartPlanning}
              startIcon={<SmartToyIcon />}
              sx={{
                bgcolor: '#ffffff',
                color: '#667eea',
                px: 5,
                py: 2.5,
                fontSize: '1.2rem',
                fontWeight: 700,
                borderRadius: '12px',
                textTransform: 'none',
                boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                '&:hover': {
                  bgcolor: '#f8fafc',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 32px rgba(0,0,0,0.2)'
                },
                transition: 'all 0.3s'
              }}
            >
              Start Planning For Free
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: '#1e293b', color: '#94a3b8', py: 6 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <SmartToyIcon sx={{ fontSize: 32, color: '#60a5fa' }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff' }}>
                  TripMate
                </Typography>
              </Box>
              <Typography sx={{ mb: 2, lineHeight: 1.7 }}>
                AI-powered travel planning that makes trip planning effortless. Get personalized recommendations, real flight prices, and complete itineraries in seconds.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#ffffff' }}>
                Powered By
              </Typography>
              <Typography sx={{ lineHeight: 1.7 }}>
                • Amadeus Flight API (200+ airlines)<br />
                • Groq AI (Lightning-fast LLM)<br />
                • Multi-agent Architecture<br />
                • Real-time Data Processing
              </Typography>
            </Grid>
          </Grid>
          <Box sx={{ borderTop: '1px solid #334155', mt: 4, pt: 4, textAlign: 'center' }}>
            <Typography sx={{ fontSize: '0.9rem' }}>
              © 2025 TripMate. Built with ❤️ using AI, Flask, and React.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* CSS for animations */}
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
          }
        `}
      </style>
    </Box>
  );
}
