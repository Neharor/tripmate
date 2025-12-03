import React, { useState, useEffect } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  Button,
  IconButton,
  Rating,
  CircularProgress,
  Container
} from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import FavoriteIcon from '@mui/icons-material/Favorite';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5002';

const DestinationCarousel = ({ onDestinationSelect }) => {
  const [favorites, setFavorites] = useState({});
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dataSource, setDataSource] = useState('');

  // Emoji and gradient mappings for destinations
  const destinationVisuals = {
    'bali': { emoji: '🏝️', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    'tokyo': { emoji: '🏯', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    'paris': { emoji: '🗼', gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
    'maldives': { emoji: '🌴', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    'new york': { emoji: '🗽', gradient: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%)' },
    'dubai': { emoji: '🏙️', gradient: 'linear-gradient(135deg, #f7971e 0%, #ffd200 100%)' },
    'london': { emoji: '🇬🇧', gradient: 'linear-gradient(135deg, #2c3e50 0%, #3498db 100%)' },
    'bangkok': { emoji: '🛕', gradient: 'linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%)' },
    'singapore': { emoji: '🏙️', gradient: 'linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)' },
    'barcelona': { emoji: '🏖️', gradient: 'linear-gradient(135deg, #f12711 0%, #f5af19 100%)' },
    'rome': { emoji: '🏛️', gradient: 'linear-gradient(135deg, #cb356b 0%, #bd3f32 100%)' },
    'sydney': { emoji: '🦘', gradient: 'linear-gradient(135deg, #1e9600 0%, #fff200 100%)' }
  };

  const getVisualForDestination = (destName) => {
    const lowerName = destName.toLowerCase();
    for (const [key, value] of Object.entries(destinationVisuals)) {
      if (lowerName.includes(key)) {
        return value;
      }
    }
    // Default visual
    return { emoji: '✈️', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' };
  };

  useEffect(() => {
    fetchTrendingDestinations();
  }, []);

  const fetchTrendingDestinations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/trending-destinations`);
      const data = await response.json();
      
      if (data.success || data.destinations) {
        // Transform backend data to frontend format
        const formattedDestinations = data.destinations.map((dest, index) => {
          const visual = getVisualForDestination(dest.destination);
          return {
            id: index + 1,
            name: dest.destination,
            emoji: visual.emoji,
            image: visual.gradient,
            tagline: dest.interests.slice(0, 2).join(' & ') || 'Popular destination',
            description: `Discover this trending destination loved by ${dest.trip_count} travelers.`,
            tags: dest.interests.slice(0, 3),
            rating: dest.rating || 4.5, // From Kaggle analysis
            reviews: dest.reviews || dest.trip_count * 8, // From Kaggle data
            avgCost: `$${dest.avg_budget}/day`,
            bestTime: dest.best_time || 'Year-round', // From Kaggle analysis
            highlights: dest.interests,
            tripCount: dest.trip_count,
            isTrending: !dest.is_fallback
          };
        });
        
        setDestinations(formattedDestinations);
        setDataSource(data.data_source);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching trending destinations:', error);
      setLoading(false);
      // Keep empty destinations array - will show loading state
    }
  };

  const toggleFavorite = (id, e) => {
    e.stopPropagation();
    setFavorites(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleDestinationClick = (destination) => {
    onDestinationSelect(destination.name);
  };

  return (
    <Box sx={{ py: 6, bgcolor: '#f8f9fa' }}>
      <Box sx={{ maxWidth: '1400px', mx: 'auto', px: { xs: 2, md: 4 } }}>
        {/* Header */}
        <Box sx={{ mb: 6, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
            <TrendingUpIcon sx={{ fontSize: 28, color: '#667eea' }} />
            <Typography
              variant="h4"
              sx={{
                fontWeight: 'bold',
                color: '#1a1a1a',
                fontSize: { xs: '24px', md: '32px' }
              }}
            >
              🌍 Trending Destinations Right Now
            </Typography>
          </Box>
          <Typography
            variant="body1"
            sx={{
              color: '#666',
              fontSize: '16px',
              maxWidth: '600px',
              mx: 'auto'
            }}
          >
            {dataSource === 'user_data' 
              ? 'Based on real trips planned by travelers like you - Click any destination to start planning!'
              : dataSource === 'mixed'
              ? 'Popular destinations loved by travelers worldwide - Click to explore!'
              : 'Explore our most popular destinations loved by travelers worldwide. Click any destination to start planning!'
            }
          </Typography>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <CircularProgress size={60} sx={{ color: '#667eea' }} />
          </Box>
        ) : destinations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" sx={{ color: '#64748b' }}>
              No trending destinations available at the moment
            </Typography>
          </Box>
        ) : (
        <>
        {/* Carousel */}
        <Box sx={{ position: 'relative' }}>
          <Swiper
            modules={[Navigation, Pagination, Autoplay]}
            navigation={{
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
              enabled: true
            }}
            pagination={{
              clickable: true,
              bulletClass: 'swiper-pagination-bullet',
              bulletActiveClass: 'swiper-pagination-bullet-active',
              el: '.swiper-pagination'
            }}
            autoplay={{
              delay: 5000,
              disableOnInteraction: false,
              pauseOnMouseEnter: true
            }}
            spaceBetween={24}
            slidesPerView={1}
            breakpoints={{
              640: {
                slidesPerView: 2,
                spaceBetween: 16
              },
              1024: {
                slidesPerView: 3,
                spaceBetween: 24
              },
              1400: {
                slidesPerView: 4,
                spaceBetween: 24
              }
            }}
            loop={true}
            speed={500}
            centeredSlides={false}
            watchSlidesProgress={true}
            sx={{
              '& .swiper-pagination': {
                position: 'static',
                mt: 4,
                display: 'flex',
                justifyContent: 'center',
                gap: '6px'
              },
              '& .swiper-pagination-bullet': {
                width: '12px',
                height: '12px',
                backgroundColor: '#ddd',
                opacity: 0.8,
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: '#999'
                }
              },
              '& .swiper-pagination-bullet-active': {
                backgroundColor: '#667eea',
                width: '32px',
                borderRadius: '6px'
              }
            }}
          >
            {destinations.map((dest) => (
              <SwiperSlide key={dest.id}>
                <DestinationCard
                  destination={dest}
                  isFavorite={favorites[dest.id]}
                  onToggleFavorite={(e) => toggleFavorite(dest.id, e)}
                  onSelect={() => handleDestinationClick(dest)}
                />
              </SwiperSlide>
            ))}
          </Swiper>

          {/* Navigation Buttons */}
          <IconButton
            className="swiper-button-prev"
            sx={{
              position: 'absolute',
              left: '-50px',
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              backgroundColor: '#667eea',
              color: 'white',
              '&:hover': {
                backgroundColor: '#764ba2'
              },
              '@media (max-width: 1024px)': {
                display: 'none'
              }
            }}
          >
            <ChevronLeftIcon />
          </IconButton>

          <IconButton
            className="swiper-button-next"
            sx={{
              position: 'absolute',
              right: '-50px',
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 10,
              backgroundColor: '#667eea',
              color: 'white',
              '&:hover': {
                backgroundColor: '#764ba2'
              },
              '@media (max-width: 1024px)': {
                display: 'none'
              }
            }}
          >
            <ChevronRightIcon />
          </IconButton>

          {/* Pagination */}
          <Box className="swiper-pagination" />
        </Box>

        {/* Call to Action */}
        <Box sx={{ textAlign: 'center', mt: 8 }}>
          <Typography variant="body1" sx={{ color: '#666', mb: 3 }}>
            Don't see your dream destination? Chat with TripMate AI to explore more options!
          </Typography>
          <Button
            variant="contained"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              px: 4,
              py: 1.5,
              fontSize: '16px',
              fontWeight: 'bold',
              '&:hover': {
                transform: 'scale(1.05)',
                boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            Explore All Destinations
          </Button>
        </Box>
        </>
        )}
      </Box>
    </Box>
  );
};

// Individual Destination Card Component
const DestinationCard = ({ destination, isFavorite, onToggleFavorite, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        border: 'none',
        boxShadow: isHovered
          ? '0 20px 40px rgba(0, 0, 0, 0.15)'
          : '0 4px 12px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s ease cubic-bezier(0.4, 0, 0.2, 1)',
        transform: isHovered ? 'translateY(-12px) scale(1.02)' : 'translateY(0)',
        borderRadius: '16px',
        overflow: 'hidden',
        background: 'white'
      }}
    >
      {/* Image Section */}
      <Box
        sx={{
          height: '200px',
          background: destination.image,
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          p: 2
        }}
      >
        {/* Emoji Badge */}
        <Box
          sx={{
            fontSize: '48px',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
            animation: isHovered ? 'bounce 0.6s ease' : 'none'
          }}
        >
          {destination.emoji}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {/* Trending Badge (if real user data) */}
          {destination.isTrending && destination.tripCount && (
            <Chip
              label={`${destination.tripCount} trips`}
              size="small"
              sx={{
                background: 'rgba(102, 126, 234, 0.95)',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '11px',
                height: '24px'
              }}
            />
          )}
          
          {/* Favorite Button */}
          <IconButton
            onClick={onToggleFavorite}
            sx={{
              background: 'rgba(255, 255, 255, 0.9)',
              '&:hover': {
                background: 'white'
              },
              transition: 'all 0.3s ease',
              width: 36,
              height: 36
            }}
          >
            {isFavorite ? (
              <FavoriteIcon sx={{ color: '#ef4444', fontSize: 20 }} />
            ) : (
              <FavoriteBorderIcon sx={{ color: '#666', fontSize: 20 }} />
            )}
          </IconButton>
        </Box>
      </Box>

      {/* Content Section */}
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 3 }}>
        {/* Destination Name */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 'bold',
            color: '#1a1a1a',
            mb: 1,
            fontSize: '18px'
          }}
        >
          {destination.name}
        </Typography>

        {/* Tagline */}
        <Typography
          variant="body2"
          sx={{
            color: '#667eea',
            fontWeight: '600',
            fontSize: '13px',
            mb: 2,
            fontStyle: 'italic'
          }}
        >
          {destination.tagline}
        </Typography>

        {/* Description */}
        <Typography
          variant="body2"
          sx={{
            color: '#666',
            mb: 2,
            lineHeight: 1.6,
            fontSize: '14px',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {destination.description}
        </Typography>

        {/* Rating */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
          <Rating
            value={destination.rating}
            precision={0.1}
            readOnly
            size="small"
            sx={{
              '& .MuiRating-icon': {
                color: '#ffc107'
              }
            }}
          />
          <Typography variant="caption" sx={{ color: '#999' }}>
            ({destination.reviews} reviews)
          </Typography>
        </Box>

        {/* Cost & Best Time */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, gap: 1 }}>
          <Box>
            <Typography variant="caption" sx={{ color: '#999', fontSize: '12px' }}>
              Avg Cost
            </Typography>
            <Typography sx={{ fontWeight: 'bold', color: '#10b981', fontSize: '14px' }}>
              {destination.avgCost}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ color: '#999', fontSize: '12px' }}>
              Best Time
            </Typography>
            <Typography sx={{ fontWeight: 'bold', color: '#f59e0b', fontSize: '14px' }}>
              {destination.bestTime}
            </Typography>
          </Box>
        </Box>

        {/* Tags */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
          {destination.tags.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              sx={{
                backgroundColor: '#f0f4ff',
                color: '#667eea',
                fontWeight: '500',
                fontSize: '12px',
                height: '28px',
                '&:hover': {
                  backgroundColor: '#667eea',
                  color: 'white'
                },
                transition: 'all 0.3s ease'
              }}
            />
          ))}
        </Box>

        {/* Highlights */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ color: '#999', fontSize: '12px', display: 'block', mb: 1 }}>
            Must-See Highlights
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            {destination.highlights.slice(0, 2).map((highlight, idx) => (
              <Typography
                key={idx}
                variant="caption"
                sx={{
                  color: '#666',
                  fontSize: '12px',
                  '&:after': {
                    content: idx < destination.highlights.length - 1 ? '"•"' : '""',
                    ml: 0.5
                  }
                }}
              >
                {highlight}
              </Typography>
            ))}
          </Box>
        </Box>

        {/* CTA Button */}
        <Button
          variant="contained"
          fullWidth
          sx={{
            background: isHovered
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : '#f0f4ff',
            color: isHovered ? 'white' : '#667eea',
            fontWeight: 'bold',
            mt: 'auto',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'scale(1.02)',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 8px 16px rgba(102, 126, 234, 0.3)'
            }
          }}
        >
          Plan Trip to {destination.name.split(',')[0]}
        </Button>
      </CardContent>
    </Card>
  );
};

export default DestinationCarousel;
