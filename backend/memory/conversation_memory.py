"""
Multi-layered memory system for TripMate agentic AI
Implements: Short-term, Long-term, and Semantic memory
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


class ConversationMemory:
    """
    Hybrid memory system with multiple layers:
    1. Short-term memory: Current conversation context (working memory)
    2. Long-term memory: User preferences and trip history
    3. Semantic memory: Extracted entities and structured knowledge
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        
        # SHORT-TERM MEMORY: Recent conversation turns (last 5-10 exchanges)
        self.short_term = []
        self.max_short_term = 10
        
        # SEMANTIC MEMORY: Extracted structured entities
        self.entities = {
            "destination": None,
            "destinations_considered": [],
            "departure_city": None,  # where user is flying from
            "duration": None,
            "budget": None,
            "budget_type": None,  # 'daily', 'total'
            "interests": [],
            "food_preference": None,  # vegetarian, non-vegetarian, vegan, any
            "cuisine_preference": None,  # Indian, Chinese, Japanese, Thai, Italian, Local, Any
            "travel_dates": None,
            "travel_time_preference": None,  # morning, afternoon, evening, anytime
            "companions": None,  # solo, couple, family, friends
            "accommodation_preferences": [],
            "activity_preferences": [],
            "dietary_preference": [],
            "special_requirements": []
        }
        
        # LONG-TERM MEMORY: User profile (would be loaded from DB)
        self.user_profile = {
            "past_trips": [],
            "favorite_destinations": [],
            "travel_style": None,  # budget, mid-range, luxury
            "preferences": {}
        }
        
        # EPISODIC MEMORY: Specific events/interactions
        self.episodes = []
        
        # CONTEXT: Additional runtime context (UI selections, etc.)
        self.context = {}
        
        # GENERATED TRIP DATA: Store generated flights, hotels, activities to prevent regeneration
        self.generated_trip_data = {
            "flights": None,
            "hotels": None,
            "activities": None,
            "itinerary_text": None,
            "generated_at": None
        }
        
        # Metadata
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
    
    def add_turn(self, user_query: str, agent_response: Optional[str] = None):
        """Add a conversation turn to short-term memory"""
        turn = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_query,
            "agent": agent_response
        }
        self.short_term.append(turn)
        
        # Prune old turns to maintain context window
        if len(self.short_term) > self.max_short_term:
            # Keep most recent turns
            self.short_term = self.short_term[-self.max_short_term:]
        
        self.last_updated = datetime.utcnow()
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get runtime context dictionary (for UI selections, temporary state, etc.)
        Returns mutable dictionary that can be updated directly
        """
        return self.context
    
    def update_entity(self, entity_type: str, value: Any, append: bool = False):
        """
        Update semantic memory with extracted entity
        
        Args:
            entity_type: Key in self.entities
            value: New value
            append: If True, append to list; if False, replace
        """
        if entity_type not in self.entities:
            return
        
        # Core trip parameters - if they change, clear cached trip data
        core_params = ["destination", "departure_city", "duration", "travel_dates", "budget"]
        
        if append and isinstance(self.entities[entity_type], list):
            if value not in self.entities[entity_type]:
                self.entities[entity_type].append(value)
        else:
            # Check if core parameter changed
            if entity_type in core_params and self.entities[entity_type] != value:
                print(f"🔄 Core parameter '{entity_type}' changed: {self.entities[entity_type]} → {value}")
                self.clear_trip_data()
            
            self.entities[entity_type] = value
        
        self.last_updated = datetime.utcnow()
    
    def get_context_summary(self) -> str:
        """
        Generate compact context summary for LLM prompts
        Combines short-term conversation with semantic entities
        """
        context_parts = []
        
        # Add semantic entities (structured knowledge)
        if self.entities["destination"]:
            context_parts.append(f"Destination: {self.entities['destination']}")
        
        if self.entities["departure_city"]:
            context_parts.append(f"Departure city: {self.entities['departure_city']}")
        
        if self.entities["duration"]:
            context_parts.append(f"Duration: {self.entities['duration']}")
        
        if self.entities["budget"]:
            budget_str = f"Budget: {self.entities['budget']}"
            if self.entities["budget_type"]:
                budget_str += f" ({self.entities['budget_type']})"
            context_parts.append(budget_str)
        
        if self.entities["interests"]:
            context_parts.append(f"Interests: {', '.join(self.entities['interests'])}")
        
        # Add recent conversation turns
        if self.short_term:
            context_parts.append("\nRecent conversation:")
            for turn in self.short_term[-3:]:  # Last 3 turns
                context_parts.append(f"User: {turn['user']}")
                if turn.get('agent'):
                    context_parts.append(f"Agent: {turn['agent'][:100]}...")  # Truncate
        
        return "\n".join(context_parts)
    
    def has_complete_info(self) -> bool:
        """Check if we have all required information for trip planning"""
        return all([
            self.entities["destination"],
            self.entities["duration"],
            self.entities["budget"],
            len(self.entities["interests"]) > 0
        ])
    
    def store_trip_data(self, flights, hotels, activities=None, itinerary_text=None):
        """Store generated trip data to prevent regeneration on every message"""
        self.generated_trip_data = {
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
            "itinerary_text": itinerary_text,
            "generated_at": datetime.utcnow().isoformat()
        }
        self.last_updated = datetime.utcnow()
        print(f"💾 Stored trip data: {len(flights or [])} flights, {len(hotels or [])} hotels")
    
    def has_trip_data(self) -> bool:
        """Check if trip data has already been generated"""
        return self.generated_trip_data.get("flights") is not None
    
    def clear_trip_data(self):
        """Clear generated trip data (when core params like destination/dates change)"""
        self.generated_trip_data = {
            "flights": None,
            "hotels": None,
            "activities": None,
            "itinerary_text": None,
            "generated_at": None
        }
        print("🗑️ Cleared trip data - will regenerate on next request")
    
    def get_missing_info(self) -> List[str]:
        """Return list of missing required information"""
        missing = []
        if not self.entities["destination"]:
            missing.append("destination")
        if not self.entities["duration"]:
            missing.append("duration")
        if not self.entities["budget"]:
            missing.append("budget")
        if len(self.entities["interests"]) == 0:
            missing.append("interests")
        return missing
    
    def add_episode(self, event_type: str, data: Dict):
        """
        Store episodic memory (specific events)
        E.g., "user rejected hotel X", "user liked destination Y"
        """
        episode = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "data": data
        }
        self.episodes.append(episode)
    
    def to_dict(self) -> Dict:
        """Serialize memory for storage (Redis/MongoDB)"""
        return {
            "session_id": self.session_id,
            "short_term": self.short_term,
            "entities": self.entities,
            "user_profile": self.user_profile,
            "episodes": self.episodes,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationMemory':
        """Deserialize memory from storage"""
        memory = cls(data["session_id"])
        memory.short_term = data.get("short_term", [])
        memory.entities = data.get("entities", memory.entities)
        memory.user_profile = data.get("user_profile", memory.user_profile)
        memory.episodes = data.get("episodes", [])
        return memory
    
    def clear(self):
        """Reset conversation memory (keep user profile)"""
        self.short_term = []
        self.entities = {key: [] if isinstance(val, list) else None 
                        for key, val in self.entities.items()}
        self.episodes = []


class MemoryManager:
    """
    Manages multiple conversation memories across sessions
    In production: Replace in-memory storage with Redis/MongoDB
    """
    
    def __init__(self):
        # In-memory storage (use Redis for production)
        self._memories: Dict[str, ConversationMemory] = {}
    
    def get_or_create(self, session_id: str) -> ConversationMemory:
        """Get existing memory or create new one"""
        if session_id not in self._memories:
            self._memories[session_id] = ConversationMemory(session_id)
        return self._memories[session_id]
    
    def save(self, session_id: str):
        """
        Persist memory to storage
        TODO: Implement Redis/MongoDB persistence
        """
        if session_id in self._memories:
            memory = self._memories[session_id]
            # TODO: Save to Redis/MongoDB
            # redis_client.set(f"memory:{session_id}", json.dumps(memory.to_dict()))
            pass
    
    def load(self, session_id: str) -> Optional[ConversationMemory]:
        """
        Load memory from storage
        TODO: Implement Redis/MongoDB loading
        """
        # TODO: Load from Redis/MongoDB
        # data = redis_client.get(f"memory:{session_id}")
        # if data:
        #     return ConversationMemory.from_dict(json.loads(data))
        return None
    
    def delete(self, session_id: str):
        """Delete session memory"""
        if session_id in self._memories:
            del self._memories[session_id]


# Global memory manager instance
memory_manager = MemoryManager()
