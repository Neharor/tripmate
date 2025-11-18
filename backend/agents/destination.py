from .base_agent import BaseAgent
import json

class DestinationAgent(BaseAgent):
    """
    Specialized agent for recommending travel destinations.
    Uses Groq AI for fast, personalized destination suggestions.
    """
    def __init__(self):
        system_prompt = """You are a destination expert. Your ONLY job: recommend travel DESTINATIONS (cities/countries).

DO NOT mention flights, hotels, or prices. ONLY destination names and why they're great.

Keep it super short - 1 line per destination."""
        
        super().__init__("DestinationAgent", system_prompt)

    def handle_request(self, input_data):
        """
        Process user query and return destination recommendations
        ONLY suggest destinations if user hasn't specified one yet
        """
        try:
            # Check if user already has a specific destination
            analysis_prompt = f"""Analyze this conversation:

{input_data}

Question: Has the user ALREADY mentioned a SPECIFIC destination (city or country)?

Examples of specific destinations: "Bali", "Paris", "Tokyo", "Thailand", "Italy"
NOT destinations: "somewhere warm", "beach destination", "Asia"

Respond with ONLY: YES or NO"""

            analysis_response = self._call_llm(analysis_prompt)
            
            # If user already specified destination, just acknowledge it
            if "YES" in analysis_response.upper():
                # Extract the destination name
                extract_prompt = f"""From this conversation, what is the destination the user wants to visit?

{input_data}

Respond with ONLY the destination name (e.g., "Bali", "Paris", "Tokyo")"""
                
                destination = self._call_llm(extract_prompt).strip()
                
                return {
                    "plan": [f"Perfect! Let's plan your trip to {destination} 🌴"]
                }
            
            # User needs destination suggestions - they haven't specified one
            user_prompt = f"""The user needs destination suggestions based on:

{input_data}

Suggest 3 destinations that match their budget, duration, and interests.

Format (one per line):
🌴 [City/Country] - [Why it's perfect for them in 8 words max]

CRITICAL:
- Match their interests and budget
- Keep descriptions under 8 words
- ONLY destination names and reasons
- NO hotels, NO flights, NO prices"""

            llm_response = self._call_llm(user_prompt)
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            return {
                "plan": [clean_response]
            }
            
        except Exception as e:
            print(f"DestinationAgent error: {str(e)}")
            return {
                "plan": [f"Error getting destinations: {str(e)}"]
            }
