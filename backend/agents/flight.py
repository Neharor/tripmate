"""
Flight Agent - Search and recommend flights using Amadeus API
Provides real flight data with actual prices and booking options
"""

from .base_agent import BaseAgent
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.flight_service import FlightService


class FlightAgent(BaseAgent):
    """
    Flight search using real Amadeus API
    Falls back to LLM suggestions if API unavailable
    """
    
    def __init__(self):
        system_prompt = """You are a flight expert. Recommend flights based on user's trip details.

Your job: Suggest flight options with realistic pricing and schedules."""
        
        super().__init__("FlightAgent", system_prompt)
        self.flight_service = FlightService()
    
    def handle_request(self, input_data):
        """
        Generate flight recommendations using Amadeus API or LLM fallback
        """
        try:
            # Extract trip details from conversation
            details = self._extract_trip_details(input_data)
            
            if not details.get('destination'):
                return {
                    "flight_text": "**Flight Search**\n\n⚠️ Please specify your destination first to search for flights."
                }
            
            # Try to get real flights from Amadeus
            if self.flight_service.enabled:
                return self._search_real_flights(details)
            else:
                # Fallback to LLM suggestions
                return self._llm_flight_suggestions(input_data)
            
        except Exception as e:
            print(f"FlightAgent error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "flight_text": f"**Flight recommendations unavailable**\n\nError: {str(e)}\n\n💡 Please try again or search manually on Google Flights."
            }
    
    def _extract_trip_details(self, input_data):
        """
        Extract destination, dates, origin from conversation
        """
        # Use LLM to extract structured data
        extraction_prompt = f"""From this conversation, extract trip details:

{input_data}

Return ONLY valid JSON (no other text):
{{
    "destination": "city name",
    "origin": "origin city (extract from 'Departure city:', 'flying from', or use 'Unknown' if not found)",
    "departure_date": "YYYY-MM-DD (7 days from now if not mentioned)",
    "return_date": "YYYY-MM-DD (departure + trip duration)",
    "adults": 1
}}

IMPORTANT: Look for "Departure city:" in the conversation to find the origin."""
        
        try:
            response = self._call_llm(extraction_prompt)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            
            if '{' in clean_response:
                start_idx = clean_response.index('{')
                end_idx = clean_response.rindex('}') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            details = json.loads(clean_response)
            return details
        except Exception as e:
            print(f"Error extracting trip details: {e}")
            return {}
    
    def _search_real_flights(self, details):
        """
        Search real flights using Amadeus API
        """
        # Get airport codes
        origin_code = self.flight_service.get_airport_code(details.get('origin', 'Los Angeles'))
        dest_code = self.flight_service.get_airport_code(details.get('destination', ''))
        
        if dest_code == 'UNKNOWN':
            return self._llm_flight_suggestions(f"Destination: {details.get('destination')}")
        
        # Search flights
        flights = self.flight_service.search_flights(
            origin=origin_code,
            destination=dest_code,
            departure_date=details.get('departure_date'),
            return_date=details.get('return_date'),
            adults=details.get('adults', 1),
            max_results=3
        )
        
        # Format flight results
        return self._format_flight_results(flights, details)
    
    def _format_flight_results(self, flights, details):
        """
        Format Amadeus flight data into user-friendly text
        """
        if not flights:
            return {
                "flight_text": "**No Flights Found**\n\nPlease try different dates or search manually on Google Flights."
            }
        
        # Check if fallback mode
        if flights[0].get('type') == 'fallback':
            flight_data = flights[0]
            text = f"""**Flight Options: {flight_data['origin']} → {flight_data['destination']}**

⚠️ Real-time flight data unavailable. Here are general suggestions:

**Airlines that fly this route:**
"""
            for airline in flight_data['airlines']:
                text += f"• {airline}\n"
            
            price_range = flight_data['estimated_price']
            text += f"""
**Estimated Price Range:**
${price_range[0]} - ${price_range[1]} per person (round-trip)

**Departure:** {flight_data['departure_date']}
**Return:** {flight_data.get('return_date', 'Not specified')}

💡 **Booking Tips:**
- Check Google Flights, Skyscanner, or Kayak for real-time prices
- Book 2-3 months in advance for best deals
- Consider layovers to save money

**To enable real-time flight search:**
Contact your administrator to set up Amadeus API credentials.
Get free API key from: https://developers.amadeus.com/register
"""
            return {"flight_text": text}
        
        # Format real Amadeus results
        text = f"""**Flight Options: {details.get('origin')} → {details.get('destination')}**

Found {len(flights)} available flights:\n\n"""
        
        for idx, flight in enumerate(flights, 1):
            text += f"""**Option {idx}** - ${flight['price']} {flight['currency']}
"""
            # Outbound flight
            outbound = flight['itineraries'][0]
            first_seg = outbound['segments'][0]
            last_seg = outbound['segments'][-1]
            
            text += f"""Outbound: {first_seg['departure']['airport']} → {last_seg['arrival']['airport']}
  Airline: {first_seg['airline']} {first_seg['flight_number']}
  Departure: {first_seg['departure']['time']}
  Arrival: {last_seg['arrival']['time']}
  Duration: {outbound['duration']}
"""
            
            # Return flight (if exists)
            if len(flight['itineraries']) > 1:
                inbound = flight['itineraries'][1]
                first_seg = inbound['segments'][0]
                last_seg = inbound['segments'][-1]
                
                text += f"""Return: {first_seg['departure']['airport']} → {last_seg['arrival']['airport']}
  Airline: {first_seg['airline']} {first_seg['flight_number']}
  Departure: {first_seg['departure']['time']}
  Arrival: {last_seg['arrival']['time']}
  Duration: {inbound['duration']}
"""
            
            text += f"\n✅ {flight['numberOfBookableSeats']} seats available\n\n"
        
        text += """💡 **Ready to book?**
Click on your preferred option to complete booking on airline website.
"""
        
        return {"flight_text": text}
    
    def _llm_flight_suggestions(self, input_data):
        """
        Fallback to LLM-based flight suggestions
        """
        user_prompt = f"""Based on this trip information:

{input_data}

Suggest REALISTIC flight options. Research actual airlines that fly this route.

Format like this:

**Flight Options**

**Outbound Flight**
[Airline Name] (or "Multiple airlines available")
[Origin City] → [Destination from conversation]
Typical flight time: ~[X] hours
Estimated price: $[reasonable price] (Economy)

**Return Flight**
[Airline Name]
[Destination] → [Origin City]
Typical flight time: ~[X] hours
Estimated price: $[reasonable price] (Economy)

**Estimated Total:** $[total]

💡 Booking Tips:
- Book 2-3 months in advance for best prices
- Check Skyscanner, Google Flights, or Kayak for current deals
- Consider layovers to save money

CRITICAL RULES:
1. Use the EXACT destination from conversation
2. Suggest realistic airlines that actually fly this route
3. Don't make up specific flight numbers
4. Price should fit their budget (mention if flights will use most of budget)
5. Be honest about typical flight durations
6. Keep it simple - just airline names and estimates"""

        llm_response = self._call_llm(user_prompt)
        
        # Return as simple text
        return {
            "flight_text": llm_response.strip()
        }
