"""
Activities & Tours Service
Fetches real activities and bookable experiences from APIs and Kaggle data
"""
import requests
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add ml directory to path
sys.path.append(str(Path(__file__).parent.parent / 'ml'))
from kaggle_activities import get_activity_recommender

class ActivitiesService:
    """
    Service for searching real activities and tours
    Priority: Kaggle Data-Driven Recommendations → APIs → Curated Database
    """
    
    def __init__(self):
        # Initialize Kaggle activity recommender (FREE, data-driven)
        try:
            self.kaggle_recommender = get_activity_recommender()
            print("✅ Kaggle Activity Recommender loaded (Data-driven, FREE)")
        except Exception as e:
            print(f"⚠️  Kaggle recommender error: {e}")
            self.kaggle_recommender = None
        
        # API keys (optional)
        self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
        self.getyourguide_api_key = os.getenv('GETYOURGUIDE_API_KEY', '')
        self.viator_api_key = os.getenv('VIATOR_API_KEY', '')
        
        # Curated activities database as final fallback
        self.activities_db = self._load_activities_db()
        
        if self.google_places_api_key:
            print("✅ Google Places API configured (FREE tier)")
        elif self.getyourguide_api_key:
            print("✅ GetYourGuide API configured")
        elif self.viator_api_key:
            print("✅ Viator API configured")
    
    def _load_activities_db(self) -> Dict:
        """Load curated activities database"""
        return {
            'Bangkok': [
                {
                    'name': 'Bangkok Street Food Tour by Tasty Bangkok',
                    'description': '3-hour guided tour of 10+ street food stalls, learn recipes',
                    'reason': 'Authentic flavors, skip lines, and expert guide',
                    'price_range': '$35-40',
                    'price_min': 35,
                    'duration': '3 hours',
                    'category': 'food',
                    'rating': 4.7,
                    'reviews': 1240
                },
                {
                    'name': 'Grand Palace and Wat Phra Kaew Tour by GetYourGuide',
                    'description': 'Skip-the-line entry to iconic palace and temple complex',
                    'reason': 'Unbeatable views, rich history, and expert guide',
                    'price_range': '$25-35',
                    'price_min': 25,
                    'duration': '4 hours',
                    'category': 'culture',
                    'rating': 4.8,
                    'reviews': 2150
                },
                {
                    'name': 'Bangkok Canal Boat Tour by Chao Phraya Princess',
                    'description': '1-hour boat ride along Chao Phraya River, see city sights',
                    'reason': 'Unique perspective, relaxing ride, and onboard amenities',
                    'price_range': '$20-30',
                    'price_min': 20,
                    'duration': '1 hour',
                    'category': 'sightseeing',
                    'rating': 4.5,
                    'reviews': 890
                },
                {
                    'name': 'Muay Thai Boxing at Rajadamnern Stadium',
                    'description': 'Live boxing match, VIP seats, and behind-the-scenes tour',
                    'reason': 'Authentic experience, thrilling action, and local culture',
                    'price_range': '$30-40',
                    'price_min': 30,
                    'duration': '2.5 hours',
                    'category': 'sports',
                    'rating': 4.6,
                    'reviews': 1450
                },
                {
                    'name': 'Jim Thompson House and Museum Tour',
                    'description': 'Guided tour of traditional Thai architecture and art',
                    'reason': 'Rich history, stunning gardens, and expert guide',
                    'price_range': '$15-25',
                    'price_min': 15,
                    'duration': '2 hours',
                    'category': 'culture',
                    'rating': 4.4,
                    'reviews': 620
                }
            ],
            'Bali': [
                {
                    'name': 'Ubud Rice Terraces and Monkey Forest Tour',
                    'description': 'Scenic hike through green rice paddies and sacred monkey forest',
                    'reason': 'Iconic Bali scenery, wildlife encounters, and local guide',
                    'price_range': '$30-45',
                    'price_min': 30,
                    'duration': '5 hours',
                    'category': 'nature',
                    'rating': 4.6,
                    'reviews': 1890
                },
                {
                    'name': 'Balinese Cooking Class at Paon Bali',
                    'description': 'Market visit + hands-on cooking lesson + recipes to take home',
                    'reason': 'Learn authentic cuisine, explore local market, cooking skills',
                    'price_range': '$40-55',
                    'price_min': 40,
                    'duration': '4 hours',
                    'category': 'food',
                    'rating': 4.8,
                    'reviews': 1420
                },
                {
                    'name': 'Mount Batur Sunrise Hike',
                    'description': '4 AM start, trek to summit for sunrise, includes breakfast',
                    'reason': 'Epic volcano views, unforgettable sunrise, adventure experience',
                    'price_range': '$35-50',
                    'price_min': 35,
                    'duration': '5 hours',
                    'category': 'adventure',
                    'rating': 4.7,
                    'reviews': 2100
                },
                {
                    'name': 'Tanah Lot Temple Sunset Tour',
                    'description': 'Skip-the-line access, guided tour, best sunset viewing spot',
                    'reason': 'Iconic sea temple, spectacular sunset, cultural significance',
                    'price_range': '$25-35',
                    'price_min': 25,
                    'duration': '3 hours',
                    'category': 'culture',
                    'rating': 4.7,
                    'reviews': 1680
                },
                {
                    'name': 'Scuba Diving or Snorkeling at Coral Gardens',
                    'description': 'Boat trip to coral reefs, equipment included, marine life viewing',
                    'reason': 'Vibrant marine ecosystem, professional guides, underwater adventure',
                    'price_range': '$45-65',
                    'price_min': 45,
                    'duration': '4 hours',
                    'category': 'water',
                    'rating': 4.6,
                    'reviews': 1540
                }
            ],
            'Paris': [
                # History Activities
                {
                    'name': 'Louvre Museum Skip-the-Line Guided Tour',
                    'description': 'Fast-track entry, expert guide, Mona Lisa and highlights tour',
                    'reason': 'Avoid 2-hour queues, expert commentary, world-class art',
                    'price_range': '$55-75',
                    'price_min': 55,
                    'duration': '3 hours',
                    'category': 'history',
                    'rating': 4.8,
                    'reviews': 3200
                },
                {
                    'name': 'Palace of Versailles Day Trip',
                    'description': 'Royal palace tour, Hall of Mirrors, magnificent gardens',
                    'reason': 'French royal history, opulent architecture, beautiful gardens',
                    'price_range': '$65-85',
                    'price_min': 65,
                    'duration': '6 hours',
                    'category': 'history',
                    'rating': 4.7,
                    'reviews': 5420
                },
                {
                    'name': 'Arc de Triomphe and Champs-Élysées Tour',
                    'description': 'Historic monument, climb to top, famous avenue walk',
                    'reason': 'Napoleon history, panoramic views, iconic Parisian boulevard',
                    'price_range': '$25-35',
                    'price_min': 25,
                    'duration': '2 hours',
                    'category': 'history',
                    'rating': 4.5,
                    'reviews': 2100
                },
                
                # Nature Activities  
                {
                    'name': 'Luxembourg Gardens Walking Tour',
                    'description': 'Beautiful palace park, tree-lined paths, peaceful gardens',
                    'reason': 'Peaceful nature escape, French garden design, perfect for couples',
                    'price_range': '$20-30',
                    'price_min': 20,
                    'duration': '2 hours',
                    'category': 'nature',
                    'rating': 4.5,
                    'reviews': 1800
                },
                {
                    'name': 'Seine River Walk and Tuileries Garden',
                    'description': 'Riverside stroll, historic garden, outdoor sculptures',
                    'reason': 'Scenic waterways, nature in city center, romantic walks',
                    'price_range': '$15-25',
                    'price_min': 15,
                    'duration': '2.5 hours',
                    'category': 'nature',
                    'rating': 4.4,
                    'reviews': 1200
                },
                {
                    'name': 'Bois de Vincennes Park and Castle',
                    'description': 'Large park, medieval castle, lakes and forests',
                    'reason': 'Escape city crowds, nature walks, historical castle',
                    'price_range': '$20-30',
                    'price_min': 20,
                    'duration': '3 hours',
                    'category': 'nature',
                    'rating': 4.3,
                    'reviews': 900
                },
                
                # Culture & Sightseeing
                {
                    'name': 'Eiffel Tower Summit Tour',
                    'description': 'Summit access, elevator included, panoramic city views',
                    'reason': 'Iconic Paris symbol, breathtaking views, must-see landmark',
                    'price_range': '$35-55',
                    'price_min': 35,
                    'duration': '2 hours',
                    'category': 'sightseeing',
                    'rating': 4.9,
                    'reviews': 12400
                },
                {
                    'name': 'Montmartre Walking Tour and Sacré-Cœur',
                    'description': 'Explore charming neighborhood, visit basilica, artist square',
                    'reason': 'Historic district, artistic vibe, stunning city views',
                    'price_range': '$25-40',
                    'price_min': 25,
                    'duration': '2.5 hours',
                    'category': 'culture',
                    'rating': 4.5,
                    'reviews': 1240
                },
                
                # Nightlife Activities (Evening Only)
                {
                    'name': 'Seine Evening Dinner Cruise',
                    'description': '3-course dinner cruise with live music and city lights',
                    'reason': 'Perfect for couples, romantic evening, illuminated monuments',
                    'price_range': '$85-120',
                    'price_min': 85,
                    'duration': '2.5 hours',
                    'category': 'nightlife',
                    'rating': 4.6,
                    'reviews': 1950,
                    'time_preference': 'evening'
                },
                {
                    'name': 'Latin Quarter Jazz Club Evening',
                    'description': 'Authentic Parisian jazz club, live music, wine bar',
                    'reason': 'Classic Paris nightlife, intimate atmosphere, quality music',
                    'price_range': '$40-60',
                    'price_min': 40,
                    'duration': '3 hours',
                    'category': 'nightlife',
                    'rating': 4.4,
                    'reviews': 850,
                    'time_preference': 'evening'
                },
                
                # Food Activities (Vegan-Friendly)
                {
                    'name': 'Vegan Food Tour of Le Marais',
                    'description': 'Plant-based restaurants, local vegan specialties, market visit',
                    'reason': 'Perfect for vegans, authentic local cuisine, diverse options',
                    'price_range': '$75-95',
                    'price_min': 75,
                    'duration': '3.5 hours',
                    'category': 'food',
                    'rating': 4.6,
                    'reviews': 1200
                }
            ],
            'Tokyo': [
                {
                    'name': 'Senso-ji Temple and Asakusa Walking Tour',
                    'description': 'Historic temple, street food market, rickshaw ride',
                    'reason': 'Traditional Tokyo culture, iconic temple, local flavors',
                    'price_range': '$30-50',
                    'price_min': 30,
                    'duration': '3 hours',
                    'category': 'culture',
                    'rating': 4.7,
                    'reviews': 1650
                },
                {
                    'name': 'Sumo Wrestling Experience and Tournament',
                    'description': 'Watch professional sumo match, meet wrestlers, understand tradition',
                    'reason': 'Unique Japanese experience, impressive athletes, cultural insight',
                    'price_range': '$40-70',
                    'price_min': 40,
                    'duration': '3 hours',
                    'category': 'sports',
                    'rating': 4.8,
                    'reviews': 1200
                },
                {
                    'name': 'Tokyo Shibuya Crossing and Nightlife Tour',
                    'description': 'Busiest intersection, Karaoke bar, izakaya dinner',
                    'reason': 'Vibrant nightlife, authentic dining, electric energy',
                    'price_range': '$50-75',
                    'price_min': 50,
                    'duration': '4 hours',
                    'category': 'nightlife',
                    'rating': 4.6,
                    'reviews': 1420
                },
                {
                    'name': 'Japanese Tea Ceremony and Zen Garden Experience',
                    'description': 'Traditional ceremony, matcha preparation, garden meditation',
                    'reason': 'Authentic Japanese tradition, peaceful experience, cultural depth',
                    'price_range': '$35-55',
                    'price_min': 35,
                    'duration': '2 hours',
                    'category': 'culture',
                    'rating': 4.9,
                    'reviews': 890
                },
                {
                    'name': 'Robot Restaurant and Akihabara Tech District',
                    'description': 'High-energy robot show, visit tech stores, arcade games',
                    'reason': 'Futuristic entertainment, unique Tokyo experience, tech culture',
                    'price_range': '$45-65',
                    'price_min': 45,
                    'duration': '3 hours',
                    'category': 'entertainment',
                    'rating': 4.5,
                    'reviews': 1100
                }
            ]
    }
    
    def search_activities(self, destination: str, interests: List[str] = None, budget: str = None, companions: str = None, dietary_preferences: List[str] = None, limit: int = 5) -> List[Dict]:
        """
        Search for activities at a destination with user preferences
        
        Args:
            destination: City/country name (e.g., "Bangkok", "Bali")
            interests: List of interest keywords
            budget: Budget range
            companions: Travel companion type (solo, couple, family_kids, friends, business)
            dietary_preferences: List of dietary restrictions (vegetarian, vegan, etc.)
            limit: Max number of activities to return
            
        Returns:
            List of activity dictionaries personalized for user preferences
        """
        try:
            print(f"🔍 Searching personalized activities: destination={destination}, companions={companions}, dietary={dietary_preferences}")
            
            # Priority 1: Kaggle data-driven recommendations (FREE, personalized)
            if self.kaggle_recommender:
                activities = self._search_kaggle_patterns(destination, interests, budget, limit)
                if activities:
                    # Apply personalization filters based on companions and dietary preferences
                    activities = self._personalize_activities(activities, companions, dietary_preferences)
                    print(f"✅ Using personalized Kaggle activities ({len(activities)} found)")
                    return activities
            
            # Priority 2: Google Places API (FREE tier)
            if self.google_places_api_key:
                activities = self._search_google_places(destination, interests, budget, limit)
                if activities:
                    activities = self._personalize_activities(activities, companions, dietary_preferences)
                    return activities
            
            # Priority 3: Other paid APIs
            if self.getyourguide_api_key:
                activities = self._search_getyourguide(destination, interests, budget, limit)
                if activities:
                    activities = self._personalize_activities(activities, companions, dietary_preferences)
                    return activities
            
            if self.viator_api_key:
                activities = self._search_viator(destination, interests, budget, limit)
                if activities:
                    return activities
            
            # Fallback: Curated database
            activities = self._search_database(destination, interests, budget, limit)
            return self._personalize_activities(activities, companions, dietary_preferences)
            
        except Exception as e:
            print(f"Activities search error: {str(e)}")
            activities = self._search_database(destination, interests, budget, limit)
            return self._personalize_activities(activities, companions, dietary_preferences)
    
    def _search_kaggle_patterns(self, destination: str, interests: List[str] = None, budget: str = None, limit: int = 5) -> List[Dict]:
        """Search using Kaggle travel data patterns (FREE, data-driven)"""
        try:
            if not self.kaggle_recommender:
                return []
            
            # Get data-driven recommendations
            activities = self.kaggle_recommender.recommend_activities(
                destination=destination,
                interests=interests or ['culture', 'food'],
                budget=budget,
                limit=limit
            )
            
            return activities
            
        except Exception as e:
            print(f"Kaggle recommender error: {str(e)}")
            return []
    
    def _search_google_places(self, destination: str, interests: List[str] = None, budget: str = None, limit: int = 5) -> List[Dict]:
        """Search using Google Places API (FREE tier - 28,000 requests/month)"""
        try:
            # Map interests to Google Places types
            interest_to_type = {
                'food': 'restaurant',
                'culture': 'museum|art_gallery|place_of_worship',
                'adventure': 'amusement_park|tourist_attraction',
                'shopping': 'shopping_mall|store',
                'nature': 'park|natural_feature',
                'nightlife': 'night_club|bar',
                'history': 'museum|historic_site',
                'beach': 'beach|resort',
                'wildlife': 'zoo|aquarium',
                'spirituality': 'place_of_worship|temple'
            }
            
            # Determine search type based on interests
            search_type = 'tourist_attraction'  # default
            if interests:
                for interest in interests:
                    if interest.lower() in interest_to_type:
                        search_type = interest_to_type[interest.lower()]
                        break
            
            # Text search for activities
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f'{destination} {" ".join(interests) if interests else "attractions things to do"}',
                'type': search_type,
                'key': self.google_places_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    places = data.get('results', [])[:limit]
                    return self._format_google_places_response(places)
            
            return []
        except Exception as e:
            print(f"Google Places API error: {str(e)}")
            return []
    
    def _format_google_places_response(self, places: List[Dict]) -> List[Dict]:
        """Format Google Places API response to match our activity structure"""
        activities = []
        for place in places:
            # Estimate price based on price_level (0-4 scale)
            price_level = place.get('price_level', 2)
            price_ranges = {
                0: ('Free', 0),
                1: ('$10-20', 10),
                2: ('$20-40', 20),
                3: ('$40-80', 40),
                4: ('$80+', 80)
            }
            price_range, price_min = price_ranges.get(price_level, ('$20-40', 20))
            
            # Determine category from types
            types = place.get('types', [])
            category = 'sightseeing'  # default
            if 'restaurant' in types or 'food' in types:
                category = 'food'
            elif 'museum' in types or 'art_gallery' in types:
                category = 'culture'
            elif 'park' in types or 'natural_feature' in types:
                category = 'nature'
            elif 'shopping_mall' in types:
                category = 'shopping'
            elif 'night_club' in types or 'bar' in types:
                category = 'nightlife'
            
            activity = {
                'name': place.get('name', 'Unknown Activity'),
                'description': place.get('formatted_address', 'Explore this popular destination'),
                'reason': f"Highly rated ({place.get('rating', 4.0)}/5) with {place.get('user_ratings_total', 0)} reviews",
                'price_range': price_range,
                'price_min': price_min,
                'duration': '2-3 hours',  # Default estimate
                'category': category,
                'rating': place.get('rating', 4.0),
                'reviews': place.get('user_ratings_total', 0),
                'location': place.get('formatted_address', ''),
                'is_open_now': place.get('opening_hours', {}).get('open_now', None)
            }
            activities.append(activity)
        
        return activities
    
    def _search_getyourguide(self, destination: str, interests: List[str] = None, budget: str = None, limit: int = 5) -> List[Dict]:
        """Search using GetYourGuide API"""
        try:
            url = "https://api.getyourguide.com/v1/tours"
            params = {
                'location': destination,
                'limit': limit,
                'api_key': self.getyourguide_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                tours = response.json().get('tours', [])
                return self._format_api_response(tours)
            
            return []
        except Exception as e:
            print(f"GetYourGuide API error: {str(e)}")
            return []
    
    def _search_viator(self, destination: str, interests: List[str] = None, budget: str = None, limit: int = 5) -> List[Dict]:
        """Search using Viator API"""
        try:
            url = "https://api.viator.com/partner/search/tours"
            params = {
                'query': destination,
                'limit': limit,
                'api_key': self.viator_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                tours = response.json().get('tours', [])
                return self._format_api_response(tours)
            
            return []
        except Exception as e:
            print(f"Viator API error: {str(e)}")
            return []
    
    def _search_database(self, destination: str, interests: List[str] = None, budget: str = None, limit: int = 5) -> List[Dict]:
        """Search curated activities database"""
        try:
            # Normalize destination name
            destination_key = None
            for key in self.activities_db.keys():
                if destination.lower() in key.lower() or key.lower() in destination.lower():
                    destination_key = key
                    break
            
            if not destination_key or destination_key not in self.activities_db:
                # Return generic popular activities
                all_activities = []
                for activities in self.activities_db.values():
                    all_activities.extend(activities)
                return all_activities[:limit]
            
            activities = self.activities_db[destination_key]
            
            # Ensure activity diversity across ALL user interests
            if interests:
                interests_lower = [i.lower() for i in interests]
                
                # Separate activities by category
                matched_by_interest = {}
                other_activities = []
                
                for activity in activities:
                    activity_category = activity.get('category', '').lower()
                    matched = False
                    
                    for interest in interests_lower:
                        if interest in activity_category or activity_category == interest:
                            if interest not in matched_by_interest:
                                matched_by_interest[interest] = []
                            matched_by_interest[interest].append(activity)
                            matched = True
                            break
                    
                    if not matched:
                        other_activities.append(activity)
                
                # Build balanced result: try to include activities for EACH interest
                balanced_activities = []
                activities_per_interest = max(1, limit // max(len(interests_lower), 1))
                
                # Add activities for each user interest
                for interest in interests_lower:
                    if interest in matched_by_interest:
                        balanced_activities.extend(matched_by_interest[interest][:activities_per_interest])
                
                # Fill remaining slots with diverse activities
                remaining_slots = limit - len(balanced_activities)
                if remaining_slots > 0:
                    # Add remaining matched activities first
                    remaining_matched = []
                    for interest_activities in matched_by_interest.values():
                        remaining_matched.extend(interest_activities[activities_per_interest:])
                    
                    balanced_activities.extend(remaining_matched[:remaining_slots // 2])
                    balanced_activities.extend(other_activities[:remaining_slots - len(remaining_matched[:remaining_slots // 2])])
                
                activities = balanced_activities[:limit]
            
            # Filter by budget if provided
            if budget:
                try:
                    # Extract number from budget string (e.g., "$50" -> 50)
                    budget_amount = int(''.join(c for c in budget if c.isdigit()))
                    activities = [a for a in activities if a.get('price_min', 0) <= budget_amount]
                except:
                    pass
            
            # Sort by rating and return limited results
            activities = sorted(activities, key=lambda x: x.get('rating', 0), reverse=True)
            return activities[:limit]
            
        except Exception as e:
            print(f"Database search error: {str(e)}")
            return []
    
    def _format_api_response(self, tours: List[Dict]) -> List[Dict]:
        """Format API response to standard format"""
        formatted = []
        for tour in tours:
            formatted.append({
                'name': tour.get('title', ''),
                'description': tour.get('description', ''),
                'reason': tour.get('summary', ''),
                'price_range': f"${tour.get('price_min', 0)}-${tour.get('price_max', 0)}",
                'price_min': tour.get('price_min', 0),
                'duration': tour.get('duration', ''),
                'category': tour.get('category', 'tours'),
                'rating': tour.get('rating', 0),
                'reviews': tour.get('review_count', 0),
                'url': tour.get('url', ''),
                'data_source': 'api'
            })
        return formatted
    
    def get_activity_details(self, activity_id: str) -> Dict:
        """Get detailed information about a specific activity"""
        # This would connect to API for more details
        pass
    
    def book_activity(self, activity_id: str, traveler_info: Dict) -> Dict:
        """Initiate activity booking"""
        # This would handle booking logic
        pass
    
    def _personalize_activities(self, activities: List[Dict], companions: str = None, dietary_preferences: List[str] = None) -> List[Dict]:
        """
        Personalize activities based on travel companions, dietary preferences, and time appropriateness
        """
        if not activities:
            return activities
        
        personalized = []
        
        for activity in activities:
            # Create a copy to avoid modifying original
            personalized_activity = activity.copy()
            
            # Add time appropriateness - filter out inappropriate timing
            category = personalized_activity.get('category', '').lower()
            time_pref = personalized_activity.get('time_preference', 'any')
            
            # Skip nightlife activities that should only be evening activities
            if category == 'nightlife' and time_pref == 'evening':
                personalized_activity['time_restriction'] = 'evening_only'
                personalized_activity['appropriate_times'] = ['7:00 PM - 11:00 PM']
            
            # Add companion-specific notes
            if companions:
                companion_notes = {
                    'couple': 'Perfect for romantic getaways and intimate experiences',
                    'family_kids': 'Family-friendly with activities suitable for children',
                    'friends': 'Great for group adventures and social experiences',
                    'solo': 'Ideal for solo travelers with opportunities to meet others',
                    'business': 'Professional setting suitable for business travelers'
                }
                
                if companions in companion_notes:
                    # Add companion context to description
                    original_reason = personalized_activity.get('reason', '')
                    personalized_activity['reason'] = f"{original_reason}. {companion_notes[companions]}"
            
            # Filter and modify food-related activities based on dietary preferences
            if dietary_preferences and personalized_activity.get('category') == 'food':
                dietary_str = ', '.join(dietary_preferences)
                personalized_activity['dietary_note'] = f"Dietary options available: {dietary_str}"
                
                # Boost activities based on dietary match
                activity_name_lower = personalized_activity.get('name', '').lower()
                activity_desc_lower = personalized_activity.get('description', '').lower()
                
                for pref in dietary_preferences:
                    if pref.lower() in activity_name_lower or pref.lower() in activity_desc_lower:
                        personalized_activity['match_score'] = 1.0  # Perfect match
                        break
                else:
                    personalized_activity['match_score'] = 0.7  # Good match but not perfect
            
            # Boost activities that match multiple user interests
            user_interest_matches = 0
            if hasattr(self, '_current_user_interests'):
                for interest in self._current_user_interests:
                    if interest.lower() in category:
                        user_interest_matches += 1
            
            personalized_activity['interest_match_count'] = user_interest_matches
            
            personalized.append(personalized_activity)
        
        # Sort by multiple factors: interest matches, match score, rating
        def sort_key(act):
            interest_matches = act.get('interest_match_count', 0)
            match_score = act.get('match_score', 0.5)  # Default neutral score
            rating = act.get('rating', 4.0)
            # Prioritize activities that match user interests
            return (interest_matches, match_score, rating)
        
        personalized.sort(key=sort_key, reverse=True)
        
        return personalized


# Global instance
activities_service = ActivitiesService()
