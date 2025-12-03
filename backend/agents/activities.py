from .base_agent import BaseAgent
from services.activities_service import activities_service
import re

class ActivitiesAgent(BaseAgent):
    """
    Specialized agent for recommending LOCAL PLACES TO VISIT that need booking (tours, attractions, etc.)
    Uses real API data from GetYourGuide, Viator, or curated database.
    """
    def __init__(self):
        system_prompt = """You are TripMate's Experience Curator.

MISSION: Recommend curated, bookable activities that match user interests."""
        
        super().__init__("ActivitiesAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return activity recommendations from API/database
        """
        try:
            input_lower = input_data.lower()
            
            # Extract destination, interests, and budget
            destination = self._extract_destination(input_lower)
            interests = self._extract_interests(input_lower)
            budget = self._extract_budget(input_lower)
            
            # Search for real activities using the service
            activities_list = activities_service.search_activities(
                destination=destination,
                interests=interests,
                budget=budget,
                limit=5
            )
            
            # Format activities for display
            formatted_activities = self._format_activities(activities_list)
            
            return {
                "activities": formatted_activities,
                "destination": destination,
                "count": len(formatted_activities),
                "data_source": "real_api" if activities_list and activities_list[0].get('data_source') == 'api' else 'curated_database'
            }
            
        except Exception as e:
            print(f"ActivitiesAgent error: {str(e)}")
            return {
                "activities": [f"Error getting activities: {str(e)}"],
                "error": True
            }
    
    def _extract_destination(self, input_lower: str) -> str:
        """Extract destination from user input"""
        destinations = {
            'bali': 'Bali',
            'bangkok': 'Bangkok',
            'paris': 'Paris',
            'tokyo': 'Tokyo',
            'rome': 'Rome'
        }
        
        for key, value in destinations.items():
            if key in input_lower:
                return value
        
        return "this destination"
    
    def _extract_interests(self, input_lower: str) -> list:
        """Extract interests from user input"""
        interests_map = {
            'beach': ['water', 'sightseeing'],
            'food': ['food', 'dining'],
            'culture': ['culture'],
            'adventure': ['adventure'],
            'night': ['nightlife']
        }
        
        interests = []
        for keyword, categories in interests_map.items():
            if keyword in input_lower:
                interests.extend(categories)
        
        return list(set(interests))
    
    def _extract_budget(self, input_lower: str) -> str:
        """Extract budget from user input"""
        matches = re.findall(r'\$(\d+)|(\d+)\s*(?:dollars?|per day|daily)', input_lower)
        if matches:
            for match in matches:
                amount = match[0] if match[0] else match[1]
                if amount:
                    return f"${amount}"
        return None
    
    def _format_activities(self, activities_list: list) -> list:
        """Format activities for display"""
        formatted = []
        
        for activity in activities_list:
            formatted_activity = f"""🎯 {activity.get('name', 'Activity')}
   What: {activity.get('description', '')}
   Why: {activity.get('reason', '')}
   Price: {activity.get('price_range', 'Contact for pricing')}"""
            
            if activity.get('rating'):
                formatted_activity += f"\n   Rating: ⭐ {activity.get('rating')}/5 ({activity.get('reviews', 0)} reviews)"
            
            formatted.append(formatted_activity)
        
        return formatted
