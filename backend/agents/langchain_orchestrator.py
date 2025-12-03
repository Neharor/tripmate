"""
LangChain-Powered Orchestrator for TripMate
Uses LangChain's agent framework for intelligent tool selection and coordination
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
import json

from .destination import DestinationAgent
from .stays import StaysAgent
from .activities import ActivitiesAgent
from .flight import FlightAgent
from .local_events import LocalEventsAgent
from .langchain_tools import create_all_tools

load_dotenv()


class LangChainOrchestrator:
    """
    LangChain-powered orchestrator that intelligently selects and coordinates tools
    """
    
    def __init__(self):
        # Initialize specialized agents
        self.destination_agent = DestinationAgent()
        self.flight_agent = FlightAgent()
        self.stays_agent = StaysAgent()
        self.activities_agent = ActivitiesAgent()
        self.local_events_agent = LocalEventsAgent()
        
        # Create LangChain tools from agents
        self.tools = create_all_tools(
            self.flight_agent,
            self.stays_agent,
            self.activities_agent,
            self.destination_agent,
            self.local_events_agent
        )
        
        # Initialize LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",  # Faster model with much higher rate limits
            groq_api_key=api_key,
            temperature=0.3,
            max_tokens=2000,
            timeout=30
        )
        
        # Create React agent prompt
        self.prompt = PromptTemplate.from_template("""You are TripMate AI, an intelligent travel planning assistant.

You have access to the following tools:

{tools}

Tool Names: {tool_names}

Your mission: Help users plan personalized trips by intelligently using the available tools.

GUIDELINES:
1. ANALYZE the user's query to understand what they need
2. If destination is not specified, use SuggestDestinations tool
3. For flight queries, use SearchFlights tool
4. For accommodation queries, use SearchHotels tool  
5. For activity queries, use ActivityRecommender tool
6. For local events/festivals during trip dates, use LocalEventsDiscoverer tool (UNIQUE FEATURE)

CRITICAL: When creating a COMPLETE trip itinerary, you MUST use ALL of these tools:
   - FlightPlanner (find flights from departure city to destination)
   - HotelPlanner (find accommodations in destination)
   - ActivityRecommender (find activities matching user interests)
   - LocalEventsDiscoverer (find events during travel dates)

DO NOT skip any of these tools when creating a full trip plan. Users expect flights, hotels, activities, AND events.

After collecting ALL the information, create a comprehensive day-by-day itinerary in your Final Answer that includes:
   - Flight details and recommendations
   - Hotel recommendations with prices
   - Day-by-day activity plan formatted as:
     **Day 1 (Date):**
     - Morning: [activity]
     - Afternoon: [activity]
     - Evening: [activity]
     
     **Day 2 (Date):**
     - Morning: [activity]
     - Afternoon: [activity]
     - Evening: [activity]
   - Local events happening during the trip
   - Budget breakdown
   
Format your Final Answer as a detailed, well-structured itinerary text with clear day-by-day sections.

INFORMATION GATHERING:
- If user hasn't specified destination, budget, or interests, ask for these details first
- Don't make assumptions about missing information
- Be conversational and helpful

Use the following format:

Question: the input question you must answer
Thought: think about what information you need and which tools to use
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""")
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=25,  # Increased to allow for flights, hotels, activities, events, AND final answer
            max_execution_time=180  # 3 minutes timeout for complete itinerary generation
        )
    
    def handle_request(self, input_data, memory=None):
        """
        Process user query using LangChain agent framework
        
        Args:
            input_data: User query with conversation context
            memory: ConversationMemory object (optional)
        
        Returns:
            dict: Orchestrated response from multiple agents
        """
        try:
            print(f"\n🤖 LangChain Orchestrator processing: {input_data[:100]}...")
            
            # Check if we have enough information to plan a trip
            if memory:
                missing_info = self._check_missing_information(memory)
                if missing_info:
                    print(f"⚠️ Missing information: {missing_info}")
                    return self._ask_for_missing_info(missing_info, memory)
            
            # If memory is provided, extract entities for context
            context = ""
            if memory:
                entities = memory.entities
                if entities.get("destination"):
                    context += f"\nDestination: {entities['destination']}"
                if entities.get("budget"):
                    context += f"\nBudget: {entities['budget']}"
                if entities.get("interests"):
                    context += f"\nInterests: {', '.join(entities['interests'])}"
                if entities.get("travel_dates"):
                    context += f"\nTravel Dates: {entities['travel_dates']}"
                if entities.get("departure_city"):
                    context += f"\nDeparture City: {entities['departure_city']}"
                if entities.get("duration"):
                    context += f"\nDuration: {entities['duration']}"
            
            # Combine input with context
            full_input = f"{input_data}\n{context}" if context else input_data
            
            # Run the agent
            result = self.agent_executor.invoke({"input": full_input})
            
            # Parse the result
            final_answer = result.get("output", "")
            
            # Format the response with itinerary structure for frontend
            return {
                "needs_clarification": False,
                "message": final_answer,
                "agent_type": "langchain_orchestrator",
                "itinerary": {
                    "itinerary_text": final_answer  # This is the day-by-day plan text
                }
            }
            
        except Exception as e:
            print(f"❌ LangChain Orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to direct agent calls
            return self._fallback_direct_calls(input_data, memory)
    
    def _check_missing_information(self, memory):
        """
        Check what information is still needed to plan a complete trip
        Also validates duration limits
        
        Returns:
            list: Missing information fields
        """
        entities = memory.entities
        missing = []
        
        # Core requirements for trip planning IN ORDER
        if not entities.get("destination"):
            missing.append("destination")
            return missing  # Stop here, ask for destination first
        
        # FIRST ask for departure city right after destination
        if not entities.get("departure_city"):
            missing.append("departure_city")
            return missing  # Stop here, ask for departure city next
        
        # THEN ask for duration (with validation)
        if not entities.get("duration"):
            missing.append("duration")
            return missing
        else:
            # Validate duration is not too long
            duration_str = entities.get("duration", "")
            days = self._extract_days_from_duration(duration_str)
            if days and days > 90:
                missing.append("duration_too_long")
                return missing
        
        # THEN ask for budget
        if not entities.get("budget"):
            missing.append("budget")
            return missing
        
        # THEN ask for interests (activities)
        if not entities.get("interests") or len(entities.get("interests", [])) == 0:
            missing.append("interests")
            return missing
        
        # THEN ask for food preference
        if not entities.get("food_preference"):
            missing.append("food_preference")
            return missing
        
        # FINALLY ask for cuisine preference
        if not entities.get("cuisine_preference"):
            missing.append("cuisine_preference")
        
        return missing
    
    def _extract_days_from_duration(self, duration_str):
        """Extract number of days from duration string or date range"""
        if not duration_str:
            return None
        
        import re
        from datetime import datetime
        
        # Try to extract from "X days" format
        match = re.search(r'(\d+)\s*days?', duration_str.lower())
        if match:
            return int(match.group(1))
        
        # Try to extract from date range "Dec 1, 2025 to Oct 1, 2026"
        if ' to ' in duration_str:
            try:
                parts = duration_str.split(' to ')
                if len(parts) == 2:
                    # Try different date formats
                    for fmt in ['%b %d, %Y', '%Y-%m-%d', '%m/%d/%Y']:
                        try:
                            start = datetime.strptime(parts[0].strip(), fmt)
                            end = datetime.strptime(parts[1].strip(), fmt)
                            days = (end - start).days
                            return days
                        except:
                            continue
            except:
                pass
        
        return None
    
    def _ask_for_missing_info(self, missing_info, memory):
        """
        Generate a conversational response asking for missing information
        
        Args:
            missing_info: List of missing fields
            memory: ConversationMemory object
        
        Returns:
            dict: Response asking for clarification
        """
        entities = memory.entities
        
        # Build personalized follow-up with form field suggestions
        # ORDER: 1. Destination → 2. Departure City → 3. Duration → 4. Budget
        
        if "destination" in missing_info:
            return {
                "needs_clarification": True,
                "message": "I'd love to help you plan a trip! 🌍\n\nWhere would you like to go?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "destination": {
                        "type": "autocomplete",
                        "label": "Destination",
                        "placeholder": "e.g., Paris, Tokyo, Bali"
                    }
                }
            }
        
        if "departure_city" in missing_info:
            dest = entities.get("destination", "there")
            return {
                "needs_clarification": True,
                "message": f"Great choice - {dest}! 🛫\n\nWhere will you be flying from?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "departure_city": {
                        "type": "autocomplete",
                        "label": "Departure City",
                        "placeholder": "e.g., New York, London, Mumbai, Delhi"
                    }
                }
            }
        
        if "duration" in missing_info:
            dest = entities.get("destination", "there")
            departure = entities.get("departure_city", "")
            route_msg = f"{departure} to {dest}" if departure else dest
            return {
                "needs_clarification": True,
                "message": f"Perfect! Planning your trip from {route_msg}! ✈️\n\nHow long do you want to stay?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "duration": {
                        "type": "number",
                        "label": "Trip Duration (days)",
                        "min": 1,
                        "max": 90,
                        "default": 5
                    },
                    "travel_dates": {
                        "type": "daterange",
                        "label": "Travel Dates (optional)",
                        "placeholder": "Select dates"
                    }
                }
            }
        
        if "budget" in missing_info:
            dest = entities.get("destination", "there")
            duration = entities.get("duration", "your trip")
            return {
                "needs_clarification": True,
                "message": f"Awesome! {dest} for {duration} 🎯\n\nWhat's your budget?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "budget": {
                        "type": "slider",
                        "label": "Daily Budget ($)",
                        "min": 20,
                        "max": 1000,
                        "step": 10,
                        "default": 100
                    }
                }
            }
        
        # Ask for food preference (only after budget is set)
        if "food_preference" in missing_info:
            return {
                "needs_clarification": True,
                "message": "Great! 🍽️\n\nWhat's your food preference?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "food_preference": {
                        "type": "select",
                        "label": "Food Preference",
                        "options": ["Any", "Vegetarian", "Non-vegetarian", "Vegan"],
                        "default": "Any"
                    }
                }
            }
        
        # Ask for interests/activities (only after budget is set)
        if "interests" in missing_info:
            return {
                "needs_clarification": True,
                "message": "Awesome! 🎯\n\nWhat kind of activities and experiences are you interested in? (Select all that apply)",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "interests": {
                        "type": "multi-select",
                        "label": "Interests & Activities",
                        "options": [
                            "Beach", "Culture", "Adventure", "Food", "Shopping", 
                            "Nightlife", "Nature", "History", "Relaxation", 
                            "Photography", "Wildlife", "Spirituality"
                        ],
                        "default": []
                    }
                }
            }
        
        # Ask for cuisine preference (only after food preference is set)
        if "cuisine_preference" in missing_info:
            return {
                "needs_clarification": True,
                "message": "Perfect! 🍜\n\nWhat type of cuisine would you like to explore?",
                "missing_fields": missing_info,
                "show_form_fields": {
                    "cuisine_preference": {
                        "type": "select",
                        "label": "Cuisine Preference",
                        "options": ["Any", "Indian", "Chinese", "Japanese", "Thai", "Italian", "Local cuisine"],
                        "default": "Any"
                    }
                }
            }

        
        # Default fallback
        return {
            "needs_clarification": True,
            "message": "I need a bit more information to plan your perfect trip. Could you tell me more about what you're looking for?",
            "missing_fields": missing_info
        }
    
    def _fallback_direct_calls(self, input_data, memory=None):
        """
        Fallback method: directly call agents without LangChain orchestration
        """
        print("⚠️ Falling back to direct agent calls")
        
        combined_result = {
            "needs_clarification": False,
            "message": "Let me help you plan your trip! Here are my recommendations:"
        }
        
        try:
            # Call agents sequentially
            import time
            
            combined_result["flights"] = self.flight_agent.handle_request(input_data)
            time.sleep(0.5)
            
            combined_result["stays"] = self.stays_agent.handle_request(input_data)
            time.sleep(0.5)
            
            combined_result["activities"] = self.activities_agent.handle_request(input_data)
            time.sleep(0.5)
            
            combined_result["local_events"] = self.local_events_agent.handle_request(input_data)
            time.sleep(0.5)
            
            combined_result["destinations"] = self.destination_agent.handle_request(input_data)
            
        except Exception as e:
            print(f"Error in fallback: {str(e)}")
        
        return combined_result
