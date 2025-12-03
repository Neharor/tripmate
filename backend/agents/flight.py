"""
Flight Agent - Search and recommend flights using:
1. Amadeus API (real-time prices)
2. ML Price Prediction (best booking time)
3. Kaggle historical data (price trends)
"""

from .base_agent import BaseAgent
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.flight_service import FlightService
from services.route_intelligence import RouteIntelligence

# Import ML predictor
try:
    from ml.flight_price_predictor import get_predictor
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False
    print("⚠️ ML predictor not available. Install pandas, numpy, scikit-learn")


class FlightAgent(BaseAgent):
    """
    Hybrid flight search:
    - Amadeus API for real flights
    - ML model for price predictions
    - Kaggle data for route insights
    """
    
    def __init__(self):
        system_prompt = """You are TripMate's Flight Expert.

MISSION: Provide 3 realistic flight options: Cheapest, Fastest, and Best Overall.

✈️ FLIGHT RECOMMENDATION RULES:

1️⃣ ALWAYS SHOW 3 OPTIONS:
- Cheapest: Lowest price (may have longer duration/layovers)
- Fastest: Shortest flight time (may be more expensive)
- Best Overall: Optimal balance of price + time + airline quality

2️⃣ REALISTIC PRICING:
- Use actual airline pricing patterns
- Don't show random numbers
- Consider route distance + airline + class
- Examples:
  * Tokyo → Bali: $800-$1,200 (8-12 hrs)
  * LA → Tokyo: $600-$1,000 (11-13 hrs)
  * NYC → London: $400-$800 (7-8 hrs)

3️⃣ ACCURATE TIMING:
- Show realistic flight durations
- Include layover cities (Singapore, Dubai, etc.)
- Time format: "8h 30m" or "11h 45m"
- Departure/arrival times: realistic (not all 9 AM)

4️⃣ REAL AIRLINES:
- Use airlines that ACTUALLY fly the route
- Examples:
  * Asia routes: Singapore Air, ANA, Garuda, Thai Airways
  * US-Europe: United, Delta, Lufthansa, BA, Air France
  * Budget: AirAsia, Scoot, JetBlue, Southwest (when applicable)

5️⃣ LAYOVER LOGIC:
- Direct flights: rare on long-haul, mention if available
- 1-stop: specify hub (Singapore, Dubai, Hong Kong, etc.)
- 2-stop: only for very long routes or budget options

6️⃣ FORMAT (clean bullet points):
✈️ Flight Options (Origin → Destination)

🏆 Best Overall: [Airline] • [Duration] • $[Price]
   Depart: [Time] → Arrive: [Time]
   [Direct/1 stop via City]

💰 Cheapest: [Airline] • [Duration] • $[Price]
   Depart: [Time] → Arrive: [Time]
   [Direct/1 stop via City]

⚡ Fastest: [Airline] • [Duration] • $[Price]
   Depart: [Time] → Arrive: [Time]
   [Direct/1 stop via City]

7️⃣ DATA SOURCES:
- Amadeus API (if enabled): Use real data
- Fallback: Use realistic estimates based on route knowledge

8️⃣ NEVER:
❌ Show impossible direct flights (Tokyo→Bali direct doesn't exist)
❌ Use airlines that don't fly the route (Lion Air on Seoul-Tokyo)
❌ Show unrealistic prices ($50 for Tokyo-Bali)
❌ Hallucinate random flight numbers"""
        
        super().__init__("FlightAgent", system_prompt)
        self.flight_service = FlightService()
        self.route_intelligence = RouteIntelligence()
        
        # Initialize ML predictor (disabled for now due to NumPy compatibility issues)
        self.predictor = None
        if ML_ENABLED:
            try:
                self.predictor = get_predictor()
                print("✓ ML price predictor initialized")
            except Exception as e:
                print(f"⚠️ ML predictor initialization failed: {e}")
                self.predictor = None
    
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
        Search real flights using Amadeus API and intelligently filter
        """
        # Get airport codes
        origin_code = self.flight_service.get_airport_code(details.get('origin', 'Los Angeles'))
        dest_code = self.flight_service.get_airport_code(details.get('destination', ''))
        
        if dest_code == 'UNKNOWN':
            return self._llm_flight_suggestions(f"Destination: {details.get('destination')}")
        
        print(f"🔍 Searching flights: {origin_code} → {dest_code}")
        
        # Search flights - OPTIMIZED: Get 3 best flights directly (faster!)
        # Still REAL-TIME data from Amadeus API ✅
        all_flights = self.flight_service.search_flights(
            origin=origin_code,
            destination=dest_code,
            departure_date=details.get('departure_date'),
            return_date=details.get('return_date'),
            adults=details.get('adults', 1),
            max_results=3  # 3 flights = 3x faster, still real-time! ⚡
        )
        
        if not all_flights:
            print("⚠️ No flights found from Amadeus, using LLM fallback")
            return self._llm_flight_suggestions(f"Route: {details.get('origin')} to {details.get('destination')}")
        
        print(f"✅ Found {len(all_flights)} flights from Amadeus")
        
        # Filter best options: Cheapest, Fastest, Earliest
        best_flights = self._filter_best_flights(all_flights)
        
        # Let LLM format the results nicely
        return self._llm_format_real_flights(best_flights, details)
    
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
        Generate specific flight recommendations using route-based airline knowledge
        """
        
        # Extract route info
        details = self._extract_trip_details(input_data)
        origin = details.get('origin', 'Unknown')
        destination = details.get('destination', 'Unknown')
        
        # Route-specific airline database
        route_airlines = self._get_airlines_for_route(origin, destination)
        
        user_prompt = f"""Based on this trip information:

{input_data}

CRITICAL: Use ONLY these airlines that actually fly {origin} → {destination}:
{', '.join(route_airlines['airlines'])}

Return ONLY valid JSON array (no other text) with 2-3 flights from the above airlines:
[
  {{
    "airline": "One of: {', '.join(route_airlines['airlines'])}",
    "flight_number": "realistic format for that airline",
    "departure_time": "HH:MM AM/PM",
    "arrival_time": "HH:MM AM/PM",
    "duration": "Xh XXm (realistic for {route_airlines['distance']})",
    "stops": 0 or 1,
    "price_one_way": realistic USD price for {route_airlines['distance']},
    "price_round_trip": realistic USD price for {route_airlines['distance']},
    "cabin_class": "Economy" or "Premium Economy",
    "departure_date": "extract from conversation or use next week",
    "return_date": "extract from conversation",
    "booking_url": "official airline website from list below"
  }}
]

Booking URLs:
{chr(10).join(f"- {airline}: {url}" for airline, url in route_airlines['booking_urls'].items())}

RULES:
1. ONLY use airlines from the list above
2. Flight duration must match route ({route_airlines['duration']})
3. Price range: {route_airlines['price_range']}
4. Mix budget + premium airlines
5. Extract exact dates from conversation
6. If user prefers morning/afternoon/evening, prioritize those times
7. Sort by price (cheapest first)

RESPOND WITH ONLY THE JSON ARRAY."""

        try:
            llm_response = self._call_llm(user_prompt)
            
            # Clean response
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            if '[' in clean_response:
                start_idx = clean_response.index('[')
                end_idx = clean_response.rindex(']') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            flights = json.loads(clean_response)
            
            # Return structured flight data
            return {
                "flights": flights
            }
            
        except Exception as e:
            print(f"Error parsing LLM flight response: {e}")
            # Fallback to simple text format
            return {
                "flight_text": f"Unable to generate flight suggestions. Error: {str(e)}"
            }
    
    def _get_airlines_for_route(self, origin, destination):
        """
        Get airlines that actually fly specific routes
        Uses RouteIntelligence service (dynamic, API-driven)
        Returns dict with airlines, duration, price range, booking URLs
        """
        return self.route_intelligence.get_route_info(origin, destination)
    
    def _filter_best_flights(self, all_flights):
        """
        Filter flights to show best options: Cheapest, Fastest, Earliest
        Returns max 3 flights
        """
        if not all_flights:
            return []
        
        # Parse flight data for sorting
        parsed_flights = []
        for flight in all_flights:
            try:
                price = float(flight.get('price', 999999))
                
                # Calculate total duration (all segments)
                total_duration_mins = 0
                for itinerary in flight.get('itineraries', []):
                    duration_str = itinerary.get('duration', 'PT0H0M')
                    # Parse ISO 8601 duration: PT10H30M
                    hours = 0
                    minutes = 0
                    if 'H' in duration_str:
                        hours = int(duration_str.split('PT')[1].split('H')[0])
                    if 'M' in duration_str:
                        minutes = int(duration_str.split('H')[-1].replace('M', '').replace('PT', ''))
                    total_duration_mins += (hours * 60 + minutes)
                
                # Get departure time
                first_segment = flight.get('itineraries', [{}])[0].get('segments', [{}])[0]
                departure_time = first_segment.get('departure', {}).get('at', '')
                
                parsed_flights.append({
                    'flight': flight,
                    'price': price,
                    'duration_mins': total_duration_mins,
                    'departure_time': departure_time
                })
            except Exception as e:
                print(f"Error parsing flight for filtering: {e}")
                continue
        
        if not parsed_flights:
            return all_flights[:3]  # Return first 3 if parsing fails
        
        # Sort and get best options
        best_options = []
        
        # 1. Cheapest flight
        cheapest = min(parsed_flights, key=lambda x: x['price'])
        best_options.append({
            **cheapest['flight'],
            'recommendation_reason': 'Cheapest Option'
        })
        
        # 2. Fastest flight (shortest duration)
        fastest = min(parsed_flights, key=lambda x: x['duration_mins'])
        if fastest['flight'] != cheapest['flight']:  # Avoid duplicates
            best_options.append({
                **fastest['flight'],
                'recommendation_reason': 'Fastest Flight'
            })
        
        # 3. Earliest departure
        earliest = min(parsed_flights, key=lambda x: x['departure_time'])
        if earliest['flight'] not in [cheapest['flight'], fastest['flight']]:
            best_options.append({
                **earliest['flight'],
                'recommendation_reason': 'Earliest Departure'
            })
        
        # If we have less than 3, add more options
        while len(best_options) < 3 and len(parsed_flights) > len(best_options):
            for pf in parsed_flights:
                if pf['flight'] not in [opt for opt in best_options]:
                    best_options.append({
                        **pf['flight'],
                        'recommendation_reason': 'Alternative Option'
                    })
                    break
        
        print(f"✅ Filtered to {len(best_options)} best flights")
        return best_options[:3]
    
    def _llm_format_real_flights(self, flights, details):
        """
        Format real Amadeus flight data using templates (NO LLM - faster!)
        """
        formatted_flights = []
        
        for idx, flight in enumerate(flights, 1):
            try:
                # Extract key details
                price = flight.get('price', 'N/A')
                currency = flight.get('currency', 'USD')
                reason = flight.get('recommendation_reason', 'Good option')
                
                # Outbound
                outbound = flight.get('itineraries', [{}])[0]
                out_segments = outbound.get('segments', [])
                out_first = out_segments[0] if out_segments else {}
                out_last = out_segments[-1] if out_segments else {}
                
                # Parse times
                dep_time = out_first.get('departure', {}).get('at', '')
                arr_time = out_last.get('arrival', {}).get('at', '')
                
                # Format times nicely (2025-01-15T10:30:00 → 10:30 AM)
                from datetime import datetime
                try:
                    dep_dt = datetime.fromisoformat(dep_time.replace('Z', '+00:00'))
                    arr_dt = datetime.fromisoformat(arr_time.replace('Z', '+00:00'))
                    dep_formatted = dep_dt.strftime("%I:%M %p")
                    arr_formatted = arr_dt.strftime("%I:%M %p")
                    dep_date = dep_dt.strftime("%b %d")
                    arr_date = arr_dt.strftime("%b %d")
                except:
                    dep_formatted = dep_time
                    arr_formatted = arr_time
                    dep_date = ""
                    arr_date = ""
                
                # Duration (PT5H30M → 5h 30m)
                duration = outbound.get('duration', '')
                duration_formatted = duration.replace('PT', '').replace('H', 'h ').replace('M', 'm')
                
                # Stops
                stops = len(out_segments) - 1
                stops_text = "Direct" if stops == 0 else f"{stops} stop(s)"
                
                # Airline
                airline_code = out_first.get('carrierCode', 'Unknown')
                airline_name = self._get_airline_name(airline_code)
                
                # Departure/Arrival cities
                dep_city = out_first.get('departure', {}).get('iataCode', '')
                arr_city = out_last.get('arrival', {}).get('iataCode', '')
                
                # Build formatted text
                flight_text = f"""✈️ **{reason}**
{airline_name} ({airline_code})
{dep_city} → {arr_city}
🛫 Departs: {dep_formatted} ({dep_date})
🛬 Arrives: {arr_formatted} ({arr_date})
⏱️ Duration: {duration_formatted}
🔄 {stops_text}
💰 **${price} {currency}**
"""
                
                formatted_flights.append(flight_text)
                
            except Exception as e:
                print(f"Error formatting flight {idx}: {e}")
                continue
        
        # Return all formatted flights joined
        if formatted_flights:
            header = f"🛫 **Flight Options from {details.get('departure_city', 'your city')} to {details.get('destination', 'your destination')}**\n\n"
            return header + "\n\n".join(formatted_flights)
        else:
            return "No flight options available at the moment."
    
    def _get_airline_name(self, code):
        """Get full airline name from code (cached for speed)"""
        airline_names = {
            'AA': 'American Airlines', 'UA': 'United Airlines', 'DL': 'Delta Air Lines',
            'BA': 'British Airways', 'AF': 'Air France', 'LH': 'Lufthansa',
            'EK': 'Emirates', 'QR': 'Qatar Airways', 'SQ': 'Singapore Airlines',
            'AI': 'Air India', '6E': 'IndiGo', 'UK': 'Vistara', 'SG': 'SpiceJet',
            'G8': 'Go First', '9W': 'Jet Airways', 'I5': 'AirAsia India',
            'TG': 'Thai Airways', 'CX': 'Cathay Pacific', 'QF': 'Qantas',
            'NZ': 'Air New Zealand', 'JL': 'Japan Airlines', 'NH': 'ANA'
        }
        return airline_names.get(code, code)


