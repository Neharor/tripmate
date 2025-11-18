from .base_agent import BaseAgent
import json

class StaysAgent(BaseAgent):
    """
    Specialized agent for recommending accommodations using Groq AI
    """
    def __init__(self):
        system_prompt = """You are a hotel expert. Your ONLY job: recommend ACCOMMODATIONS (hotels/hostels/resorts).

DO NOT mention destinations, flights, or activities. ONLY places to sleep.

Keep it super short - 1 line per hotel."""
        
        super().__init__("StaysAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return accommodation recommendations
        """
        try:
            # Extract destination and budget from conversation
            user_prompt = f"""Based on this conversation:

{input_data}

Recommend 3-4 REAL hotels/accommodations for the destination mentioned with DIFFERENT PRICE RANGES.

CRITICAL RULES:
1. Use the EXACT destination from the conversation (e.g., if they said "Bali", recommend Bali hotels)
2. Research and suggest REAL hotels that actually exist in that destination
3. **MATCH THE BUDGET**: If budget is $100/day, suggest hotels that leave room for food & activities
   - Budget option: 30-40% of daily budget (e.g., $30-40/night for $100/day budget)
   - Mid-range: 50-60% of daily budget (e.g., $50-60/night)
   - Premium: 70-80% of daily budget (e.g., $70-80/night)
4. **MATCH THEIR INTERESTS**:
   - If "Food" interest: Hotels near restaurants/food districts, include breakfast options
   - If "Shopping" interest: Hotels near shopping areas, malls, markets
   - If "Beach" interest: Beach resorts, hotels with beach access, ocean views
   - If "Culture" interest: Hotels near historic sites, museums, cultural districts
   - If "Adventure" interest: Hotels near adventure activities, tour operators
   - If "Nightlife" interest: Hotels in entertainment/party districts
5. Use this EXACT format (one hotel per line):

🏨 [Real Hotel Name] - [Brief description], $[price]/night

Example output:
🏨 Bali Bustle Hostel - Budget hostel near Seminyak Beach, $25/night
🏨 The Kayon Resort - Mid-range resort with pool and culture tours, $55/night
🏨 Alila Ubud - Luxury resort in cultural heart of Bali, $85/night

IMPORTANT:
- Provide 3-4 options at DIFFERENT price points
- ALL prices must fit within the daily budget (leave room for food/activities)
- DO NOT suggest hotels from other destinations
- Keep descriptions under 8 words
- ONLY hotels - NO flights, NO activities"""

            llm_response = self._call_llm(user_prompt)
            
            # Parse the response to extract individual hotels
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            # Split by lines and filter out hotel entries
            hotels = []
            for line in clean_response.split('\n'):
                line = line.strip()
                if line.startswith('🏨'):
                    hotels.append(line)
            
            # If we got hotels, return them as separate items
            if hotels:
                return {
                    "stays": hotels
                }
            else:
                # Fallback: return as single item
                return {
                    "stays": [clean_response]
                }
            
        except Exception as e:
            print(f"StaysAgent error: {str(e)}")
            return {
                "stays": [f"Error getting accommodations: {str(e)}"]
            }
