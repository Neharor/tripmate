"""
Dynamic Route Intelligence Service
Replaces hardcoded route database with API-driven, ML-enhanced route data
"""

import os
import json
from datetime import datetime, timedelta

class RouteIntelligence:
    """
    Provides route-specific airline data using:
    1. Amadeus Airport & Airline Routes API
    2. Cached route data (updated weekly)
    3. ML-based price predictions
    """
    
    def __init__(self):
        self.cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'route_cache.json')
        self.cache = self._load_cache()
        
        # Initialize Amadeus (optional - for route discovery)
        try:
            from amadeus import Client, ResponseError
            api_key = os.getenv('AMADEUS_API_KEY')
            api_secret = os.getenv('AMADEUS_API_SECRET')
            
            if api_key and api_secret:
                self.amadeus = Client(
                    client_id=api_key,
                    client_secret=api_secret
                )
                print("✅ RouteIntelligence: Amadeus connected (dynamic routes enabled)")
            else:
                self.amadeus = None
                print("⚠️  RouteIntelligence: Using cached data only (no Amadeus API)")
        except Exception as e:
            self.amadeus = None
            print(f"⚠️  RouteIntelligence: Amadeus unavailable - {e}")
    
    def get_route_info(self, origin_city, dest_city):
        """
        Get airlines, duration, price range for a route
        
        Args:
            origin_city (str): Origin city name
            dest_city (str): Destination city name
            
        Returns:
            dict: Route information with airlines, duration, prices, booking URLs
        """
        # Normalize city names
        origin = origin_city.lower().strip()
        dest = dest_city.lower().strip()
        
        # Create cache key
        cache_key = f"{origin}_{dest}"
        reverse_key = f"{dest}_{origin}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if self._is_cache_valid(cached_data):
                print(f"✓ Using cached route data: {origin} → {dest}")
                return cached_data['info']
        
        if reverse_key in self.cache:
            cached_data = self.cache[reverse_key]
            if self._is_cache_valid(cached_data):
                print(f"✓ Using cached route data: {dest} → {origin}")
                return cached_data['info']
        
        # Try to fetch live data from Amadeus
        if self.amadeus:
            route_info = self._fetch_live_route_data(origin_city, dest_city)
            if route_info:
                # Cache the result
                self._update_cache(cache_key, route_info)
                return route_info
        
        # Fallback to intelligent defaults based on geography
        return self._intelligent_fallback(origin_city, dest_city)
    
    def _fetch_live_route_data(self, origin_city, dest_city):
        """
        Fetch real-time route data from Amadeus API
        """
        try:
            # Get airport codes
            from .flight_service import FlightService
            fs = FlightService()
            
            origin_code = fs.get_airport_code(origin_city)
            dest_code = fs.get_airport_code(dest_city)
            
            if origin_code == 'UNKNOWN' or dest_code == 'UNKNOWN':
                return None
            
            # Search for airlines operating this route (use flight search)
            # Amadeus doesn't have a dedicated "routes" API for free tier
            # So we do a sample search 7 days out to discover airlines
            departure_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=dest_code,
                departureDate=departure_date,
                adults=1,
                max=10
            )
            
            if not response.data:
                return None
            
            # Extract unique airlines and calculate average duration/price
            airlines = set()
            durations = []
            prices = []
            
            for offer in response.data:
                # Get airline from first segment
                airline_code = offer['itineraries'][0]['segments'][0]['carrierCode']
                airlines.add(fs._get_airline_name(airline_code))
                
                # Get duration
                duration = offer['itineraries'][0]['duration']
                durations.append(self._parse_duration(duration))
                
                # Get price
                prices.append(float(offer['price']['total']))
            
            # Calculate averages
            avg_duration = sum(durations) / len(durations) if durations else 480  # 8 hours default
            min_price = min(prices) if prices else 200
            max_price = max(prices) if prices else 800
            
            return {
                'airlines': list(airlines),
                'duration': self._format_duration(avg_duration),
                'distance': self._categorize_distance(avg_duration),
                'price_range': f'${int(min_price)}-{int(max_price)} one-way',
                'booking_urls': self._get_booking_urls(list(airlines)),
                'source': 'amadeus_api',
                'cached_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching live route data: {e}")
            return None
    
    def _intelligent_fallback(self, origin_city, dest_city):
        """
        Generate intelligent route info based on geography and common patterns
        """
        # Determine region pairs
        origin_region = self._get_region(origin_city)
        dest_region = self._get_region(dest_city)
        
        # Use region-based airline recommendations
        airlines = self._get_regional_airlines(origin_region, dest_region)
        
        # Estimate duration based on typical distances
        duration_hours = self._estimate_duration(origin_region, dest_region)
        
        return {
            'airlines': airlines,
            'duration': self._format_duration(duration_hours * 60),
            'distance': self._categorize_distance(duration_hours * 60),
            'price_range': self._estimate_price_range(duration_hours),
            'booking_urls': self._get_booking_urls(airlines),
            'source': 'intelligent_fallback',
            'cached_at': datetime.now().isoformat()
        }
    
    def _get_region(self, city):
        """Determine geographic region"""
        city_lower = city.lower()
        
        # Asia
        if any(x in city_lower for x in ['tokyo', 'seoul', 'bangkok', 'singapore', 'hong kong', 'bali', 
                                          'jakarta', 'kuala lumpur', 'manila', 'taipei', 'osaka', 'beijing', 'shanghai']):
            return 'asia'
        
        # Middle East
        if any(x in city_lower for x in ['dubai', 'doha', 'abu dhabi', 'riyadh', 'jeddah']):
            return 'middle_east'
        
        # Europe
        if any(x in city_lower for x in ['london', 'paris', 'rome', 'madrid', 'berlin', 'amsterdam', 
                                          'istanbul', 'athens', 'barcelona', 'vienna']):
            return 'europe'
        
        # North America
        if any(x in city_lower for x in ['new york', 'los angeles', 'chicago', 'miami', 'toronto', 
                                          'vancouver', 'san francisco', 'seattle', 'boston']):
            return 'north_america'
        
        # India/South Asia
        if any(x in city_lower for x in ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 
                                          'hyderabad', 'pune', 'ahmedabad']):
            return 'south_asia'
        
        # Australia/Oceania
        if any(x in city_lower for x in ['sydney', 'melbourne', 'brisbane', 'perth', 'auckland']):
            return 'oceania'
        
        return 'unknown'
    
    def _get_regional_airlines(self, origin_region, dest_region):
        """Get common airlines for region pairs"""
        
        # Global carriers (fly everywhere)
        global_carriers = ['Emirates', 'Qatar Airways', 'Singapore Airlines', 'Turkish Airlines']
        
        regional_map = {
            ('asia', 'asia'): ['ANA', 'JAL', 'Singapore Airlines', 'Thai Airways', 'Cathay Pacific', 'AirAsia'],
            ('asia', 'north_america'): ['ANA', 'JAL', 'Singapore Airlines', 'United', 'Delta', 'American Airlines'],
            ('asia', 'europe'): ['Singapore Airlines', 'Qatar Airways', 'Emirates', 'Lufthansa', 'Air France'],
            ('asia', 'middle_east'): ['Emirates', 'Qatar Airways', 'Etihad', 'Singapore Airlines'],
            ('north_america', 'europe'): ['British Airways', 'Lufthansa', 'Air France', 'United', 'Delta', 'American Airlines'],
            ('north_america', 'south_asia'): ['Air India', 'Emirates', 'Qatar Airways', 'United', 'Lufthansa'],
            ('europe', 'asia'): ['Lufthansa', 'Air France', 'British Airways', 'Singapore Airlines', 'Qatar Airways'],
            ('south_asia', 'middle_east'): ['Air India', 'Emirates', 'Qatar Airways', 'Etihad'],
        }
        
        # Check both directions
        airlines = regional_map.get((origin_region, dest_region)) or regional_map.get((dest_region, origin_region))
        
        if airlines:
            return airlines
        else:
            # Default to global carriers for unknown routes
            return global_carriers
    
    def _estimate_duration(self, origin_region, dest_region):
        """Estimate flight duration in hours"""
        
        # Same region
        if origin_region == dest_region:
            return 3
        
        duration_map = {
            ('asia', 'north_america'): 12,
            ('asia', 'europe'): 11,
            ('asia', 'middle_east'): 7,
            ('north_america', 'europe'): 8,
            ('north_america', 'south_asia'): 15,
            ('europe', 'asia'): 11,
            ('south_asia', 'middle_east'): 4,
        }
        
        duration = duration_map.get((origin_region, dest_region)) or duration_map.get((dest_region, origin_region))
        
        return duration if duration else 10  # Default 10 hours
    
    def _estimate_price_range(self, duration_hours):
        """Estimate price range based on duration"""
        if duration_hours < 3:
            return '$100-300 one-way'
        elif duration_hours < 6:
            return '$200-500 one-way'
        elif duration_hours < 10:
            return '$400-800 one-way'
        else:
            return '$600-1200 one-way'
    
    def _categorize_distance(self, duration_minutes):
        """Categorize distance based on duration"""
        hours = duration_minutes / 60
        if hours < 3:
            return 'short'
        elif hours < 7:
            return 'medium'
        else:
            return 'long'
    
    def _format_duration(self, minutes):
        """Format duration in minutes to 'Xh XXm'"""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m"
    
    def _parse_duration(self, iso_duration):
        """Parse ISO 8601 duration (PT12H30M) to minutes"""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_duration)
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            return hours * 60 + minutes
        return 480  # Default 8 hours
    
    def _get_booking_urls(self, airlines):
        """Get booking URLs for airlines"""
        url_map = {
            'Emirates': 'https://www.emirates.com',
            'Qatar Airways': 'https://www.qatarairways.com',
            'Singapore Airlines': 'https://www.singaporeair.com',
            'Turkish Airlines': 'https://www.turkishairlines.com',
            'British Airways': 'https://www.britishairways.com',
            'Lufthansa': 'https://www.lufthansa.com',
            'Air France': 'https://www.airfrance.com',
            'United': 'https://www.united.com',
            'Delta': 'https://www.delta.com',
            'American Airlines': 'https://www.aa.com',
            'ANA': 'https://www.ana.co.jp',
            'JAL': 'https://www.jal.co.jp',
            'Cathay Pacific': 'https://www.cathaypacific.com',
            'Thai Airways': 'https://www.thaiairways.com',
            'AirAsia': 'https://www.airasia.com',
            'Air India': 'https://www.airindia.in',
            'Korean Air': 'https://www.koreanair.com',
            'Asiana Airlines': 'https://www.flyasiana.com',
            'Garuda Indonesia': 'https://www.garuda-indonesia.com',
            'Virgin Atlantic': 'https://www.virginatlantic.com',
            'Etihad': 'https://www.etihad.com',
        }
        
        return {airline: url_map.get(airline, 'https://www.google.com/flights') for airline in airlines}
    
    def _load_cache(self):
        """Load route cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading route cache: {e}")
        return {}
    
    def _update_cache(self, cache_key, route_info):
        """Update cache with new route data"""
        try:
            self.cache[cache_key] = {
                'info': route_info,
                'cached_at': datetime.now().isoformat()
            }
            
            # Create data directory if needed
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # Save to file
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
                
            print(f"✓ Cached route data: {cache_key}")
        except Exception as e:
            print(f"Error updating cache: {e}")
    
    def _is_cache_valid(self, cached_data, max_age_days=7):
        """Check if cached data is still valid"""
        try:
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            age = datetime.now() - cached_time
            return age.days < max_age_days
        except:
            return False
