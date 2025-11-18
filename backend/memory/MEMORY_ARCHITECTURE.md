# TripMate Memory Architecture

## Overview

TripMate implements a **multi-layered memory system** inspired by cognitive science and modern agentic AI architectures. This enables the system to maintain context across conversations and provide personalized recommendations.

## Memory Layers

### 1. **Short-Term Memory** (Working Memory)
- **Purpose**: Store recent conversation turns (last 5-10 exchanges)
- **Retention**: Current session only
- **Use Case**: Maintain conversational flow, resolve pronouns/references
- **Implementation**: `ConversationMemory.short_term`

```python
memory.add_turn("Plan a trip to Bali", "I'd love to help! How many days?")
```

### 2. **Semantic Memory** (Structured Knowledge)
- **Purpose**: Extract and store structured entities from conversations
- **Retention**: Entire session
- **Use Case**: Track destination, budget, duration, interests without re-asking
- **Implementation**: `ConversationMemory.entities`

```python
memory.entities = {
    "destination": "Bali",
    "duration": "5 days",
    "budget": "$20",
    "budget_type": "daily",
    "interests": ["Beach", "Food", "Culture"]
}
```

### 3. **Episodic Memory** (Event History)
- **Purpose**: Remember specific events (user rejected hotel X, liked destination Y)
- **Retention**: Session or cross-session
- **Use Case**: Avoid repeating rejected suggestions, learn preferences
- **Implementation**: `ConversationMemory.episodes`

```python
memory.add_episode("hotel_rejected", {
    "hotel_name": "Expensive Resort",
    "reason": "too expensive"
})
```

### 4. **Long-Term Memory** (User Profile)
- **Purpose**: Store user preferences across multiple trips
- **Retention**: Permanent (database)
- **Use Case**: Personalized recommendations based on past behavior
- **Implementation**: `ConversationMemory.user_profile` + Database

```python
user_profile = {
    "past_trips": ["Bali 2024", "Paris 2023"],
    "favorite_destinations": ["Beach destinations"],
    "travel_style": "budget"
}
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Entity Extractor Agent                          │
│  Extracts: destination, duration, budget, interests          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Conversation Memory                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Short-Term   │  │  Semantic    │  │  Episodic    │      │
│  │   Memory     │  │   Memory     │  │   Memory     │      │
│  │              │  │              │  │              │      │
│  │ Last 10 turns│  │ Entities:    │  │ Events:      │      │
│  │              │  │ - Destination│  │ - Rejections │      │
│  │              │  │ - Budget     │  │ - Preferences│      │
│  │              │  │ - Interests  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Context Summary Generator                       │
│  Combines all memory layers into compact LLM prompt          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Orchestrator + Specialized Agents                  │
│  Process query with full memory context                      │
└─────────────────────────────────────────────────────────────┘
```

## Current Implementation

### In-Memory Storage (Development)
- **Storage**: Python dictionaries in RAM
- **Persistence**: ❌ Lost on restart
- **Scalability**: ❌ Single server only
- **Status**: ✅ Currently active

### Redis Storage (Production-Ready)
- **Storage**: Redis key-value store
- **Persistence**: ✅ Survives restarts
- **Scalability**: ✅ Shared across multiple servers
- **Status**: ⏸️ Commented out in `redis_store.py`

### MongoDB Storage (Future)
- **Storage**: MongoDB documents
- **Persistence**: ✅ Permanent
- **Scalability**: ✅ Fully distributed
- **Status**: 🔮 Planned for user profiles

## Usage Examples

### Basic Usage

```python
from memory.conversation_memory import memory_manager

# Get memory for session
memory = memory_manager.get_or_create("session_123")

# Add conversation turn
memory.add_turn("I want to go to Bali", "Great! How many days?")

# Update entities
memory.update_entity("destination", "Bali")
memory.update_entity("interests", "Beach", append=True)

# Get context for LLM
context = memory.get_context_summary()

# Check if complete
if memory.has_complete_info():
    print("Ready to plan trip!")
else:
    missing = memory.get_missing_info()
    print(f"Still need: {missing}")
```

### Entity Extraction

```python
from agents.entity_extractor import EntityExtractorAgent

extractor = EntityExtractorAgent()

conversation = """
User: I want to visit Bali
User: For 5 days
User: My budget is $50 per day
User: I like beaches and food
"""

entities = extractor.extract_entities(conversation)
# Returns:
# {
#     "destination": "Bali",
#     "duration": "5 days",
#     "budget": "$50",
#     "budget_type": "daily",
#     "interests": ["Beach", "Food"]
# }
```

## Migration to Production

### Step 1: Enable Redis

1. Install Redis:
```bash
docker run -d -p 6379:6379 redis
# OR
brew install redis && redis-server
```

2. Install Python client:
```bash
pip install redis
```

3. Update `.env`:
```
REDIS_URL=redis://localhost:6379
```

4. Uncomment `redis_store.py` code

5. Update `conversation_memory.py`:
```python
from memory.redis_store import RedisMemoryStore

class MemoryManager:
    def __init__(self):
        self.store = RedisMemoryStore(os.getenv("REDIS_URL"))
```

### Step 2: Add Vector Search (Semantic Memory)

For advanced semantic search across past conversations:

1. Install vector DB:
```bash
pip install chromadb  # or pinecone-client, weaviate-client
```

2. Embed conversation turns:
```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vector_store.add_texts([turn["user"] for turn in memory.short_term])
```

3. Retrieve similar past conversations:
```python
similar = vector_store.similarity_search(current_query, k=3)
```

### Step 3: User Profiles in MongoDB

Store long-term user preferences:

```python
user_profile = {
    "user_id": "user_123",
    "past_trips": [
        {
            "destination": "Bali",
            "date": "2024-01-15",
            "rating": 5,
            "budget": "$50/day"
        }
    ],
    "preferences": {
        "travel_style": "budget",
        "favorite_activities": ["beach", "food"],
        "avoided_destinations": []
    }
}

db.users.insert_one(user_profile)
```

## Benefits of Multi-Layer Memory

1. **Context Awareness**: System remembers destination without re-asking
2. **Personalization**: Learns user preferences over time
3. **Efficiency**: Reduces token usage (semantic memory > full conversation history)
4. **Scalability**: Structured entities easier to search/filter than raw text
5. **Persistence**: Redis/DB storage survives server restarts

## Monitoring & Debugging

### View Current Memory State

```python
# In API response
result["memory_entities"] = memory.entities

# Frontend console will show:
{
  "destination": "Bali",
  "duration": "5 days",
  "budget": "$20",
  "interests": ["Beach", "Food"]
}
```

### Memory Metrics

Track memory usage:
- Average entities per session
- Entity extraction accuracy
- Memory hit rate (entities reused vs re-extracted)

## Future Enhancements

1. **Vector Embeddings**: Semantic search across past trips
2. **Entity Linking**: Connect "Bali" mentions across sessions
3. **Memory Consolidation**: Summarize old conversations to save space
4. **Conflict Resolution**: Handle contradictory info (budget changed)
5. **Multi-User Memory**: Shared memory for group trips
6. **Memory Decay**: Expire old preferences automatically

## Files

- `backend/memory/conversation_memory.py` - Core memory classes
- `backend/memory/redis_store.py` - Redis persistence (commented)
- `backend/agents/entity_extractor.py` - Entity extraction agent
- `backend/main.py` - Memory integration in API

## References

- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)
- [Cognitive Architecture](https://en.wikipedia.org/wiki/Cognitive_architecture)
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
