from .base_agent import BaseAgent
from .destination import DestinationAgent
from .stays import StaysAgent
from .budget import BudgetAgent
from .weather import WeatherAgent
from .activities import ActivitiesAgent
from .itinerary import ItineraryAgent
from .flight import FlightAgent
import concurrent.futures  # For parallel agent execution

class OrchestratorAgent(BaseAgent):
    """
    Master coordinator agent that analyzes queries and delegates to specialized agents
    """
    def __init__(self):
        system_prompt = """You are TripMate AI, a next-generation multi-agent travel orchestrator.

Your role: Analyze user queries intelligently and coordinate specialized agents to generate realistic, structured, personalized travel plans.

🎯 CORE PRINCIPLES:

1️⃣ ASK FEWER, SMARTER QUESTIONS
- Analyze previous conversation history BEFORE asking
- NEVER ask repetitive questions
- Detect missing info: destination, departure city, dates, duration, budget, interests, food preference, flight time preference
- Ask ONLY what's genuinely missing in a single batch

2️⃣ INTELLIGENT INTENT DETECTION
- If user says "Bali" → destination detected, ask for duration/budget/dates
- If user says "5 days" → duration detected, ask for destination/budget
- If user says "$100/day" → budget detected, continue
- If user says "Adventure + Food" → interests detected
- If user says "Jan 15 to Jan 20" → dates detected
- If user provides COMPLETE info → activate all agents immediately

3️⃣ AGENT COORDINATION PRIORITY
When ALL info is available, activate agents in this order:
1. FlightAgent → Real flight search (3 options: cheapest, fastest, optimal)
2. StaysAgent → Hotels filtered by budget, neighborhood, style
3. ItineraryAgent → Time-optimized, weather-aware, realistic schedules
4. ActivitiesAgent → Curated experiences matching interests

4️⃣ RESPONSE STRUCTURE (when complete info available):
{
    "needs_clarification": false,
    "flights": {...},        // 3 flight options with realistic prices
    "stays": {...},          // 3-5 hotels with price/neighborhood/why it fits
    "itinerary": {...},      // Day-by-day with times, activities, food, travel gaps
    "activities": {...}      // Curated activities matching interests
}

5️⃣ CLARIFICATION RESPONSE (when info missing):
{
    "needs_clarification": true,
    "message": "Great! To create your perfect trip, I need:",
    "questions": ["📍 Destination?", "🛫 Departure city?", "📆 Travel dates?", "⏰ Flight time preference?"]
}

6️⃣ QUALITY STANDARDS
✅ Realistic flight prices (no random numbers)
✅ Time-optimized itineraries (no impossible travel gaps)
✅ Weather-aware scheduling (outdoor activities on good weather days)
✅ Budget-aware filtering (hotels/activities match user's budget)
✅ Interest-based curation (if "Adventure + Food" → prioritize those)
✅ Food preference filtering (if Vegetarian → no non-veg restaurants)

7️⃣ TONE & FORMATTING
- Professional yet friendly
- Use emojis sparingly (1-2 per section)
- Clean, structured output
- No hallucinated data

8️⃣ REQUIRED INFO CHECKLIST
Before activating agents, ensure you have:
✓ Destination (where)
✓ Departure city (from where)
✓ Travel dates (when - specific dates or "starting X")
✓ Duration (how many days)
✓ Budget (per day or total)
✓ Interests (what activities)
✓ Food preference (dietary restrictions)
✓ Flight time preference (morning/afternoon/evening/anytime)

If ANY is missing → ask in ONE question batch, don't repeat."""
        
        super().__init__("OrchestratorAgent", system_prompt)
        
        # Initialize all specialized agents
        self.destination_agent = DestinationAgent()
        self.stays_agent = StaysAgent()
        self.activities_agent = ActivitiesAgent()
        self.budget_agent = BudgetAgent()
        self.weather_agent = WeatherAgent()
        self.itinerary_agent = ItineraryAgent()
        self.flight_agent = FlightAgent()

    def _analyze_intent(self, user_query):
        """
        Use LLM to analyze query and determine what information is available
        """
        try:
            # Ask LLM to analyze the conversation
            analysis_prompt = f"""Analyze this travel planning conversation:

{user_query}

Extract the following information and respond ONLY in valid JSON format (no extra text):
{{
    "has_destination": true/false,
    "destination": "city/country name or null",
    "has_duration": true/false,
    "duration": "duration mentioned or null",
    "has_budget": true/false,
    "budget": "budget amount or null",
    "has_interests": true/false,
    "interests": "interests mentioned or null",
    "has_food_pref": true/false,
    "food_pref": "vegetarian/vegan/non-vegetarian or null",
    "has_cuisine_pref": true/false,
    "cuisine_pref": "Indian/Chinese/Japanese/Thai/Italian/Local or null",
    "user_asking_for": "stays/activities/flights/budget_breakdown/general"
}}

Important Rules:
- has_destination: true if ANY location is mentioned (city, country, region)
- has_duration: true if ANY timeframe mentioned (days, weeks, months)
- has_budget: true if ANY budget/price mentioned (daily, total, per night)
- has_interests: true if user mentions ANY interests (beach, culture, adventure, food, nightlife, shopping, etc.)
- has_food_pref: true if dietary restriction mentioned (vegetarian, vegan, non-veg)
- has_cuisine_pref: true if specific cuisine mentioned (Indian food, Japanese, Thai, Chinese, Italian, Local food)
- user_asking_for:
  * "stays" if user ASKS a question about hotels/accommodation ("where should I stay?", "recommend hotels")
  * "activities" if user ASKS about things to do/tours ("what can I do?", "show me activities")
  * "flights" if user ASKS about plane tickets ("how do I get there?", "find flights")
  * "budget_breakdown" ONLY if user ASKS "what will it cost?", "give me a breakdown", "how much total?"
  * "general" if user is just PROVIDING information without asking a question ("20 dollars", "5 days", "my budget is X")

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

            llm_response = self._call_llm(analysis_prompt)
            
            # Parse LLM response
            import json
            # Clean response - remove markdown code blocks if present
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            # Try to extract JSON if LLM added extra text
            if '{' in clean_response:
                start_idx = clean_response.index('{')
                end_idx = clean_response.rindex('}') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            analysis = json.loads(clean_response)
            
            print(f"LLM Analysis: {analysis}")
            
            # Determine if we need clarification
            has_destination = analysis.get("has_destination", False)
            has_duration = analysis.get("has_duration", False)
            has_budget = analysis.get("has_budget", False)
            has_interests = analysis.get("has_interests", False)
            user_asking_for = analysis.get("user_asking_for", "general")
            
            # Check if this is a follow-up (contains "Previous conversation:")
            is_followup = "previous conversation:" in user_query.lower()
            
            # If no destination, must ask for it
            if not has_destination:
                questions = []
                questions.append("📍 Where do you want to go? (e.g., Bali, Paris, Tokyo, anywhere!)")
                if not has_budget:
                    questions.append("💰 What's your budget per day?")
                if not has_interests:
                    questions.append("🎯 What are you interested in? (beach, culture, adventure, food, etc.)")
                
                return {
                    "needs_clarification": True,
                    "message": "Great! I need to know your destination to give you recommendations.",
                    "questions": questions
                }
            
            # Has destination, route based on what user is asking for
            if has_destination and (has_duration or has_budget or is_followup):
                # If user is specifically asking for something (stays, activities), provide it
                # But if just providing info, ask for missing details first
                
                # Check if we have COMPLETE info (destination + duration + budget + interests)
                has_complete_info = has_destination and has_duration and has_budget and has_interests
                
                # Route based on user's specific request
                if user_asking_for == "stays":
                    # User specifically asked for stays - provide them
                    return {
                        "needs_clarification": False,
                        "activate_destination": False,
                        "activate_stays": True,
                        "activate_activities": False,
                        "activate_budget": False,
                        "activate_weather": False
                    }
                elif user_asking_for == "flights":
                    return {
                        "needs_clarification": True,
                        "message": "I can help you plan your trip, but I don't currently book flights. I can help with:",
                        "questions": [
                            "🏨 Accommodations (hotels, hostels, resorts)",
                            "🎯 Local activities and attractions",
                            "💰 Budget planning",
                            "🌍 Destination recommendations"
                        ]
                    }
                elif user_asking_for == "activities":
                    # User specifically asked for activities - provide them
                    return {
                        "needs_clarification": False,
                        "activate_destination": False,
                        "activate_stays": False,
                        "activate_activities": True,
                        "activate_budget": False,
                        "activate_weather": False
                    }
                elif user_asking_for == "budget_breakdown":
                    # User is asking for budget breakdown - activate budget agent only
                    return {
                        "needs_clarification": False,
                        "activate_destination": False,
                        "activate_stays": False,
                        "activate_activities": False,
                        "activate_budget": True,
                        "activate_weather": False
                    }
                else:
                    # User is providing info (general) - check if we have everything
                    if not has_complete_info:
                        # Missing info - ask for it
                        questions = []
                        if not has_budget:
                            questions.append("💰 What's your budget per day?")
                        if not has_interests:
                            questions.append("🎯 What are you interested in? (beach, culture, adventure, food, etc.)")
                        
                        return {
                            "needs_clarification": True,
                            "message": "Great! Just need a bit more info to give you the best recommendations:",
                            "questions": questions
                        }
                    
                    # Have complete info - show recommendations
                    return {
                        "needs_clarification": False,
                        "activate_destination": True,
                        "activate_stays": True,
                        "activate_activities": False,
                        "activate_budget": False,
                        "activate_weather": False
                    }
            
            # Need more information
            questions = []
            if not has_budget:
                questions.append("💰 What's your budget per day?")
            if not has_interests:
                questions.append("🎯 What are you interested in? (beach, culture, adventure, food, etc.)")
            
            return {
                "needs_clarification": True,
                "message": "I'd love to help plan your trip! To give you the best recommendations, I need a few more details:",
                "questions": questions
            }
            
        except Exception as e:
            print(f"LLM analysis error: {str(e)}")
            # Fallback to simple logic if LLM fails
            return {
                "needs_clarification": True,
                "message": "I'd love to help plan your trip! Could you tell me more about your destination, duration, and budget?",
                "questions": [
                    "📍 Where do you want to go?",
                    "📅 How many days?",
                    "💰 What's your budget?"
                ]
            }

    def handle_request(self, input_data, memory=None):
        """
        Coordinate multiple agents based on query analysis
        Uses memory entities directly for more reliable intent detection
        
        Args:
            input_data: User query with conversation context
            memory: ConversationMemory object (optional, falls back to LLM analysis)
        """
        try:
            print(f"\nOrchestrator processing: {input_data[:100]}...")
            
            # Use memory entities if available (more reliable than LLM re-analysis)
            if memory:
                has_destination = bool(memory.entities.get("destination")) and memory.entities.get("destination") != "null"
                has_departure_city = bool(memory.entities.get("departure_city")) and memory.entities.get("departure_city") != "null"
                has_duration = bool(memory.entities.get("duration")) and memory.entities.get("duration") != "null"
                has_budget = bool(memory.entities.get("budget")) and memory.entities.get("budget") != "null"
                has_interests = len(memory.entities.get("interests", [])) > 0
                has_food_pref = bool(memory.entities.get("food_preference")) and memory.entities.get("food_preference") != "null"
                has_travel_dates = bool(memory.entities.get("travel_dates")) and memory.entities.get("travel_dates") != "null"
                has_time_pref = bool(memory.entities.get("travel_time_preference")) and memory.entities.get("travel_time_preference") != "null"
                
                # If travel_dates are provided, calculate duration automatically
                if has_travel_dates and not has_duration:
                    travel_dates = memory.entities.get("travel_dates", "")
                    # Try to calculate duration from dates (e.g., "Nov 20 to Nov 23" = 3 days)
                    if " to " in travel_dates:
                        try:
                            from datetime import datetime
                            parts = travel_dates.split(" to ")
                            if len(parts) == 2:
                                # Simple day calculation (assuming dates are in same month)
                                start_str = parts[0].strip()
                                end_str = parts[1].strip()
                                # Extract day numbers
                                import re
                                start_day = re.search(r'\d+', start_str)
                                end_day = re.search(r'\d+', end_str)
                                if start_day and end_day:
                                    days = int(end_day.group()) - int(start_day.group()) + 1
                                    if days > 0:
                                        memory.update_entity("duration", f"{days} days")
                                        has_duration = True
                                        print(f"Auto-calculated duration from dates: {days} days")
                        except Exception as e:
                            print(f"Could not auto-calculate duration: {e}")
                
                print(f"Memory check - Destination:{has_destination}, DepartureCity:{has_departure_city}, Duration:{has_duration}, Budget:{has_budget}, Interests:{has_interests}, FoodPref:{has_food_pref}, TravelDates:{has_travel_dates}, TimePref:{has_time_pref}")
                
                # Check for cuisine preference
                has_cuisine_pref = bool(memory.entities.get("cuisine_preference"))
                
                # Check if we have complete info (all required fields)
                # Duration is optional if we have travel_dates
                has_complete_info = has_destination and has_departure_city and (has_duration or has_travel_dates) and has_budget and has_interests and has_food_pref and has_cuisine_pref and has_travel_dates and has_time_pref
                
                # If missing any required info, ask for it
                if not has_complete_info:
                    questions = []
                    if not has_destination:
                        questions.append("📍 Where do you want to go?")
                    if not has_departure_city:
                        questions.append("🛫 Where are you flying from? (your departure city)")
                    if not has_travel_dates:
                        questions.append("📆 When do you want to travel? (e.g., 'Jan 15 to Jan 20' or 'starting March 1')")
                    if not has_time_pref:
                        questions.append("⏰ What time do you prefer to fly? (morning/afternoon/evening/anytime)")
                    if not has_budget:
                        questions.append("💰 What's your budget per day?")
                    if not has_interests:
                        questions.append("🎯 What are you interested in? (beach, culture, adventure, food, etc.)")
                    if not has_food_pref:
                        questions.append("🍽️ Food preference? (Vegetarian/Non-vegetarian/Vegan/Any)")
                    
                    # Check for cuisine preference
                    has_cuisine_pref = bool(memory.entities.get("cuisine_preference"))
                    if not has_cuisine_pref:
                        questions.append("🌍 Preferred cuisine? (Local/Indian/Chinese/Japanese/Thai/Italian/Any)")
                    
                    return {
                        "needs_clarification": True,
                        "message": "Great! Just need a bit more info to give you the best recommendations:",
                        "questions": questions
                    }
                
                # All info available - show recommendations
                print("Complete info available - activating agents")
                
                combined_result = {
                    "needs_clarification": False,
                    "message": "Perfect! I have all the details I need. Let me create your personalized itinerary... ✈️🏨"
                }
                
                # SEQUENTIAL EXECUTION with delays to avoid rate limits
                # (Parallel was too fast - hit API rate limits!)
                print("Running agents sequentially to avoid rate limits...")
                
                # 1. Activate flight agent first
                print("Activating FlightAgent...")
                try:
                    combined_result["flights"] = self.flight_agent.handle_request(input_data)
                    print("✅ FlightAgent done")
                except Exception as e:
                    print(f"⚠️ FlightAgent error: {e}")
                    combined_result["flights"] = {"error": "Couldn't fetch flights at the moment"}
                
                # 2. Activate stays agent
                print("Activating StaysAgent...")
                try:
                    combined_result["stays"] = self.stays_agent.handle_request(input_data)
                    print("✅ StaysAgent done")
                except Exception as e:
                    print(f"⚠️ StaysAgent error: {e}")
                    combined_result["stays"] = {"error": "Couldn't fetch accommodations"}
                
                # Small delay to respect rate limits
                import time
                time.sleep(1)
                
                # 3. Activate itinerary agent
                print("Activating ItineraryAgent...")
                try:
                    combined_result["itinerary"] = self.itinerary_agent.handle_request(input_data)
                    print("✅ ItineraryAgent done")
                except Exception as e:
                    print(f"⚠️ ItineraryAgent error: {e}")
                    combined_result["itinerary"] = {"error": "Couldn't generate itinerary"}
                
                # Small delay to respect rate limits
                time.sleep(1)
                
                # 4. Activate activities agent
                print("Activating ActivitiesAgent...")
                try:
                    combined_result["activities"] = self.activities_agent.handle_request(input_data)
                    print("✅ ActivitiesAgent done")
                except Exception as e:
                    print(f"⚠️ ActivitiesAgent error: {e}")
                    combined_result["activities"] = {"error": "Couldn't fetch activities"}
                
                print("🎉 All agents completed!")
                return combined_result
            
            # Fallback: No memory provided, use LLM analysis
            else:
                print("No memory provided, falling back to LLM analysis")
                intent = self._analyze_intent(input_data)
                print(f"Intent analysis: {intent}")
                
                # If needs clarification, return questions to user
                if intent.get("needs_clarification", False):
                    return {
                        "needs_clarification": True,
                        "message": intent.get("message", "Could you provide more details about your trip?"),
                        "questions": intent.get("questions", [])
                    }
                
                # Query is complete, delegate to agents
                combined_result = {
                    "needs_clarification": False,
                    "query_analysis": intent.get("summary", "")
                }
                
                # Delegate to appropriate agents
                if intent.get("activate_destination", True):
                    print("Activating DestinationAgent...")
                    combined_result["destinations"] = self.destination_agent.handle_request(input_data)
                
                if intent.get("activate_stays", True):
                    print("Activating StaysAgent...")
                    combined_result["stays"] = self.stays_agent.handle_request(input_data)
                
                if intent.get("activate_activities", False):
                    print("Activating ActivitiesAgent...")
                    combined_result["activities"] = self.activities_agent.handle_request(input_data)
                
                if intent.get("activate_budget", False):
                    print("Activating BudgetAgent...")
                    combined_result["budget"] = self.budget_agent.handle_request(input_data)
                
                if intent.get("activate_weather", False):
                    print("Activating WeatherAgent...")
                    combined_result["weather"] = self.weather_agent.handle_request(input_data)
                
                return combined_result
            
        except Exception as e:
            print(f"Orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to basic delegation
            return {
                "needs_clarification": False,
                "destinations": self.destination_agent.handle_request(input_data),
                "stays": self.stays_agent.handle_request(input_data)
            }
