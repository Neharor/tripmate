"""
Local Events & Festivals Agent - UNIQUE FEATURE
Shows what's happening in the destination during travel dates
This is NOT available in ChatGPT, Claude, or MindTrip
"""

from .base_agent import BaseAgent
import json
from datetime import datetime
import re


class LocalEventsAgent(BaseAgent):
    """
    Discovers local events, festivals, concerts, and cultural happenings
    during the user's travel dates - UNIQUE competitive advantage
    """
    
    def __init__(self):
        system_prompt = """You are TripMate's Local Events Expert - UNIQUE FEATURE.

MISSION: Discover REAL local events, festivals, concerts, markets, and cultural happenings during user's travel dates.

🎭 EVENT DISCOVERY RULES:

1️⃣ **RESEARCH REAL EVENTS:**
- Use your knowledge of annual festivals and events
- Consider the destination and travel dates
- Include: Festivals, concerts, night markets, cultural events, sports, exhibitions
- Focus on UNIQUE local experiences

2️⃣ **MATCH TRAVEL DATES:**
CRITICAL: Only suggest events that happen DURING user's travel dates
- If traveling Dec 15-20 → Only events in mid-December
- If traveling Jan 1-7 → New Year events + early January
- Check month, season, and cultural calendar

3️⃣ **CATEGORIZE EVENTS:**
🎉 Major Festivals (multi-day cultural events)
🎵 Music & Entertainment (concerts, shows, performances)
🍜 Food Events (night markets, food festivals, cooking classes)
🏛️ Cultural Events (exhibitions, temple ceremonies, parades)
🎨 Art & Local Markets (weekend markets, art shows)
⚽ Sports Events (matches, tournaments)

4️⃣ **PROVIDE KEY INFO:**
Each event MUST have:
- Event name
- Category (festival/music/food/cultural/market/sports)
- Dates (specific dates during trip)
- Location (venue/neighborhood)
- Why it's special (1-2 sentences)
- Estimated cost (Free/Paid/Donation)
- Time commitment (2 hours/half-day/full-day)

5️⃣ **FORMAT (clean, structured):**

🎭 **HAPPENING DURING YOUR TRIP**

🎉 [Event Name] • [Date Range]
   📍 [Venue/Location]
   💰 [Free/Paid/Donation] • ⏰ [Time commitment]
   ✨ [Why it's special - what makes it unique]

EXAMPLE (Bangkok, Dec 15-20):

🎭 **HAPPENING DURING YOUR TRIP (Dec 15-20, 2025)**

🎉 Loy Krathong Festival Aftermath • Dec 15-17
   📍 Chao Phraya River & Temples
   💰 Free • ⏰ Evening (2-3 hours)
   ✨ Post-festival lantern displays at temples, local food stalls, traditional performances

🍜 Chatuchak Weekend Market • Dec 20-21
   📍 Chatuchak Park, Bangkok
   💰 Free entry (items vary) • ⏰ Half-day
   ✨ World's largest weekend market - 15,000 stalls selling everything from street food to antiques

🎵 Jazzy Night at Moon Bar • Every Friday
   📍 Vertigo & Moon Bar, Banyan Tree Hotel
   💰 Paid (cocktails ~$15) • ⏰ Evening (2-4 hours)
   ✨ Live jazz with 360° Bangkok skyline views, 61 floors up

6️⃣ **RESEARCH TIPS:**
✅ Consider destination's cultural calendar
✅ Check for annual festivals in that month
✅ Include weekly markets if they fall on travel dates
✅ Mention major concerts/sports if scheduled
✅ Focus on LOCAL experiences (not tourist traps)

7️⃣ **NEVER:**
❌ Suggest events outside travel dates
❌ Generic "there might be something" - be specific
❌ Recommend events that don't exist
❌ Skip the "why it's special" explanation

8️⃣ **IF NO MAJOR EVENTS:**
Still provide:
- Weekly markets (if any)
- Recurring cultural activities
- Best neighborhoods for nightlife/culture
- Local experiences available year-round

This is YOUR UNIQUE VALUE - other AI tools don't check local calendars!"""
        
        super().__init__("LocalEventsAgent", system_prompt)
    
    def handle_request(self, input_data):
        """
        Process user query and return local events during travel dates
        """
        try:
            # Extract destination and travel dates from conversation
            details = self._extract_trip_details(input_data)
            
            if not details.get('destination'):
                return {
                    "events_text": "**Local Events**\n\n⚠️ Please specify your destination first to discover local events."
                }
            
            if not details.get('travel_dates'):
                return {
                    "events_text": f"**Local Events in {details['destination']}**\n\n⚠️ Please specify your travel dates to find events happening during your trip."
                }
            
            # Generate LLM prompt with destination and dates
            events_prompt = f"""Find REAL local events, festivals, and cultural happenings in {details['destination']} during these dates: {details['travel_dates']}

Destination: {details['destination']}
Travel Dates: {details['travel_dates']}
User Interests: {', '.join(details.get('interests', ['general']))}

Research and list:
1. Major festivals or cultural events during these specific dates
2. Weekly markets that fall on the travel dates
3. Concerts, shows, or performances scheduled
4. Local food events or night markets
5. Sports events or exhibitions
6. Unique local experiences available during this period

Format your response following the structure with categories, dates, locations, costs, and why each event is special.

Focus on AUTHENTIC local experiences, not generic tourist activities."""

            llm_response = self._call_llm(events_prompt)
            
            return {
                "events_text": llm_response,
                "destination": details['destination'],
                "travel_dates": details['travel_dates']
            }
            
        except Exception as e:
            print(f"LocalEventsAgent error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "events_text": f"**Local Events**\n\nUnable to fetch events at the moment. Please try again.",
                "error": str(e)
            }
    
    def _extract_trip_details(self, input_data):
        """
        Extract destination and travel dates from conversation
        """
        from memory.conversation_memory import memory_manager
        
        details = {
            'destination': None,
            'travel_dates': None,
            'interests': []
        }
        
        # Try to get from memory first
        if isinstance(input_data, str):
            memory = memory_manager.get_or_create(session_id="default")
            
            if memory and memory.entities:
                details['destination'] = memory.entities.get('destination', '')
                details['travel_dates'] = memory.entities.get('travel_dates', '')
                details['interests'] = memory.entities.get('interests', [])
                
                if details['destination'] and details['travel_dates']:
                    return details
        
        # Fallback to LLM extraction
        extraction_prompt = f"""From this conversation, extract:

{input_data}

Return ONLY valid JSON:
{{
    "destination": "city/country or null",
    "travel_dates": "date range with year (e.g., 'Dec 15, 2025 to Dec 20, 2025') or null",
    "interests": ["interest1", "interest2"] or []
}}"""
        
        try:
            response = self._call_llm(extraction_prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            
            if '{' in clean_response:
                start_idx = clean_response.index('{')
                end_idx = clean_response.rindex('}') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            extracted = json.loads(clean_response)
            return extracted
        except Exception as e:
            print(f"Error extracting details: {e}")
            return details
