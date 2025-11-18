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
    
    def extract_entities(self, conversation_text: str) -> dict:
        """
        Extract entities from conversation using LLM
        """
        try:
            extraction_prompt = f"""Extract travel information from this conversation:

{conversation_text}

Return ONLY valid JSON with these fields:
{{
    "destination": "city/country or null",
    "departure_city": "city user is flying from or null",
    "duration": "e.g., '5 days', '2 weeks' or null",
    "budget": "e.g., '$20', '$1000' or null",
    "budget_type": "'daily' or 'total' or null",
    "interests": ["beach", "culture", etc.] or [],
    "food_preference": "'vegetarian', 'non-vegetarian', 'vegan', 'any' or null",
    "travel_dates": "if mentioned, or null",
    "companions": "'solo', 'couple', 'family', 'friends' or null"
}}

CRITICAL Rules:
- Extract ONLY what's explicitly mentioned
- Use null for missing information
- budget_type: 'daily' if "per day" mentioned, 'total' otherwise
- interests: extract ALL mentioned activities/preferences
- food_preference: extract if user mentions veg/non-veg/vegan preferences
- departure_city: Look at the CONTEXT! If the assistant JUST asked "Where are you flying from?" and user responds with a city name, that's the departure_city
- If destination is already set and user mentions another city, that's likely the departure_city
- If user updates info (e.g., changes budget), return the NEW value

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
