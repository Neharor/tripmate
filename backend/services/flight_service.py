"""
Real Flight Search using Amadeus API
Provides actual flight data with prices, airlines, and booking links
"""

from amadeus import Client, ResponseError
import os
from datetime import datetime, timedelta

class FlightService:
    """
    Service for searching real flights using Amadeus API
    """
    
    def __init__(self):
        # Initialize Amadeus client
        # Get API credentials from environment variables
        api_key = os.getenv('AMADEUS_API_KEY', '')
        api_secret = os.getenv('AMADEUS_API_SECRET', '')
        
        if api_key and api_secret:
            self.amadeus = Client(
                client_id=api_key,
                client_secret=api_secret
            )
            self.enabled = True
        else:
            print("⚠️  Amadeus API credentials not found. Flight search will use fallback mode.")
            print("   To enable real flights: Set AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables")
            print("   Get free API key from: https://developers.amadeus.com/register")
            self.amadeus = None
            self.enabled = False
    
    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, max_results=5):
        """
        Search for flights between origin and destination
        
        Args:
            origin: IATA code (e.g., "LAX" for Los Angeles)
            destination: IATA code (e.g., "DPS" for Bali)
            departure_date: Date in YYYY-MM-DD format
            return_date: Optional return date in YYYY-MM-DD format
            adults: Number of adult passengers
            max_results: Maximum number of flight offers to return
            
        Returns:
            List of flight offers with prices and details
        """
        
        if not self.enabled:
            return self._fallback_flights(origin, destination, departure_date, return_date)
        
        try:
            # Search for flight offers
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                returnDate=return_date,
                adults=adults,
                max=max_results
            )
            
            # Parse and format flight data
            flights = []
            for offer in response.data:
                flight_data = self._parse_flight_offer(offer)
                flights.append(flight_data)
            
            return flights
            
        except ResponseError as error:
            print(f"Amadeus API error: {error}")
            return self._fallback_flights(origin, destination, departure_date, return_date)
    
    def _parse_flight_offer(self, offer):
        """
        Parse Amadeus flight offer into simplified format
        """
        # Extract pricing
        price = float(offer['price']['total'])
        currency = offer['price']['currency']
        
        # Extract itinerary details
        itineraries = []
        for itinerary in offer['itineraries']:
            segments = []
            for segment in itinerary['segments']:
                segments.append({
                    'airline': segment['carrierCode'],
                    'flight_number': segment['number'],
                    'departure': {
                        'airport': segment['departure']['iataCode'],
                        'time': segment['departure']['at']
                    },
                    'arrival': {
                        'airport': segment['arrival']['iataCode'],
                        'time': segment['arrival']['at']
                    },
                    'duration': segment['duration']
                })
            itineraries.append({
                'segments': segments,
                'duration': itinerary['duration']
            })
        
        return {
            'id': offer['id'],
            'price': price,
            'currency': currency,
            'itineraries': itineraries,
            'numberOfBookableSeats': offer.get('numberOfBookableSeats', 0)
        }
    
    def _fallback_flights(self, origin, destination, departure_date, return_date=None):
        """
        Fallback flight suggestions when API is not available
        Uses general knowledge about airlines and routes
        """
        return [{
            'type': 'fallback',
            'message': 'Real-time flight data unavailable. Here are general suggestions:',
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'airlines': self._get_common_airlines(origin, destination),
            'estimated_price': self._estimate_price(origin, destination),
            'note': 'To see real flights with actual prices, set up Amadeus API credentials.'
        }]
    
    def _get_common_airlines(self, origin, destination):
        """
        Return common airlines that typically fly between regions
        """
        # Map of common routes to airlines
        airline_map = {
            'US-ASIA': ['Singapore Airlines', 'Cathay Pacific', 'Japan Airlines', 'Korean Air', 'EVA Air'],
            'US-EUROPE': ['Lufthansa', 'British Airways', 'Air France', 'KLM', 'United'],
            'US-DOMESTIC': ['Delta', 'United', 'American Airlines', 'Southwest'],
            'ASIA-ASIA': ['AirAsia', 'Singapore Airlines', 'Thai Airways', 'Garuda Indonesia'],
            'EUROPE-ASIA': ['Emirates', 'Qatar Airways', 'Turkish Airlines', 'Etihad']
        }
        
        # Determine route region
        if origin.startswith(('LAX', 'SFO', 'JFK', 'ORD')) and destination in ['DPS', 'BKK', 'HKT', 'CGK']:
            return airline_map['US-ASIA']
        else:
            return ['Multiple airlines available']
    
    def _estimate_price(self, origin, destination):
        """
        Rough price estimate based on route distance
        """
        # Very basic estimation - in real app, use historical data
        price_ranges = {
            'short': (100, 300),      # < 500 miles
            'medium': (300, 600),     # 500-1500 miles
            'long': (600, 1200),      # 1500-5000 miles
            'ultra_long': (800, 2000) # > 5000 miles
        }
        
        # For demo, assume most international flights are long-haul
        return price_ranges['ultra_long']
    
    def get_airport_code(self, city_name):
        """
        Get IATA airport code for a city
        This is a simple lookup - in production, use Amadeus Airport Search API
        """
        airport_codes = {
            'bali': 'DPS',
            'denpasar': 'DPS',
            'los angeles': 'LAX',
            'new york': 'JFK',
            'san francisco': 'SFO',
            'bangkok': 'BKK',
            'singapore': 'SIN',
            'tokyo': 'NRT',
            'paris': 'CDG',
            'london': 'LHR',
            'dubai': 'DXB',
            'sydney': 'SYD',
            'mumbai': 'BOM',
            'delhi': 'DEL'
        }
        
        return airport_codes.get(city_name.lower(), 'UNKNOWN')
