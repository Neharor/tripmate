# GitHub Copilot Instructions for TripMate

TripMate is an AI-powered travel planner with a **Single Agent Architecture** using LangChain orchestration, machine learning recommendations, and real-time APIs.

## 🏗️ Architecture Overview

### Core Components
- **LangChain Orchestrator** (`backend/agents/langchain_orchestrator.py`) - Main ReAct agent with Groq LLM
- **5 Specialized Tools** wrapped as LangChain tools in `langchain_tools.py`
- **ML Engine** - Collaborative filtering trained on 6,580 trip records
- **Live APIs** - Amadeus (flights/hotels), Google Places (activities)

### Agent Pattern
All agents extend `BaseAgent` (abstract class) with consistent structure:
```python
class SomeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SomeName", system_prompt="...")
    
    def handle_request(self, input_data):
        # Process with self._call_llm() or external APIs
        return structured_response
```

## 🚀 Developer Workflows

### Backend Setup
```bash
cd backend
pip3 install -r requirements.txt
python3 main.py  # Runs on localhost:5002
```

### Frontend Setup
```bash
cd frontend/trimate-frontend
npm install
npm start  # Runs on localhost:3000 with proxy to :5002
```

### Testing
- `python3 test_amadeus.py` - Test Amadeus API integration
- `python3 test_enhanced_itinerary.py` - E2E trip generation test
- `python3 ml/collaborative_filter.py` - Test ML recommendations

## 🧠 Key Patterns

### 1. Orchestrator Selection
Main entry point checks environment variable:
```python
USE_LANGCHAIN_ORCHESTRATOR = os.getenv("USE_LANGCHAIN_ORCHESTRATOR", "true").lower() == "true"
```
- `True` → Uses LangChain ReAct agent (default)
- `False` → Uses classic orchestrator

### 2. Tool Structure
LangChain tools in `langchain_tools.py` wrap agents with proper schemas:
```python
def create_flight_tool(flight_agent):
    def search_flights(query: str) -> str:
        result = flight_agent.handle_request(query)
        return json.dumps(result, indent=2)
    
    return Tool(name="FlightPlanner", description="...", func=search_flights)
```

### 3. API Integration Pattern
- **Amadeus**: OAuth token in `services/flight_service.py`, `services/hotel_service.py`
- **Google Places**: Direct API key in `services/activities_service.py`
- **Groq LLM**: Used across all agents via `BaseAgent._call_llm()`

### 4. ML Integration
Collaborative filtering in `ml/collaborative_filter.py`:
```python
cf_recommender.get_similar_destinations('Bangkok', top_n=5)
# Returns: [(destination, similarity_score), ...]
```

## 📁 File Organization

### Critical Files for Agent Development
- `backend/agents/langchain_orchestrator.py` - Main agent logic
- `backend/agents/langchain_tools.py` - Tool definitions
- `backend/agents/base_agent.py` - Agent base class
- `backend/services/` - External API clients
- `backend/ml/` - Machine learning models

### Route Structure
Flask routes in `backend/routes/`:
- `auth_routes.py` - Authentication
- `trip_routes.py` - Trip CRUD operations  
- `trending.py` - ML-powered trending destinations
- `locations.py` - Location search/autocomplete

## 🔧 Environment Configuration

Required `.env` variables:
```
GROQ_API_KEY=your_groq_api_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
GOOGLE_PLACES_API_KEY=your_google_places_key (optional)
MONGODB_URI=your_mongodb_uri (optional)
```

## 🎯 Development Guidelines

### Adding New Agents
1. Extend `BaseAgent` in `backend/agents/`
2. Create corresponding tool in `langchain_tools.py`
3. Add tool to `create_all_tools()` function
4. Update orchestrator prompt if needed

### ML Model Updates
- Training data in `backend/ml/data/kaggle/`
- Models auto-rebuild on data changes
- Test with `python3 ml/collaborative_filter.py`

### Frontend Integration
- API calls via `src/api.js` with proxy to `:5002`
- Components in `src/components/` follow Material-UI patterns
- Chat interface in `ChatInterface.js` handles LangChain streaming

### Error Handling
- LangChain tools return JSON strings on success, error messages on failure
- Amadeus API errors handled with fallback responses
- ML models have graceful degradation when data unavailable

## 🔍 Debugging Tips

- Check `USE_LANGCHAIN_ORCHESTRATOR` flag for agent routing
- LangChain agent thoughts visible in `/api/generate` response
- Amadeus API test script: `python3 backend/test_amadeus.py`
- ML recommendations test: `python3 backend/ml/collaborative_filter.py`