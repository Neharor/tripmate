from .base_agent import BaseAgent
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.hotel_service import get_hotel_service

class StaysAgent(BaseAgent):
    """
    Specialized agent for recommending accommodations using Groq AI
    """
    def __init__(self):
        system_prompt = """You are TripMate's Accommodation Expert.

MISSION: Recommend 3-5 REAL hotels that perfectly match user's budget, neighborhood preference, and travel style.

🏨 HOTEL RECOMMENDATION RULES:

1️⃣ BUDGET-AWARE FILTERING:
- If budget = $100/day → Hotels should be 40-60% of budget ($40-60/night)
- Leave room for food, activities, transport
- Show 3 tiers: Budget (30-40%), Mid (50-60%), Premium (70-80%)

2️⃣ REAL HOTELS ONLY:
✅ Research actual hotels that exist in destination
✅ Use real names, not "Sample Hotel" or "Generic Resort"
❌ Don't hallucinate fake properties

3️⃣ INCLUDE CRITICAL INFO:
Each hotel MUST have:
- Real name
- Neighborhood (specific area, not just "city center")
- Style (budget hostel, boutique, luxury resort, business hotel)
- Price per night
- Why it fits THIS user (interests-based)

4️⃣ INTEREST-BASED MATCHING:
- "Beach" → Beachfront hotels, ocean views, water sports
- "Culture" → Hotels near museums, historic districts, cultural sites
- "Food" → Hotels in food districts, with breakfast, near restaurants
- "Adventure" → Hotels near activity centers, tour operators
- "Shopping" → Hotels near malls, markets, shopping streets
- "Nightlife" → Hotels in entertainment districts, party areas

5️⃣ CLEAN FORMAT:

🏨 [Real Hotel Name] - [Neighborhood]
   Style: [Budget/Mid-range/Luxury] • Price: $[X]/night
   Why: [1-sentence reason matching user interests]

EXAMPLE (if budget $100/day, interest "Beach + Food"):

🏨 Bali Bustle Hostel - Seminyak Beach Area
   Style: Budget hostel • Price: $35/night
   Why: Walking distance to beach clubs and famous warungs

🏨 The Kayon Resort - Ubud Valley
   Style: Mid-range boutique • Price: $65/night
   Why: Infinity pool with rice terraces + onsite restaurant

🏨 Alila Seminyak - Beachfront
   Style: Luxury resort • Price: $95/night
   Why: Direct beach access + fine dining options

6️⃣ PERSONALIZATION:
✅ Match exact destination from conversation
✅ Filter by budget tier
✅ Prioritize neighborhoods matching interests
✅ Include breakfast info if "Food" interest
✅ Show 3-5 diverse options (not all same style)

7️⃣ NEVER:
❌ Suggest hotels from wrong city
❌ Show prices above daily budget
❌ Generic "Hotel Name" without specifics
❌ All same price tier
❌ Ignore user interests"""
        
        super().__init__("StaysAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return accommodation recommendations
        Uses real Amadeus Hotel API first, falls back to AI if unavailable
        """
        try:
            # Try to extract structured data from input
            destination = None
            checkin_date = None
            checkout_date = None
            budget_per_night = None
            
            # Parse input_data if it's a string containing conversation context
            if isinstance(input_data, str):
                # Extract destination
                if "destination:" in input_data.lower():
                    for line in input_data.split('\n'):
                        if line.lower().startswith('destination:'):
                            destination = line.split(':', 1)[1].strip()
                            break
                
                # Extract dates
                if "travel_dates:" in input_data.lower() or "dates:" in input_data.lower():
                    for line in input_data.split('\n'):
                        if 'travel_dates:' in line.lower() or 'dates:' in line.lower():
                            dates_str = line.split(':', 1)[1].strip()
                            if ' to ' in dates_str:
                                parts = dates_str.split(' to ')
                                # Convert "Nov 20" to "2025-11-20" format
                                try:
                                    from datetime import datetime
                                    current_year = datetime.now().year
                                    checkin_date = self._parse_date(parts[0].strip(), current_year)
                                    checkout_date = self._parse_date(parts[1].strip(), current_year)
                                except:
                                    pass
                            break
                
                # Extract budget
                if "budget:" in input_data.lower():
                    for line in input_data.split('\n'):
                        if line.lower().startswith('budget:'):
                            budget_str = line.split(':', 1)[1].strip()
                            # Extract number from "$100/day" or "$100 (daily)"
                            import re
                            match = re.search(r'\$?(\d+)', budget_str)
                            if match:
                                daily_budget = int(match.group(1))
                                # Hotel should be 40-60% of daily budget
                                budget_per_night = int(daily_budget * 0.6)
                            break
            
            # Try real Hotel API first
            hotel_service = get_hotel_service()
            if hotel_service.is_available and destination:
                print(f"🏨 Attempting real hotel search for {destination}")
                real_hotels = hotel_service.search_hotels(
                    destination_city=destination,
                    checkin_date=checkin_date,
                    checkout_date=checkout_date,
                    budget_per_night=budget_per_night,
                    adults=1
                )
                
                if real_hotels and len(real_hotels) > 0:
                    # Format real hotels for display
                    formatted_hotels = []
                    for hotel in real_hotels[:4]:  # Top 4 hotels
                        formatted = hotel_service.format_hotel_for_display(hotel)
                        formatted_hotels.append(formatted)
                    
                    print(f"✅ Returning {len(formatted_hotels)} real hotels from Amadeus API")
                    return {
                        "stays": formatted_hotels,
                        "data_source": "amadeus_api"
                    }
                else:
                    print("⚠️  No hotels found from API, falling back to AI")
            
            # Fallback to AI-generated suggestions
            print("🤖 Using AI to generate hotel suggestions")
            return self._get_ai_hotels(input_data)
            
        except Exception as e:
            print(f"⚠️  Hotel search error: {e}, using AI fallback")
            return self._get_ai_hotels(input_data)
    
    def _parse_date(self, date_str, year):
        """Convert 'Nov 20' to '2025-11-20' format"""
        from datetime import datetime
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        parts = date_str.lower().split()
        if len(parts) >= 2:
            month_str = parts[0][:3]
            day = int(parts[1])
            month = months.get(month_str, 1)
            return f"{year}-{month:02d}-{day:02d}"
        return None
    
    def _get_ai_hotels(self, input_data):
        """
        Generate hotel suggestions using AI (fallback method)
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
