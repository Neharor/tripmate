"""
Amadeus Hotel Search Service
Real-time hotel data using Amadeus API
"""
import os
from amadeus import Client, ResponseError
from datetime import datetime, timedelta

class HotelService:
    """
    Service for searching real hotels using Amadeus Hotel API
    """
    
    def __init__(self):
        self.client = None
        self.is_available = False
        
        # Initialize Amadeus client
        api_key = os.getenv('AMADEUS_API_KEY')
        api_secret = os.getenv('AMADEUS_API_SECRET')
        
        if api_key and api_secret and api_key != 'your_api_key_here':
            try:
                self.client = Client(
                    client_id=api_key,
                    client_secret=api_secret
                )
                self.is_available = True
                print("✅ Amadeus Hotel API connected successfully!")
            except Exception as e:
                print(f"⚠️  Amadeus Hotel API initialization failed: {e}")
                self.is_available = False
        else:
            print("⚠️  Amadeus Hotel API credentials not found. Using AI fallback.")
    
    def search_hotels(self, destination_city, checkin_date=None, checkout_date=None, 
                      budget_per_night=None, adults=1, radius=5):
        """
        Search for hotels in a destination
        
        Args:
            destination_city: City name (e.g., "Bali", "Paris")
            checkin_date: Check-in date (YYYY-MM-DD) or None for flexible
            checkout_date: Check-out date (YYYY-MM-DD) or None for flexible
            budget_per_night: Maximum price per night in USD
            adults: Number of adults
            radius: Search radius in kilometers
            
        Returns:
            List of hotels with real prices and details
        """
        if not self.is_available:
            return None
        
        try:
            # Step 1: Get city location (lat/long)
            city_location = self._get_city_location(destination_city)
            if not city_location:
                print(f"⚠️  Could not find location for {destination_city}")
                return None
            
            latitude = city_location['latitude']
            longitude = city_location['longitude']
            
            # Step 2: Set default dates if not provided
            if not checkin_date:
                checkin_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            if not checkout_date:
                checkout_date = (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
            
            # Step 3: Search for hotel offers
            print(f"🏨 Searching hotels in {destination_city} ({latitude}, {longitude})")
            print(f"   Check-in: {checkin_date}, Check-out: {checkout_date}")
            
            response = self.client.shopping.hotel_offers_search.get(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                radiusUnit='KM',
                checkInDate=checkin_date,
                checkOutDate=checkout_date,
                adults=adults,
                roomQuantity=1,
                currency='USD',
                bestRateOnly=True
            )
            
            # Step 4: Parse and filter results
            hotels = self._parse_hotel_results(response.data, budget_per_night)
            
            print(f"✅ Found {len(hotels)} hotels in {destination_city}")
            return hotels
            
        except ResponseError as error:
            print(f"⚠️  Amadeus Hotel API error: {error}")
            return None
        except Exception as e:
            print(f"⚠️  Hotel search failed: {e}")
            return None
    
    def _get_city_location(self, city_name):
        """
        Get latitude/longitude for a city using Amadeus Location API
        """
        try:
            response = self.client.reference_data.locations.get(
                keyword=city_name,
                subType='CITY'
            )
            
            if response.data and len(response.data) > 0:
                location = response.data[0]
                return {
                    'city': location['address']['cityName'],
                    'country': location['address'].get('countryName', ''),
                    'latitude': location['geoCode']['latitude'],
                    'longitude': location['geoCode']['longitude'],
                    'iata_code': location.get('iataCode', '')
                }
            return None
            
        except Exception as e:
            print(f"⚠️  Could not get location for {city_name}: {e}")
            return None
    
    def _parse_hotel_results(self, data, budget_per_night=None):
        """
        Parse Amadeus hotel API response into clean format
        """
        hotels = []
        
        for offer in data[:10]:  # Limit to top 10 results
            try:
                hotel = offer.get('hotel', {})
                offers_list = offer.get('offers', [])
                
                if not offers_list:
                    continue
                
                # Get best offer (first one, as we requested bestRateOnly)
                best_offer = offers_list[0]
                price_info = best_offer.get('price', {})
                
                # Calculate price per night
                total_price = float(price_info.get('total', 0))
                nights = self._calculate_nights(
                    best_offer.get('checkInDate'),
                    best_offer.get('checkOutDate')
                )
                price_per_night = total_price / nights if nights > 0 else total_price
                
                # Filter by budget
                if budget_per_night and price_per_night > budget_per_night:
                    continue
                
                # Build hotel object
                hotel_obj = {
                    'name': hotel.get('name', 'Unknown Hotel'),
                    'hotel_id': hotel.get('hotelId', ''),
                    'price_per_night': round(price_per_night, 2),
                    'total_price': round(total_price, 2),
                    'currency': price_info.get('currency', 'USD'),
                    'checkin': best_offer.get('checkInDate'),
                    'checkout': best_offer.get('checkOutDate'),
                    'nights': nights,
                    'room_type': best_offer.get('room', {}).get('typeEstimated', {}).get('category', 'Standard'),
                    'rating': hotel.get('rating', 'N/A'),
                    'amenities': hotel.get('amenities', []),
                    'latitude': hotel.get('latitude'),
                    'longitude': hotel.get('longitude'),
                    'address': self._format_address(hotel.get('address', {})),
                    'is_real': True,
                    'data_source': 'amadeus_api'
                }
                
                hotels.append(hotel_obj)
                
            except Exception as e:
                print(f"⚠️  Error parsing hotel: {e}")
                continue
        
        # Sort by price (low to high)
        hotels.sort(key=lambda x: x['price_per_night'])
        
        return hotels
    
    def _calculate_nights(self, checkin, checkout):
        """Calculate number of nights between dates"""
        try:
            checkin_dt = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_dt = datetime.strptime(checkout, '%Y-%m-%d')
            return (checkout_dt - checkin_dt).days
        except:
            return 1
    
    def _format_address(self, address):
        """Format hotel address"""
        parts = []
        if address.get('lines'):
            parts.extend(address['lines'])
        if address.get('cityName'):
            parts.append(address['cityName'])
        if address.get('countryName'):
            parts.append(address['countryName'])
        return ', '.join(parts) if parts else 'Address not available'
    
    def format_hotel_for_display(self, hotel):
        """
        Format hotel data for user-friendly display
        """
        # Determine price category
        price = hotel['price_per_night']
        if price < 50:
            category = "Budget"
            emoji = "🏨"
        elif price < 100:
            category = "Mid-range"
            emoji = "🏨"
        else:
            category = "Luxury"
            emoji = "✨"
        
        # Build display string
        display = f"{emoji} {hotel['name']}\n"
        display += f"   {category} • ${price:.0f}/night"
        
        if hotel.get('rating') and hotel['rating'] != 'N/A':
            display += f" • {hotel['rating']}★"
        
        if hotel.get('address'):
            display += f"\n   📍 {hotel['address']}"
        
        if hotel.get('room_type'):
            display += f"\n   🛏️  {hotel['room_type']} room"
        
        display += f"\n   💰 Total: ${hotel['total_price']:.0f} for {hotel['nights']} nights"
        
        return display


# Global instance
_hotel_service = None

def get_hotel_service():
    """Get or create hotel service instance"""
    global _hotel_service
    if _hotel_service is None:
        _hotel_service = HotelService()
    return _hotel_service
