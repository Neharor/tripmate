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
            try:
                self.amadeus = Client(
                    client_id=api_key,
                    client_secret=api_secret
                )
                self.enabled = True
                print("✅ Amadeus API connected successfully!")
                print(f"   API Key: {api_key[:8]}...")
            except Exception as e:
                print(f"❌ Amadeus API initialization failed: {e}")
                self.amadeus = None
                self.enabled = False
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
            # Search for flight offers (request USD pricing for universal understanding)
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                returnDate=return_date,
                adults=adults,
                currencyCode='USD',
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
            total_duration_mins = self._parse_duration(itinerary['duration'])
            
            for segment in itinerary['segments']:
                airline_code = segment['carrierCode']
                airline_name = self._get_airline_name(airline_code)
                
                segments.append({
                    'airline': airline_code,
                    'airline_name': airline_name,
                    'flight_number': f"{airline_code} {segment['number']}",
                    'departure': {
                        'airport': segment['departure']['iataCode'],
                        'time': segment['departure']['at'],
                        'terminal': segment['departure'].get('terminal', '')
                    },
                    'arrival': {
                        'airport': segment['arrival']['iataCode'],
                        'time': segment['arrival']['at'],
                        'terminal': segment['arrival'].get('terminal', '')
                    },
                    'duration': segment['duration'],
                    'aircraft': segment.get('aircraft', {}).get('code', 'Unknown')
                })
            
            # Determine if direct flight
            is_direct = len(segments) == 1
            stops = len(segments) - 1
            
            itineraries.append({
                'segments': segments,
                'duration': itinerary['duration'],
                'duration_mins': total_duration_mins,
                'is_direct': is_direct,
                'stops': stops
            })
        
        return {
            'id': offer['id'],
            'price': price,
            'currency': currency,
            'itineraries': itineraries,
            'numberOfBookableSeats': offer.get('numberOfBookableSeats', 0),
            'validatingAirlineCodes': offer.get('validatingAirlineCodes', []),
            'is_real': True,  # Mark as real Amadeus data
            'data_source': 'Amadeus API'
        }
    
    def _parse_duration(self, duration_str):
        """
        Parse ISO 8601 duration (e.g., 'PT2H30M') to minutes
        """
        import re
        hours = 0
        minutes = 0
        
        # Extract hours
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Extract minutes
        min_match = re.search(r'(\d+)M', duration_str)
        if min_match:
            minutes = int(min_match.group(1))
        
        return hours * 60 + minutes
    
    def _get_airline_name(self, code):
        """
        Map IATA airline codes to full names
        """
        airline_names = {
            # Major Global Carriers
            'SQ': 'Singapore Airlines',
            'EK': 'Emirates',
            'QR': 'Qatar Airways',
            'TK': 'Turkish Airlines',
            'NH': 'All Nippon Airways (ANA)',
            'JL': 'Japan Airlines',
            'KE': 'Korean Air',
            'OZ': 'Asiana Airlines',
            'CX': 'Cathay Pacific',
            'BR': 'EVA Air',
            
            # US Carriers
            'AA': 'American Airlines',
            'DL': 'Delta Air Lines',
            'UA': 'United Airlines',
            'WN': 'Southwest Airlines',
            'B6': 'JetBlue Airways',
            'AS': 'Alaska Airlines',
            
            # European Carriers
            'LH': 'Lufthansa',
            'BA': 'British Airways',
            'AF': 'Air France',
            'KL': 'KLM Royal Dutch Airlines',
            'IB': 'Iberia',
            'AZ': 'ITA Airways',
            'LX': 'Swiss International Air Lines',
            'OS': 'Austrian Airlines',
            
            # Asian LCC & Regional
            'AK': 'AirAsia',
            'FD': 'Thai AirAsia',
            'D7': 'AirAsia X',
            'JT': 'Lion Air',
            'GA': 'Garuda Indonesia',
            'TG': 'Thai Airways',
            'VN': 'Vietnam Airlines',
            'CI': 'China Airlines',
            'MH': 'Malaysia Airlines',
            '3K': 'Jetstar Asia',
            'TR': 'Scoot',
            
            # Middle East
            'EY': 'Etihad Airways',
            'WY': 'Oman Air',
            'MS': 'EgyptAir',
            
            # Oceania
            'QF': 'Qantas',
            'NZ': 'Air New Zealand',
            
            # Others
            'AI': 'Air India',
            '6E': 'IndiGo',
            'SG': 'SpiceJet',
            'UK': 'Vistara'
        }
        
        return airline_names.get(code, code)
    
    def _fallback_flights(self, origin, destination, departure_date, return_date=None):
        """
        Generate realistic flight data when API is unavailable
        Returns structured flight data matching Amadeus format
        """
        import random
        from datetime import datetime, timedelta
        
        # Get realistic airlines for route
        airlines = self._get_route_airlines(origin, destination)
        price_range = self._get_route_price_range(origin, destination)
        
        flights = []
        
        # Generate 3 realistic flight options
        for i, (airline_info, price_modifier) in enumerate(zip(airlines[:3], [1.0, 0.85, 1.15])):
            base_price = random.randint(price_range[0], price_range[1])
            final_price = int(base_price * price_modifier)
            
            # Generate realistic times
            dep_hour = random.choice([7, 8, 9, 14, 16, 22]) if i < 2 else random.choice([6, 23])
            dep_minute = random.choice([0, 15, 30, 45])
            
            # Calculate arrival based on route duration
            duration_hours = self._get_route_duration(origin, destination)
            arr_time = (dep_hour + duration_hours) % 24
            
            flight_data = {
                'id': f'fallback_{i+1}',
                'price': final_price,
                'currency': 'USD',
                'itineraries': [{
                    'segments': [{
                        'airline': airline_info['code'],
                        'airline_name': airline_info['name'],
                        'flight_number': f"{airline_info['code']}{random.randint(100, 999)}",
                        'departure': {
                            'airport': origin,
                            'time': f"{departure_date}T{dep_hour:02d}:{dep_minute:02d}:00",
                            'terminal': random.choice(['1', '2', '3', 'A', 'B'])
                        },
                        'arrival': {
                            'airport': destination,
                            'time': f"{departure_date}T{arr_time:02d}:{dep_minute:02d}:00",
                            'terminal': random.choice(['1', '2', '3', 'A', 'B'])
                        },
                        'duration': f"PT{duration_hours}H{random.choice([0, 15, 30, 45])}M",
                        'aircraft': airline_info.get('aircraft', 'Boeing 777')
                    }],
                    'duration': f"PT{duration_hours}H{random.choice([0, 15, 30, 45])}M",
                    'duration_mins': duration_hours * 60 + random.choice([0, 15, 30, 45]),
                    'is_direct': random.choice([True, False]) if duration_hours > 8 else True,
                    'stops': 0 if duration_hours <= 8 else random.choice([0, 1])
                }],
                'numberOfBookableSeats': random.randint(1, 9),
                'validatingAirlineCodes': [airline_info['code']],
                'is_real': False,  # Mark as fallback data
                'data_source': 'AI Generated (Amadeus API unavailable)'
            }
            
            flights.append(flight_data)
        
        print(f"✅ Generated {len(flights)} fallback flights for {origin} → {destination}")
        return flights
    
    def _get_route_airlines(self, origin, destination):
        """
        Get realistic airlines with codes and aircraft for specific routes
        """
        # Enhanced airline data with codes and aircraft
        airline_data = {
            'US-ASIA': [
                {'name': 'Singapore Airlines', 'code': 'SQ', 'aircraft': 'Boeing 787-9'},
                {'name': 'Cathay Pacific', 'code': 'CX', 'aircraft': 'Airbus A350'},
                {'name': 'Emirates', 'code': 'EK', 'aircraft': 'Airbus A380'},
                {'name': 'Japan Airlines', 'code': 'JL', 'aircraft': 'Boeing 777-300'}
            ],
            'ASIA-ASIA': [
                {'name': 'Thai Airways', 'code': 'TG', 'aircraft': 'Boeing 787-8'},
                {'name': 'Singapore Airlines', 'code': 'SQ', 'aircraft': 'Airbus A350'},
                {'name': 'AirAsia', 'code': 'AK', 'aircraft': 'Airbus A320'}
            ],
            'US-EUROPE': [
                {'name': 'Lufthansa', 'code': 'LH', 'aircraft': 'Airbus A340'},
                {'name': 'British Airways', 'code': 'BA', 'aircraft': 'Boeing 777'},
                {'name': 'United Airlines', 'code': 'UA', 'aircraft': 'Boeing 787-9'}
            ],
            'DEFAULT': [
                {'name': 'Emirates', 'code': 'EK', 'aircraft': 'Airbus A380'},
                {'name': 'Singapore Airlines', 'code': 'SQ', 'aircraft': 'Boeing 787-9'},
                {'name': 'Qatar Airways', 'code': 'QR', 'aircraft': 'Airbus A350'}
            ]
        }
        
        # Route classification logic
        us_airports = ['JFK', 'LAX', 'SFO', 'ORD', 'MIA', 'DFW']
        asia_airports = ['BKK', 'NRT', 'ICN', 'SIN', 'DPS', 'HKG']
        europe_airports = ['LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD']
        
        if origin in us_airports and destination in asia_airports:
            return airline_data['US-ASIA']
        elif origin in asia_airports and destination in asia_airports:
            return airline_data['ASIA-ASIA']
        elif origin in us_airports and destination in europe_airports:
            return airline_data['US-EUROPE']
        else:
            return airline_data['DEFAULT']
    
    def _get_route_price_range(self, origin, destination):
        """
        Get realistic price range based on actual route characteristics
        """
        # Route-specific pricing based on real market data
        route_prices = {
            # US to Asia routes
            ('JFK', 'BKK'): (650, 1200),
            ('LAX', 'BKK'): (600, 1100),
            ('SFO', 'NRT'): (500, 900),
            ('JFK', 'NRT'): (550, 1000),
            
            # Asia to Asia routes  
            ('NRT', 'BKK'): (200, 450),
            ('SIN', 'BKK'): (100, 250),
            ('HKG', 'BKK'): (150, 300),
            
            # US to Europe routes
            ('JFK', 'LHR'): (400, 800),
            ('LAX', 'CDG'): (500, 900),
        }
        
        # Check for exact route match
        route_key = (origin, destination)
        if route_key in route_prices:
            return route_prices[route_key]
        
        # Reverse route check
        reverse_key = (destination, origin)
        if reverse_key in route_prices:
            return route_prices[reverse_key]
        
        # Default ranges by distance category
        us_airports = ['JFK', 'LAX', 'SFO', 'ORD', 'MIA', 'DFW']
        asia_airports = ['BKK', 'NRT', 'ICN', 'SIN', 'DPS', 'HKG']
        europe_airports = ['LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD']
        
        if (origin in us_airports and destination in asia_airports) or \
           (origin in asia_airports and destination in us_airports):
            return (600, 1200)  # Long-haul transpacific
        elif (origin in us_airports and destination in europe_airports) or \
             (origin in europe_airports and destination in us_airports):
            return (400, 900)   # Transatlantic
        elif (origin in asia_airports and destination in asia_airports):
            return (150, 400)   # Regional Asia
        else:
            return (300, 800)   # Default international
    
    def _get_route_duration(self, origin, destination):
        """
        Get realistic flight duration in hours for route
        """
        route_durations = {
            ('JFK', 'BKK'): 17, ('LAX', 'BKK'): 15,
            ('NRT', 'BKK'): 6, ('SIN', 'BKK'): 2,
            ('JFK', 'NRT'): 13, ('LAX', 'NRT'): 11,
            ('JFK', 'LHR'): 7, ('LAX', 'CDG'): 11
        }
        
        route_key = (origin, destination)
        if route_key in route_durations:
            return route_durations[route_key]
        
        reverse_key = (destination, origin)
        if reverse_key in route_durations:
            return route_durations[reverse_key]
        
        # Default estimate
        return 8  # Average international flight
    
    def get_airport_code(self, city_name):
        """
        Get IATA airport code for a city
        This is a simple lookup - in production, use Amadeus Airport Search API
        """
        # Extract city name before comma (e.g., "Dubai, UAE" -> "Dubai")
        if ',' in city_name:
            city_name = city_name.split(',')[0].strip()
        
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
        
        code = airport_codes.get(city_name.lower(), 'UNKNOWN')
        if code != 'UNKNOWN':
            print(f"✈️ Mapped '{city_name}' to airport code: {code}")
        return code
