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
            # FAST PATH: Try regex extraction first for simple patterns (instant, no LLM call)
            # Get last user message for quick pattern matching
            lines = conversation_text.strip().split('\n')
            last_user_message = ""
            for line in reversed(lines):
                if line.startswith("User:"):
                    last_user_message = line.replace("User:", "").strip()
                    break
            
            if last_user_message:
                # Try fast regex extraction for common patterns
                quick_extract = self._quick_extract(last_user_message, current_memory)
                if quick_extract.get("_fast_path_success"):
                    # Regex found a clear match - skip expensive LLM call
                    print(f"⚡ FAST EXTRACT: Skipped LLM, used regex for '{last_user_message[:50]}'")
                    del quick_extract["_fast_path_success"]  # Remove internal flag
                    return quick_extract
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
                if current_memory.get("flight_time_preference"):
                    known_fields.append(f"✅ Flight time: {current_memory['flight_time_preference']}")
                
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
    "flight_time_preference": "'morning', 'afternoon', 'evening', 'anytime' or null",
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
   - If assistant asked "What time do you prefer to fly?" → Next answer = flight_time_preference
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
    
    def _quick_extract(self, text: str, current_memory: dict = None) -> dict:
        """
        FAST regex-based extraction for simple, unambiguous inputs
        Returns dict with "_fast_path_success": True if confident match found
        """
        text_lower = text.lower().strip()
        
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
            "flight_time_preference": None,
            "companions": None,
            "dietary_preference": [],  # Array for orchestrator compatibility
            "_fast_path_success": False  # Flag to indicate if we found a clear match
        }
        
        # Pattern 1: Budget (e.g., "$100/day", "$1000", "100 dollars per day")
        budget_match = re.search(r'\$(\d+)\s*(?:/day|per\s+day)?', text_lower)
        if budget_match and len(text_lower) < 20:  # Simple budget response
            entities["budget"] = f"${budget_match.group(1)}/day" if '/day' in text_lower or 'per day' in text_lower else f"${budget_match.group(1)}"
            entities["budget_type"] = "daily" if '/day' in text_lower or 'per day' in text_lower else "total"
            entities["_fast_path_success"] = True
            return entities
        
        # Pattern 2: Date range (e.g., "Dec 8, 2025 to Dec 10, 2025")
        date_match = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+,?\s+\d{4}\s+to\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+,?\s+\d{4}', text_lower)
        if date_match:
            entities["travel_dates"] = date_match.group(0).title()
            entities["duration"] = date_match.group(0).title()
            entities["_fast_path_success"] = True
            return entities
        
        # Pattern 3: Simple city/country names (look for capitalized words)
        # PRIORITY: Check this BEFORE interests pattern
        # More flexible pattern to handle "Dubai, UAE", "Tokyo, Japan", "New York", etc.
        city_pattern = r'^[A-Z][a-zA-Z\s\-]+(?:,\s*[A-Z][a-zA-Z\s\-]+)?$'
        
        # Check if text matches city pattern (even without current_memory)
        if re.match(city_pattern, text.strip()):
            # If no destination yet, assume this is destination
            if not current_memory or not current_memory.get("destination"):
                entities["destination"] = text.strip()
                entities["_fast_path_success"] = True
                return entities
            # If we have destination but no departure city, this is departure
            elif current_memory.get("destination") and not current_memory.get("departure_city"):
                entities["departure_city"] = text.strip()
                entities["_fast_path_success"] = True
                return entities
        
        # Pattern 4: Interests list (comma-separated, e.g., "Food, Shopping, Nightlife")  
        # Only match if it has MULTIPLE items (at least 2 commas or clear interest words)
        if ',' in text and current_memory and not current_memory.get("interests"):
            # Skip if it looks like a city (e.g., "Dubai, UAE" has only 1 comma)
            if text.count(',') == 1 and re.match(city_pattern, text.strip()):
                pass  # This is a city, not interests
            else:
                interest_candidates = [i.strip().title() for i in text.split(',')]
                if all(len(i) < 20 and i.isalpha() or ' ' in i for i in interest_candidates):
                    entities["interests"] = interest_candidates
                    entities["_fast_path_success"] = True
                    return entities
        
        # Pattern 5: Food/Dietary preferences
        # Note: We set BOTH food_preference (single) and dietary_preference (array) for compatibility
        food_prefs = {'vegetarian': 'Vegetarian', 'vegan': 'Vegan', 'non-vegetarian': 'Non-Vegetarian', 
                      'kosher': 'Kosher', 'gluten-free': 'Gluten-Free', 'lactose-free': 'Lactose-Free',
                      'no restrictions': 'No Restrictions', 'any': 'No Restrictions'}
        for key, val in food_prefs.items():
            if key in text_lower and len(text_lower) < 30:
                entities["food_preference"] = val  # Single value for backward compatibility
                entities["dietary_preference"] = [val]  # Array for orchestrator
                entities["_fast_path_success"] = True
                return entities
        
        # Pattern 6: Travel companions
        companions = {'solo': 'solo', 'couple': 'couple', 'family': 'family', 'friends': 'friends'}
        for key, val in companions.items():
            if key in text_lower and len(text_lower) < 30:
                entities["companions"] = val
                entities["_fast_path_success"] = True
                return entities
        
        # Pattern 7: Flight time preferences
        flight_time_map = {
            'morning': 'Morning (6 AM - 12 PM)',
            'afternoon': 'Afternoon (12 PM - 5 PM)',
            'evening': 'Evening (5 PM - 10 PM)',
            'night': 'Red-Eye/Night (10 PM - 6 AM)',
            'red-eye': 'Red-Eye/Night (10 PM - 6 AM)',
            'anytime': 'Anytime (No Preference)',
            'no preference': 'Anytime (No Preference)',
            'any time': 'Anytime (No Preference)'
        }
        for key, val in flight_time_map.items():
            if key in text_lower and len(text_lower) < 50:
                entities["flight_time_preference"] = val
                entities["_fast_path_success"] = True
                return entities
        
        # No clear match - return with _fast_path_success = False (will fall back to LLM)
        return entities
    
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
