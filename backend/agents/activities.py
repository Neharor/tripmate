from .base_agent import BaseAgent
import json

class ActivitiesAgent(BaseAgent):
    """
    Specialized agent for recommending LOCAL PLACES TO VISIT that need booking (tours, attractions, etc.)
    This is shown AFTER the itinerary as additional bookable experiences.
    """
    def __init__(self):
        system_prompt = """You are a local attractions and tours expert. Your job: recommend BOOKABLE LOCAL PLACES and EXPERIENCES.

Focus on:
- Popular tours that need advance booking
- Major attractions with tickets
- Unique experiences (cooking classes, spa, diving, etc.)
- Day trips and excursions

Each recommendation should include:
- Name of place/tour
- Brief description (1 line)
- Approximate price
- Why it's worth booking

Keep it concise - show 4-5 top bookable experiences."""
        
        super().__init__("ActivitiesAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return activity recommendations
        """
        try:
            # Extract context from input
            input_lower = input_data.lower()
            
            # Extract destination from context
            destination = "this destination"
            if 'bali' in input_lower:
                destination = "Bali"
            elif 'bangkok' in input_lower:
                destination = "Bangkok"
            elif 'paris' in input_lower:
                destination = "Paris"
            elif 'tokyo' in input_lower:
                destination = "Tokyo"
            elif 'rome' in input_lower:
                destination = "Rome"
            
            # Extract budget context if mentioned
            budget_conscious = any(word in input_lower for word in ['budget', 'cheap', 'affordable', 'free', 'low cost'])
            
            # Extract interests from context
            interests = []
            if 'beach' in input_lower or 'swim' in input_lower or 'surf' in input_lower:
                interests.append('beach activities')
            if 'food' in input_lower or 'eat' in input_lower or 'culinary' in input_lower:
                interests.append('food experiences')
            if 'culture' in input_lower or 'temple' in input_lower or 'museum' in input_lower:
                interests.append('cultural sites')
            if 'adventure' in input_lower or 'hiking' in input_lower or 'trek' in input_lower:
                interests.append('adventure activities')
            if 'night' in input_lower or 'bar' in input_lower or 'club' in input_lower:
                interests.append('nightlife')
            
            # Build the prompt for BOOKABLE local places
            if budget_conscious:
                user_prompt = f"""User wants BUDGET-FRIENDLY bookable experiences in {destination}.

Recommend 4-5 affordable tours/attractions that need advance booking. Format each as:

� Experience Name - Brief description, why book it ($price range)

Examples:
� Ubud Rice Terrace Walk - Guided tour of iconic terraces, skip-the-line entry ($15-25)
� Snorkeling at Blue Lagoon - Equipment included, boat trip ($20-30)
🎫 Traditional Cooking Class - 3-hour class, market visit included ($25-35)

CRITICAL: Focus on BOOKABLE experiences under $50. Include specific names and prices."""
            elif interests:
                interest_str = ', '.join(interests)
                user_prompt = f"""User wants bookable experiences in {destination} focused on: {interest_str}

Recommend 4-5 tours/attractions based on their interests. Format each as:

� Experience Name - Brief description, why book it ($price range)

Examples:
� Sunset Cruise & Dinner - Private boat, 3 hours, dinner included ($60-80)
� Scuba Diving Certification - 2-day course, equipment provided ($200-250)
🎫 Street Food Walking Tour - 3 hours, 8+ tastings, local guide ($40-60)

CRITICAL: Match to interests: {interest_str}. Include specific names and prices."""
            else:
                user_prompt = f"""Based on: {input_data}

Recommend 4-5 TOP bookable experiences in {destination} that tourists should pre-book. Format each as:

� Experience Name - Brief description, why book it ($price range)

Examples:
� Tanah Lot Temple Sunset Tour - Skip lines, guided tour, sunset views ($30-45)
� Mount Batur Sunrise Trek - 4am start, breakfast at summit, guide included ($40-60)
🎫 Spa & Wellness Package - 2-hour treatment, massage + facial ($50-80)

CRITICAL: ONLY experiences that need advance booking. Include specific names and prices."""

            llm_response = self._call_llm(user_prompt)
            
            # Strip any JSON formatting
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            # Split into individual activities if formatted as a list
            activities = [line.strip() for line in clean_response.split('\n') if line.strip() and line.strip().startswith(('�', '�🎯', '🌊', '🍜', '🏛️', '🚶', '•', '-'))]
            
            if not activities:
                activities = [clean_response]
            
            return {
                "activities": activities
            }
            
        except Exception as e:
            print(f"ActivitiesAgent error: {str(e)}")
            return {
                "activities": [f"Error getting activities: {str(e)}"]
            }
