"""
Google Places API service for fetching real places, attractions, and restaurant data
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GooglePlacesService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = 'https://maps.googleapis.com/maps/api/place'
    
    def search_attractions(self, city, interest=None, limit=10):
        """
        Search for tourist attractions and activities using Google Places API
        
        Args:
            city: City name (e.g., 'Singapore')
            interest: Interest type (e.g., 'Shopping', 'Nature', 'History', 'Culture')
            limit: Maximum number of results
        
        Returns:
            List of attraction dictionaries
        """
        # Map interests to Google Places types and keywords
        interest_mapping = {
            'Shopping': 'shopping mall market boutique',
            'Nature': 'park garden nature reserve',
            'History': 'museum historical site monument',
            'Culture': 'temple art gallery cultural center',
            'Adventure': 'adventure sports activity park',
            'Food': 'food market street food tour',
            'Beach': 'beach waterfront seaside',
            'Nightlife': 'bar nightclub entertainment',
            'Relaxation': 'spa wellness massage',
            'Photography': 'viewpoint scenic landmark'
        }
        
        # Build search query
        if interest and interest in interest_mapping:
            query = f"{interest_mapping[interest]} in {city}"
        else:
            query = f"tourist attractions in {city}"
        
        print(f"🔍 Google Places attractions search: '{query}'")
        
        # Call Text Search API
        url = f'{self.base_url}/textsearch/json'
        params = {
            'query': query,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                print(f"❌ Google Places API error: {response.status_code}")
                return []
            
            data = response.json()
            
            if data.get('status') != 'OK':
                print(f"❌ Google Places status: {data.get('status')}")
                return []
            
            results = data.get('results', [])[:limit]
            print(f"✅ Found {len(results)} attractions from Google Places")
            
            # Format results
            attractions = []
            for place in results:
                attraction = {
                    'name': place.get('name', 'Unknown'),
                    'address': place.get('formatted_address', 'N/A'),
                    'rating': place.get('rating', 0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'types': place.get('types', []),
                    'place_id': place.get('place_id', '')
                }
                
                # Generate description from types
                types = [t.replace('_', ' ').title() for t in place.get('types', [])]
                attraction['description'] = ', '.join(types[:2]) if types else 'Attraction'
                
                attractions.append(attraction)
            
            return attractions
            
        except Exception as e:
            print(f"❌ Google Places attractions error: {e}")
            return []
    
    def search_restaurants(self, city, cuisine=None, dietary=None, limit=5):
        """
        Search for restaurants using Google Places API
        
        Args:
            city: City name (e.g., 'Singapore')
            cuisine: Cuisine type (e.g., 'Indian', 'Chinese', 'Thai')
            dietary: Dietary preference (e.g., 'Vegan', 'Vegetarian', 'Halal')
            limit: Maximum number of results
        
        Returns:
            List of restaurant dictionaries
        """
        # Build search query
        query_parts = []
        
        if dietary:
            # Handle both list and string
            if isinstance(dietary, list):
                query_parts.extend([d.lower() for d in dietary])
            else:
                query_parts.append(dietary.lower())
        
        if cuisine:
            query_parts.append(cuisine.lower())
        
        query_parts.extend(['restaurant', 'in', city])
        query = ' '.join(query_parts)
        
        print(f"🔍 Google Places search: '{query}'")
        
        # Call Text Search API
        url = f'{self.base_url}/textsearch/json'
        params = {
            'query': query,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                print(f"❌ Google Places API error: {response.status_code}")
                return []
            
            data = response.json()
            
            if data.get('status') != 'OK':
                print(f"❌ Google Places status: {data.get('status')}")
                print(f"   Message: {data.get('error_message', 'No message')}")
                return []
            
            results = data.get('results', [])[:limit]
            print(f"✅ Found {len(results)} restaurants from Google Places")
            
            # Format results
            restaurants = []
            for place in results:
                restaurant = {
                    'name': place.get('name', 'Unknown'),
                    'address': place.get('formatted_address', 'N/A'),
                    'rating': place.get('rating', 0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'price_level': place.get('price_level', 2),  # 1-4 scale
                    'types': place.get('types', []),
                    'place_id': place.get('place_id', '')
                }
                
                # Generate specialty from types
                types = [t.replace('_', ' ').title() for t in place.get('types', []) if 'restaurant' not in t.lower()]
                restaurant['specialty'] = ', '.join(types[:2]) if types else 'Restaurant'
                
                # Generate highlights (placeholder - could enhance with details API)
                if cuisine:
                    restaurant['highlights'] = f"{cuisine} cuisine specialties"
                else:
                    restaurant['highlights'] = "Local favorites"
                
                # Price indicator
                price_level = restaurant['price_level']
                restaurant['price'] = '$' * max(1, min(price_level, 4))
                
                restaurants.append(restaurant)
            
            return restaurants
            
        except Exception as e:
            print(f"❌ Google Places error: {e}")
            return []
    
    def get_place_details(self, place_id):
        """
        Get detailed information about a specific place
        
        Args:
            place_id: Google Places ID
        
        Returns:
            Dictionary with place details
        """
        url = f'{self.base_url}/details/json'
        params = {
            'place_id': place_id,
            'fields': 'name,rating,formatted_phone_number,opening_hours,website,price_level,reviews',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    return data.get('result', {})
            
            return {}
            
        except Exception as e:
            print(f"❌ Place details error: {e}")
            return {}


def format_restaurant_for_itinerary(restaurant):
    """Format a restaurant dict as a markdown string for the itinerary with Google Maps link and hover tooltip."""
    rating_text = f"{restaurant['rating']}⭐" if restaurant.get('rating') else "N/A"
    reviews_text = f"({restaurant.get('user_ratings_total', 0)} reviews)" if restaurant.get('user_ratings_total') else ""
    
    # Create Google Maps link from place_id
    place_id = restaurant.get('place_id', '')
    name = restaurant['name']
    address = restaurant.get('address', 'N/A')
    
    if place_id:
        # Make the name a clickable link with title attribute for hover tooltip
        name_link = f'<a href="https://www.google.com/maps/place/?q=place_id:{place_id}" target="_blank" title="{address}">{name}</a>'
    else:
        name_link = f"**{name}**"
    
    return (
        f"{name_link} {rating_text} {reviews_text} - "
        f"{restaurant.get('specialty', 'Restaurant')}. "
        f"Try: {restaurant.get('highlights', 'Local specialties')}"
    )


def format_attraction_for_itinerary(attraction):
    """Format an attraction dict as a markdown string for the itinerary with Google Maps link and hover tooltip."""
    rating_text = f"{attraction['rating']}⭐" if attraction.get('rating') else ""
    reviews_text = f"({attraction.get('user_ratings_total', 0)} reviews)" if attraction.get('user_ratings_total') else ""
    
    # Create Google Maps link from place_id
    place_id = attraction.get('place_id', '')
    name = attraction['name']
    address = attraction.get('address', 'N/A')
    description = attraction.get('description', '')
    
    # Create hover text with address and description
    hover_text = f"{address}"
    if description:
        hover_text = f"{description} | {address}"
    
    if place_id:
        # Make the name a clickable link with title attribute for hover tooltip
        name_link = f'<a href="https://www.google.com/maps/place/?q=place_id:{place_id}" target="_blank" title="{hover_text}">{name}</a>'
    else:
        name_link = f"**{name}**"
    
    if rating_text and reviews_text:
        return f"{name_link} {rating_text} {reviews_text}"
    else:
        return f"{name_link}"


# Test function
if __name__ == "__main__":
    service = GooglePlacesService()
    
    print("\n🧪 Testing Google Places API:")
    print("=" * 60)
    
    # Test restaurants
    print("\n🍽️  RESTAURANTS:")
    restaurants = service.search_restaurants('Singapore', cuisine='Indian', dietary='Vegan', limit=4)
    
    for i, r in enumerate(restaurants, 1):
        print(f"\n{i}. {format_restaurant_for_itinerary(r)}")
        print(f"   📍 {r['address']}")
        print(f"   💰 {r['price']}")
    
    # Test attractions
    print("\n\n🎯 ATTRACTIONS:")
    attractions = service.search_attractions('Singapore', interest='Shopping', limit=5)
    
    for i, a in enumerate(attractions, 1):
        print(f"\n{i}. {format_attraction_for_itinerary(a)}")
        print(f"   📍 {a['address']}")

