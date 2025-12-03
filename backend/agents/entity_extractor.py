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
    "travel_dates": "MUST include year! e.g., 'Dec 15, 2025 to Dec 20, 2025', '2025-12-25 to 2025-12-30', or null",
    "travel_time_preference": "'morning', 'afternoon', 'evening', 'anytime' or null",
    "companions": "'solo', 'couple', 'family', 'friends' or null"
}}

CRITICAL Rules for CONTEXT AWARENESS:
1. **DETECTING EXPLICIT CHANGES (user wants to UPDATE existing info):**
   - Phrases like "actually", "instead", "change to", "I meant", "correction", "no wait" = USER IS UPDATING
   - Example: "actually 7 days" → UPDATE duration (even if duration already set)
   - Example: "change destination to Tokyo" → UPDATE destination to Tokyo
   - Example: "I meant $50 per day" → UPDATE budget
   - When you detect explicit change phrases, return the NEW value in JSON (this will REPLACE old value)

2. **DESTINATION UPDATE LOGIC:**
   - If user explicitly says "change destination to X" or "I want to go to X instead" → UPDATE destination to X
   - If destination is already known and user mentions a NEW city WITHOUT context → That's departure_city
   - If user says "from X to Y" → X is departure_city, Y is destination
   - Look at conversation flow to determine if user is CHANGING destination or ADDING departure city

3. **Look at what the assistant JUST asked:**
   - If assistant asked "Where do you want to go?" → Next city = destination
   - If assistant asked "Where are you flying from?" → Next city = departure_city (NOT destination)
   - If assistant asked "When do you want to travel?" → Next answer = travel_dates (MUST include year: "Dec 15, 2025 to Dec 20, 2025")
   - If assistant asked "What time do you prefer to fly?" → Next answer = travel_time_preference
   - If assistant asked "Food preference?" → Next answer = food_preference (Vegetarian/Non-vegetarian/Vegan/Any)
   - If assistant asked "Preferred cuisine?" → Next answer = cuisine_preference (Indian/Chinese/Japanese/Thai/etc.)

4. **Smart city detection:**
   - First city mentioned in conversation → destination
   - Second city mentioned → departure_city (unless user is clearly changing destination)
   - If user says "actually, I want to go to X" or "change to X" → UPDATE destination

5. **Date format MUST include year:**
   - Always extract dates with full year: "Jan 15, 2025 to Jan 20, 2025" or "2025-01-15 to 2025-01-20"
   - If user says "Dec 15 to Dec 20" → Add current year (2025): "Dec 15, 2025 to Dec 20, 2025"

6. **Only extract NEW information** from the latest user message
7. Use null for missing information
8. **CRITICAL: Explicit changes override existing values**
   - If user uses change phrases ("actually", "instead", "change to"), ALWAYS return the NEW value
   - This signals to the system to REPLACE the old value, not ignore it

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
