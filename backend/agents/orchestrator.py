from .base_agent import BaseAgent
from .destination import DestinationAgent
from .stays import StaysAgent
from .budget import BudgetAgent
from .weather import WeatherAgent
from .activities import ActivitiesAgent
from .itinerary import ItineraryAgent
from .flight import FlightAgent

class OrchestratorAgent(BaseAgent):
    """
    Master coordinator agent that analyzes queries and delegates to specialized agents
    """
    def __init__(self):
        system_prompt = """You are the orchestrator AI agent for a travel planning system. Your role is to:
1. Check if the user has provided complete information (destination, duration, budget, interests)
2. If information is missing, ask clarifying questions in a friendly, conversational way
3. Once you have enough info, delegate to specialized agents

When information is INCOMPLETE, respond with JSON:
{
    "needs_clarification": true,
    "questions": ["What's your destination?", "How many days?", "Budget range?", "Interests?"],
    "message": "friendly conversational message asking for details"
}

When information is COMPLETE, respond with JSON:
{
    "needs_clarification": false,
    "activate_destination": true/false,
    "activate_stays": true/false,
    "activate_activities": true/false,
    "activate_budget": true/false,
    "activate_weather": true/false
}"""
        
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
    "user_asking_for": "stays/activities/flights/budget_breakdown/general"
}}

Important Rules:
- has_destination: true if ANY location is mentioned (city, country, region)
- has_duration: true if ANY timeframe mentioned (days, weeks, months)
- has_budget: true if ANY budget/price mentioned (daily, total, per night)
- has_interests: true if user mentions ANY interests (beach, culture, adventure, food, nightlife, shopping, etc.)
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
                if not has_duration:
                    questions.append("📅 How many days/weeks?")
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
                        if not has_duration:
                            questions.append("📅 How many days/weeks?")
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
            if not has_duration:
                questions.append("📅 How many days/weeks?")
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
                
                print(f"Memory check - Destination:{has_destination}, DepartureCity:{has_departure_city}, Duration:{has_duration}, Budget:{has_budget}, Interests:{has_interests}, FoodPref:{has_food_pref}")
                
                # Check if we have complete info (including departure city and food preference)
                has_complete_info = has_destination and has_departure_city and has_duration and has_budget and has_interests and has_food_pref
                
                # If missing any required info, ask for it
                if not has_complete_info:
                    questions = []
                    if not has_destination:
                        questions.append("📍 Where do you want to go?")
                    if not has_departure_city:
                        questions.append("🛫 Where are you flying from? (your departure city)")
                    if not has_duration:
                        questions.append("📅 How many days/weeks?")
                    if not has_budget:
                        questions.append("💰 What's your budget per day?")
                    if not has_interests:
                        questions.append("🎯 What are you interested in? (beach, culture, adventure, food, etc.)")
                    if not has_food_pref:
                        questions.append("🍽️ Food preference? (Vegetarian/Non-vegetarian/Vegan/Any)")
                    
                    return {
                        "needs_clarification": True,
                        "message": "Great! Just need a bit more info to give you the best recommendations:",
                        "questions": questions
                    }
                
                # All info available - show recommendations
                print("Complete info available - activating agents")
                combined_result = {
                    "needs_clarification": False
                }
                
                # Order: Flights → Stays → Itinerary → Activities (local places needing booking)
                
                # 1. Activate flight agent first
                print("Activating FlightAgent...")
                combined_result["flights"] = self.flight_agent.handle_request(input_data)
                
                # 2. Activate stays agent
                print("Activating StaysAgent...")
                combined_result["stays"] = self.stays_agent.handle_request(input_data)
                
                # 3. Activate itinerary agent
                print("Activating ItineraryAgent...")
                combined_result["itinerary"] = self.itinerary_agent.handle_request(input_data)
                
                # 4. Activate activities agent (local places that need booking)
                print("Activating ActivitiesAgent...")
                combined_result["activities"] = self.activities_agent.handle_request(input_data)
                
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
