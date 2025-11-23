"""
Location search routes for autocomplete
Uses Amadeus API to search real destinations
"""
from flask import Blueprint, request, jsonify
import os
from amadeus import Client, ResponseError

locations_bp = Blueprint('locations', __name__)

# Initialize Amadeus client
amadeus_client = None
api_key = os.getenv('AMADEUS_API_KEY')
api_secret = os.getenv('AMADEUS_API_SECRET')

if api_key and api_secret and api_key != 'your_api_key_here':
    try:
        amadeus_client = Client(client_id=api_key, client_secret=api_secret)
        print("✅ Amadeus Location API ready for autocomplete")
    except Exception as e:
        print(f"⚠️  Amadeus Location API initialization failed: {e}")

@locations_bp.route('/api/locations/search', methods=['GET'])
def search_locations():
    """
    Search for destinations using Amadeus Location API
    Query params:
    - q: search query (e.g., "Bali", "Paris", "New York")
    - limit: max results (default: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query or len(query) < 2:
            return jsonify({
                'locations': [],
                'message': 'Query too short (min 2 characters)'
            }), 200
        
        # If Amadeus not available, return empty
        if not amadeus_client:
            return jsonify({
                'locations': [],
                'message': 'Location API not available'
            }), 200
        
        # Search using Amadeus Location API
        response = amadeus_client.reference_data.locations.get(
            keyword=query,
            subType=['CITY', 'AIRPORT'],
            page={'limit': limit}
        )
        
        # Parse results
        locations = []
        seen = set()  # To avoid duplicates
        
        for location in response.data:
            try:
                # Extract city and country
                address = location.get('address', {})
                city_name = address.get('cityName', '')
                country_name = address.get('countryName', '')
                
                if not city_name:
                    continue
                
                # Create unique key
                location_key = f"{city_name}, {country_name}"
                
                # Skip duplicates
                if location_key in seen:
                    continue
                seen.add(location_key)
                
                # Build location object
                location_obj = {
                    'name': city_name,
                    'country': country_name,
                    'display': location_key,
                    'iata_code': location.get('iataCode', ''),
                    'type': location.get('subType', 'CITY'),
                    'latitude': location.get('geoCode', {}).get('latitude'),
                    'longitude': location.get('geoCode', {}).get('longitude')
                }
                
                locations.append(location_obj)
                
            except Exception as e:
                print(f"Error parsing location: {e}")
                continue
        
        return jsonify({
            'locations': locations,
            'count': len(locations),
            'query': query
        }), 200
        
    except ResponseError as error:
        print(f"Amadeus API error: {error}")
        return jsonify({
            'locations': [],
            'error': 'Location search failed',
            'message': str(error)
        }), 500
        
    except Exception as e:
        print(f"Location search error: {e}")
        return jsonify({
            'locations': [],
            'error': 'Internal error',
            'message': str(e)
        }), 500

@locations_bp.route('/api/locations/popular', methods=['GET'])
def get_popular_locations():
    """
    Get popular destinations
    Returns curated list of top destinations
    """
    popular = [
        # Asia
        {'name': 'Bali', 'country': 'Indonesia', 'display': 'Bali, Indonesia'},
        {'name': 'Tokyo', 'country': 'Japan', 'display': 'Tokyo, Japan'},
        {'name': 'Bangkok', 'country': 'Thailand', 'display': 'Bangkok, Thailand'},
        {'name': 'Singapore', 'country': 'Singapore', 'display': 'Singapore'},
        {'name': 'Dubai', 'country': 'UAE', 'display': 'Dubai, UAE'},
        {'name': 'Goa', 'country': 'India', 'display': 'Goa, India'},
        {'name': 'Jaipur', 'country': 'India', 'display': 'Jaipur, India'},
        {'name': 'Mumbai', 'country': 'India', 'display': 'Mumbai, India'},
        
        # Europe
        {'name': 'Paris', 'country': 'France', 'display': 'Paris, France'},
        {'name': 'London', 'country': 'UK', 'display': 'London, UK'},
        {'name': 'Rome', 'country': 'Italy', 'display': 'Rome, Italy'},
        {'name': 'Barcelona', 'country': 'Spain', 'display': 'Barcelona, Spain'},
        {'name': 'Amsterdam', 'country': 'Netherlands', 'display': 'Amsterdam, Netherlands'},
        
        # Americas
        {'name': 'New York', 'country': 'USA', 'display': 'New York, USA'},
        {'name': 'Los Angeles', 'country': 'USA', 'display': 'Los Angeles, USA'},
        {'name': 'Cancun', 'country': 'Mexico', 'display': 'Cancun, Mexico'},
        
        # Africa
        {'name': 'Cape Town', 'country': 'South Africa', 'display': 'Cape Town, South Africa'},
        {'name': 'Marrakech', 'country': 'Morocco', 'display': 'Marrakech, Morocco'},
        
        # Oceania
        {'name': 'Sydney', 'country': 'Australia', 'display': 'Sydney, Australia'},
        {'name': 'Auckland', 'country': 'New Zealand', 'display': 'Auckland, New Zealand'}
    ]
    
    return jsonify({
        'locations': popular,
        'count': len(popular)
    }), 200
