"""
Entity extraction agent for populating semantic memory
"""

from .base_agent import BaseAgent
import json
import re


class EntityExtractorAgent(BaseAgent):
    """
    Extracts structured entities from conversation for memory layer
    """
    
    def __init__(self):
        system_prompt = """You are an entity extraction AI. Extract structured information from travel conversations.

Your job: Identify and extract travel-related entities in JSON format."""
        
        super().__init__("EntityExtractor", system_prompt)
    
    def handle_request(self, input_data):
        """
        Main interface - delegates to extract_entities
        Required by BaseAgent abstract class
        """
        return self.extract_entities(input_data)
    
    def extract_entities(self, conversation_text: str, current_memory: dict = None) -> dict:
        """
        Extract entities from conversation using LLM
        
        Args:
            conversation_text: Full conversation history
            current_memory: Current semantic memory state (what's already known)
        """
        try:
            # Build context about what's already known
            memory_context = ""
            if current_memory:
                known_fields = []
                if current_memory.get("destination"):
                    known_fields.append(f"✅ Destination: {current_memory['destination']}")
                if current_memory.get("departure_city"):
                    known_fields.append(f"✅ Departure city: {current_memory['departure_city']}")
                if current_memory.get("duration"):
                    known_fields.append(f"✅ Duration: {current_memory['duration']}")
                if current_memory.get("budget"):
                    known_fields.append(f"✅ Budget: {current_memory['budget']}")
                if current_memory.get("interests"):
                    known_fields.append(f"✅ Interests: {current_memory['interests']}")
                if current_memory.get("food_preference"):
                    known_fields.append(f"✅ Food preference: {current_memory['food_preference']}")
                if current_memory.get("cuisine_preference"):
                    known_fields.append(f"✅ Cuisine preference: {current_memory['cuisine_preference']}")
                if current_memory.get("travel_dates"):
                    known_fields.append(f"✅ Travel dates: {current_memory['travel_dates']}")
                if current_memory.get("travel_time_preference"):
                    known_fields.append(f"✅ Flight time: {current_memory['travel_time_preference']}")
                
                if known_fields:
                    memory_context = f"\n\n**ALREADY KNOWN (don't overwrite these):**\n" + "\n".join(known_fields)
            
            extraction_prompt = f"""Extract travel information from this conversation:

{conversation_text}{memory_context}

Return ONLY valid JSON with these fields:
{{
    "destination": "city/country or null",
    "departure_city": "city user is flying from or null",
    "duration": "e.g., '5 days', '2 weeks' or null",
    "budget": "e.g., '$20', '$1000' or null",
    "budget_type": "'daily' or 'total' or null",
    "interests": ["beach", "culture", etc.] or [],
    "food_preference": "'vegetarian', 'non-vegetarian', 'vegan', 'any' or null",
    "cuisine_preference": "'Indian', 'Chinese', 'Japanese', 'Thai', 'Italian', 'Local cuisine', 'Any' or null",
    "travel_dates": "e.g., '2025-12-25 to 2025-12-30', 'Jan 15 to Jan 20', 'starting March 1' or null",
    "travel_time_preference": "'morning', 'afternoon', 'evening', 'anytime' or null",
    "companions": "'solo', 'couple', 'family', 'friends' or null"
}}

CRITICAL Rules for CONTEXT AWARENESS:
1. **NEVER OVERWRITE ALREADY KNOWN FIELDS** - If a field is marked as "ALREADY KNOWN" above, YOU MUST return null for it. This is NON-NEGOTIABLE!
   Example: If destination is ALREADY KNOWN as "Delhi", and user says "Tokyo", DO NOT change destination to Tokyo!
2. **Look at what the assistant JUST asked:**
   - If assistant asked "Where do you want to go?" → Next city = destination
   - If assistant asked "Where are you flying from?" → Next city = departure_city (NOT destination)
   - If assistant asked "When do you want to travel?" → Next answer = travel_dates
   - If assistant asked "What time do you prefer to fly?" → Next answer = travel_time_preference
   - If assistant asked "Food preference?" → Next answer = food_preference (Vegetarian/Non-vegetarian/Vegan/Any)
   - If assistant asked "Preferred cuisine?" → Next answer = cuisine_preference (Indian/Chinese/Japanese/Thai/etc.)
3. **Smart city detection - CRITICAL ORDER:**
   - If destination is ALREADY SET → Return null for destination (DON'T CHANGE IT!)
   - If destination is NOT set yet and user mentions a city → That's the destination (FIRST PRIORITY)
   - If destination is ALREADY SET and user mentions a city → That's the departure_city
   - DEFAULT: When in doubt, if it's early in conversation and only ONE city mentioned → It's the destination
4. **Only extract NEW information** from the latest user message
5. Use null for missing information
6. If user updates info (e.g., changes budget), return the NEW value

ABSOLUTE RULE: NEVER overwrite destination if it's already known! If user provides another city after destination is set, that city is departure_city!

RESPOND WITH ONLY THE JSON OBJECT."""

            llm_response = self._call_llm(extraction_prompt)
            
            # Clean and parse JSON
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON if LLM added extra text
            if '{' in clean_response:
                start_idx = clean_response.index('{')
                end_idx = clean_response.rindex('}') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            entities = json.loads(clean_response)
            
            return entities
            
        except Exception as e:
            print(f"Entity extraction error: {str(e)}")
            # Fallback to basic regex extraction
            return self._fallback_extraction(conversation_text)
    
    def _fallback_extraction(self, text: str) -> dict:
        """
        Regex-based fallback if LLM extraction fails
        """
        text_lower = text.lower()
        
        entities = {
            "destination": None,
            "departure_city": None,
            "duration": None,
            "budget": None,
            "budget_type": None,
            "interests": [],
            "food_preference": None,
            "cuisine_preference": None,
            "travel_dates": None,
            "companions": None
        }
        
        # Extract budget
        budget_patterns = [
            r'\$(\d+)\s*(?:per\s+day|daily|/day)',
            r'(\d+)\s+dollars?\s+(?:per\s+day|daily|/day)',
            r'\$(\d+)',
            r'(\d+)\s+dollars?'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities["budget"] = f"${match.group(1)}"
                if 'per day' in text_lower or 'daily' in text_lower or '/day' in text_lower:
                    entities["budget_type"] = "daily"
                else:
                    entities["budget_type"] = "total"
                break
        
        # Extract duration
        duration_pattern = r'(\d+)\s+(day|week|month)s?'
        duration_match = re.search(duration_pattern, text_lower)
        if duration_match:
            entities["duration"] = f"{duration_match.group(1)} {duration_match.group(2)}s"
        
        # Extract interests (simple keyword matching)
        interest_keywords = ['beach', 'culture', 'adventure', 'food', 'shopping', 
                            'nightlife', 'nature', 'hiking', 'diving', 'surfing',
                            'museum', 'temple', 'party', 'relax']
        
        for keyword in interest_keywords:
            if keyword in text_lower:
                entities["interests"].append(keyword.capitalize())
        
        return entities
