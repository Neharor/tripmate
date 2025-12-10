"""
Curated restaurant database for different cities, cuisines, and dietary preferences.
This serves as a fallback when Google Places API is not available.
"""

RESTAURANTS = {
    'Singapore': {
        'Indian': {
            'Vegan': [
                {
                    'name': 'Saravanaa Bhavan',
                    'address': '58 Serangoon Rd, Singapore',
                    'rating': 4.4,
                    'specialty': 'South Indian vegetarian cuisine',
                    'price': '$$',
                    'highlights': 'Masala dosa, vegan thali, idli'
                },
                {
                    'name': 'MTR 1924',
                    'address': 'Little India Arcade',
                    'rating': 4.3,
                    'specialty': 'Authentic South Indian vegan options',
                    'price': '$$',
                    'highlights': 'Vegan biryani, sambhar, coconut chutney'
                },
                {
                    'name': 'Komala Vilas',
                    'address': '76-78 Serangoon Road',
                    'rating': 4.2,
                    'specialty': 'Traditional Indian vegetarian',
                    'price': '$',
                    'highlights': 'Masala thosai, veg biryani, chai'
                },
                {
                    'name': 'Ananda Bhavan',
                    'address': 'Tekka Centre',
                    'rating': 4.1,
                    'specialty': 'North & South Indian vegan-friendly',
                    'price': '$',
                    'highlights': 'Pani puri, chaat, vegan sweets'
                }
            ],
            'Vegetarian': [
                {
                    'name': 'Saravanaa Bhavan',
                    'address': '58 Serangoon Rd, Singapore',
                    'rating': 4.4,
                    'specialty': 'South Indian vegetarian cuisine',
                    'price': '$$',
                    'highlights': 'Paneer dishes, masala dosa, lassi'
                },
                {
                    'name': 'The Banana Leaf Apolo',
                    'address': 'Little India',
                    'rating': 4.3,
                    'specialty': 'Vegetarian Indian thali',
                    'price': '$$',
                    'highlights': 'Banana leaf rice, vegetable curry'
                }
            ],
            'None': [
                {
                    'name': 'The Song of India',
                    'address': 'Scotts Road',
                    'rating': 4.6,
                    'specialty': 'Fine dining Indian',
                    'price': '$$$',
                    'highlights': 'Tandoori, curry selection, elegant ambiance'
                },
                {
                    'name': 'Muthu\'s Curry',
                    'address': 'Little India',
                    'rating': 4.4,
                    'specialty': 'Traditional fish head curry',
                    'price': '$$',
                    'highlights': 'Fish head curry, biryani, seafood'
                }
            ]
        },
        'Chinese': {
            'Vegan': [
                {
                    'name': 'Lingzhi Vegetarian',
                    'address': 'Liat Towers',
                    'rating': 4.5,
                    'specialty': 'Chinese vegetarian fine dining',
                    'price': '$$$',
                    'highlights': 'Mock meat dishes, organic ingredients'
                }
            ]
        },
        'Thai': {
            'Vegan': [
                {
                    'name': 'Thai Tantric',
                    'address': 'Harding Road',
                    'rating': 4.3,
                    'specialty': 'Thai with vegan options',
                    'price': '$$',
                    'highlights': 'Tom yum, pad thai, green curry'
                }
            ]
        },
        'Local': {
            'Vegan': [
                {
                    'name': 'Original Sin',
                    'address': 'Jalan Merah Saga',
                    'rating': 4.4,
                    'specialty': 'Mediterranean vegetarian',
                    'price': '$$',
                    'highlights': 'Pizzas, pastas, organic wine'
                }
            ],
            'Halal': [
                {
                    'name': 'Hjh Maimunah Restaurant',
                    'address': 'Jalan Pisang',
                    'rating': 4.5,
                    'specialty': 'Malay nasi padang',
                    'price': '$',
                    'highlights': 'Rendang, sambal, traditional dishes'
                }
            ]
        }
    },
    
    'Bangkok': {
        'Thai': {
            'Vegan': [
                {
                    'name': 'Broccoli Revolution',
                    'address': 'Sukhumvit Soi 49',
                    'rating': 4.6,
                    'specialty': 'Plant-based Thai fusion',
                    'price': '$$',
                    'highlights': 'Vegan pad thai, tom yum, smoothie bowls'
                },
                {
                    'name': 'May Veggie Home',
                    'address': 'Phra Nakhon',
                    'rating': 4.5,
                    'specialty': 'Traditional Thai vegan',
                    'price': '$',
                    'highlights': 'Green curry, stir-fries, rice dishes'
                }
            ]
        }
    },
    
    'Tokyo': {
        'Japanese': {
            'Vegan': [
                {
                    'name': 'Ain Soph Journey',
                    'address': 'Shinjuku',
                    'rating': 4.7,
                    'specialty': 'Vegan Japanese comfort food',
                    'price': '$$',
                    'highlights': 'Vegan ramen, katsu curry, pancakes'
                },
                {
                    'name': 'T\'s TanTan',
                    'address': 'Tokyo Station',
                    'rating': 4.5,
                    'specialty': 'Vegan ramen',
                    'price': '$',
                    'highlights': 'Tan tan men, sesame ramen'
                }
            ]
        }
    },
    
    'Paris': {
        'French': {
            'Vegan': [
                {
                    'name': 'Gentle Gourmet',
                    'address': 'Le Marais',
                    'rating': 4.6,
                    'specialty': 'Vegan French bistro',
                    'price': '$$$',
                    'highlights': 'Plant-based bourguignon, crème brûlée'
                }
            ]
        }
    }
}


def get_restaurants(city, cuisine=None, dietary=None, limit=4):
    """
    Get restaurant recommendations based on city, cuisine, and dietary preferences.
    
    Args:
        city: City name (e.g., 'Singapore')
        cuisine: Cuisine type (e.g., 'Indian', 'Chinese', 'Thai', 'Local')
        dietary: Dietary preference (e.g., 'Vegan', 'Vegetarian', 'Halal', 'None')
        limit: Maximum number of restaurants to return
    
    Returns:
        List of restaurant dictionaries
    """
    city_data = RESTAURANTS.get(city, {})
    
    if not city_data:
        return []
    
    # If cuisine specified, filter by cuisine
    if cuisine and cuisine in city_data:
        cuisine_data = city_data[cuisine]
        
        # If dietary preference specified, filter by that
        if dietary and dietary in cuisine_data:
            return cuisine_data[dietary][:limit]
        
        # Otherwise, return all restaurants for that cuisine
        all_restaurants = []
        for diet_category in cuisine_data.values():
            all_restaurants.extend(diet_category)
        return all_restaurants[:limit]
    
    # No specific cuisine - search all cuisines for dietary match
    if dietary:
        matching = []
        for cuisine_name, cuisine_data in city_data.items():
            if dietary in cuisine_data:
                matching.extend(cuisine_data[dietary])
        return matching[:limit]
    
    # Return any restaurants from the city
    all_restaurants = []
    for cuisine_data in city_data.values():
        for diet_category in cuisine_data.values():
            all_restaurants.extend(diet_category)
    return all_restaurants[:limit]


def format_restaurant_for_itinerary(restaurant):
    """Format a restaurant dict as a markdown string for the itinerary."""
    return (
        f"**{restaurant['name']}** ({restaurant['rating']}⭐) - "
        f"{restaurant['specialty']}. "
        f"Try: {restaurant['highlights']}"
    )


# Test function
if __name__ == "__main__":
    print("Testing Singapore Indian Vegan restaurants:")
    restaurants = get_restaurants('Singapore', 'Indian', 'Vegan')
    for i, r in enumerate(restaurants, 1):
        print(f"{i}. {format_restaurant_for_itinerary(r)}")
