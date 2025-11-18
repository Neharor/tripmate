"""
Itinerary Agent - Generates detailed day-by-day travel schedules
Creates hour-by-hour itineraries with travel times and realistic schedules
"""

from .base_agent import BaseAgent
import json
from datetime import datetime, timedelta


class ItineraryAgent(BaseAgent):
    """
    Creates structured daily itineraries with realistic timing
    """
    
    def __init__(self):
        system_prompt = """You are an expert travel itinerary planner. Create realistic, well-paced daily schedules.

Your job: Generate hour-by-hour itineraries that are:
- Realistic (account for travel time, opening hours, meal breaks)
- Well-paced (not too rushed, not too slow)
- Logically ordered (group nearby attractions)
- Balanced (mix culture, food, relaxation)"""
        
        super().__init__("ItineraryAgent", system_prompt)
    
    def handle_request(self, input_data):
        """
        Generate day-by-day itinerary - Simple text format
        """
        try:
            user_prompt = f"""Based on this trip information:

{input_data}

Create a COMPACT day-by-day itinerary for the EXACT destination mentioned.

Format each day like this (CONCISE):

**Day 1: [Theme]**
09:00 - Arrive at [Airport] → Check-in
11:30 - [Hotel Area] → Drop bags, freshen up
13:00 - Lunch at [Restaurant] (VG/V/NV) - [Local dish] ($X)
15:00 - [Attraction 1] → [Brief description]
17:30 - [Attraction 2] 
19:00 - Dinner at [Restaurant] (VG/V/NV) - [Cuisine] ($X)

**Day 2: [Theme]**
[Continue similar compact format]

FORMATTING RULES - VERY IMPORTANT:
1. Use → arrows instead of bullet points
2. ONE LINE per activity (not multiple lines)
3. Only show cost when there's a charge
4. Mark restaurants: (V) vegetarian, (VG) vegan, (NV) non-veg
5. Keep descriptions to 3-5 words max
6. NO "Cost: $0" or "Free entrance" - just skip cost line
7. Max 5-6 activities per day
8. Use 24-hour time format (09:00, 15:00, 19:00)

CRITICAL RULES:
1. Use EXACT destination from conversation
2. Suggest REAL places that exist there
3. **MATCH INTERESTS** - 80% focused on their interest
4. **MATCH FOOD PREFERENCE**:
   - Vegetarian: ONLY vegetarian restaurants marked (V)
   - Vegan: ONLY vegan restaurants marked (VG)  
   - Non-vegetarian: Mix of all, marked (V), (VG), or (NV)
5. Stay within daily budget
6. EXACT number of days mentioned
7. Be realistic with timing
8. COMPLETE full itinerary - don't cut off
13. For food interest: Include specific dishes to try, famous restaurants, food markets, cooking classes
14. Make the itinerary's theme match their interest - not just generic sightseeing
15. **ONLY show costs when there's an actual charge** - Don't write "Cost: $0" or "Free entrance"
16. For free activities (beaches, parks, walking tours), just describe them without mentioning price
17. Keep format clean: time, activity name, brief description, cost (only if applicable)
18. **IMPORTANT**: Mark each restaurant/meal with dietary info - (V) for vegetarian, (VG) for vegan, (NV) for non-vegetarian

Generate the COMPLETE itinerary now (all days):"""

            llm_response = self._call_llm(user_prompt)
            
            # Return as simple text - no JSON parsing needed
            return {
                "itinerary_text": llm_response.strip()
            }
            
        except Exception as e:
            print(f"ItineraryAgent error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "itinerary_text": f"**Unable to generate itinerary**\n\nError: {str(e)}\n\nPlease try again with more specific preferences."
            }
    
    def validate_itinerary(self, itinerary_data):
        """
        Validate itinerary structure and timing
        """
        # TODO: Check for time conflicts, unrealistic travel times, etc.
        pass
    
    def optimize_route(self, activities):
        """
        Reorder activities to minimize travel time
        (Future: integrate with Google Maps Directions API)
        """
        # TODO: Use geocoding + routing to optimize order
        pass
