from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from pymongo import MongoClient
import os
import json
import datetime
from dotenv import load_dotenv
from collections import defaultdict

from agents.orchestrator import OrchestratorAgent  # Import orchestrator
from agents.entity_extractor import EntityExtractorAgent
from memory.conversation_memory import memory_manager

# Import database models and routes
from models.user import User
from models.trip import Trip
from routes.auth import auth_bp, init_auth_routes
from routes.trips import trips_bp, init_trips_routes
from routes.recommendations import recommendations_bp, init_recommendations_routes
from routes.locations import locations_bp  # Import location search routes

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tripmate-secret-key-change-in-production")
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# MongoDB connection (enabled for trip storage)
mongodb_uri = os.getenv("MONGODB_URI")
db = None
user_model = None
trip_model = None

if mongodb_uri:
    try:
        # Try to connect with shorter timeout and SSL workarounds for macOS LibreSSL
        client = MongoClient(
            mongodb_uri, 
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True  # Workaround for LibreSSL SSL issues
        )
        # Test connection
        client.server_info()
        db = client["tripmate_db"]
        
        # Initialize models
        user_model = User(db)
        trip_model = Trip(db)
        
        # Initialize routes with models
        init_auth_routes(user_model)
        init_trips_routes(trip_model, user_model)
        init_recommendations_routes(trip_model, user_model)
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(trips_bp)
        app.register_blueprint(recommendations_bp)
        
        print("✅ MongoDB connected successfully! Trip storage enabled.")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {str(e)}")
        print("⚠️  Trip storage disabled. Only chat mode available.")
        db = None
else:
    print("⚠️  No MONGODB_URI in .env. Trip storage disabled.")

# Register location search blueprint (no MongoDB required)
app.register_blueprint(locations_bp)

# Initialize agents once
orchestrator = OrchestratorAgent()
entity_extractor = EntityExtractorAgent()

# Legacy in-memory storage (deprecated - use memory_manager instead)
conversations = defaultdict(list)

@app.route("/")
def home():
    return jsonify({"status": "TripMate backend ok"})

@app.route("/test")
def test_page():
    return send_file('test.html')

@app.route("/api/generate", methods=["POST"])
def generate_itinerary():
    try:
        print("\n=== New Request ===")
        
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")
        
        print(f"Session: {session_id}, Query: {query}")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Get or create conversation memory for this session
        memory = memory_manager.get_or_create(session_id)
        
        # Add user query to short-term memory FIRST (before first message check)
        memory.add_turn(query)
        
        # If this is the FIRST query (just added, so length == 1), suggest popular destinations
        # But only if query is generic greeting like "hi", "hello", not a destination
        is_first_message = len(memory.short_term) == 1
        is_greeting = query.lower().strip() in ['hi', 'hello', 'hey', 'start', 'begin', 'help']
        
        if is_first_message and is_greeting and not memory.entities.get("destination"):
            import random
            
            # Dynamic destination categories with variety
            beach_destinations = [
                "🏖️ Bali, Indonesia - Pristine beaches & ancient temples",
                "🌴 Maldives - Crystal waters & luxury overwater villas",
                "🏝️ Phuket, Thailand - Island paradise & vibrant nightlife",
                "� Santorini, Greece - Iconic sunsets & white-washed villages"
            ]
            
            city_destinations = [
                "🗼 Paris, France - Art, romance & world-class cuisine",
                "🏯 Tokyo, Japan - Futuristic tech meets ancient traditions",
                "🗽 New York, USA - The city that never sleeps",
                "🕌 Dubai, UAE - Modern marvels & desert adventures"
            ]
            
            nature_destinations = [
                "🏔️ Swiss Alps, Switzerland - Majestic mountains & scenic trails",
                "� Iceland - Northern lights & dramatic landscapes",
                "🦁 Tanzania - Safari adventures & Mount Kilimanjaro",
                "🏞️ New Zealand - Lord of the Rings landscapes"
            ]
            
            cultural_destinations = [
                "🏛️ Rome, Italy - Ancient history & incredible food",
                "🕌 Istanbul, Turkey - Where East meets West",
                "🏯 Kyoto, Japan - Traditional temples & gardens",
                "� Prague, Czech Republic - Fairytale architecture"
            ]
            
            # Randomly select 2 from each category for variety
            selected_destinations = (
                random.sample(beach_destinations, 2) +
                random.sample(city_destinations, 2) +
                random.sample(nature_destinations, 2) +
                random.sample(cultural_destinations, 2)
            )
            
            # Shuffle for more dynamic feel
            random.shuffle(selected_destinations)
            
            # Dynamic greeting messages
            greetings = [
                "Ready to explore the world? ✈️",
                "Your next adventure awaits! 🌍",
                "Let's discover your dream destination! 🗺️",
                "Time to plan something amazing! ✨"
            ]
            
            tips = [
                "💡 **Pro tip:** Tell me your travel style (adventure, relaxation, food, culture) for better recommendations!",
                "💡 **Quick start:** Pick a destination below or tell me your dream trip!",
                "💡 **Not sure?** Just tell me what you love - beaches, mountains, cities, or culture!",
                "💡 **Fun fact:** I can help you plan everything from budget backpacking to luxury getaways!"
            ]
            
            welcome_text = f"""👋 **Welcome to TripMate!** I'm your AI travel companion.

{random.choice(greetings)}

🌍 **Trending Destinations Right Now:**
{chr(10).join(selected_destinations)}

{random.choice(tips)}

**Or simply type any destination you're dreaming of!** 🎯"""
            
            return jsonify({
                "response": welcome_text,
                "needs_clarification": True,
                "show_destinations": True
            })
        
        # Extract entities from current query and update semantic memory
        try:
            # Get full conversation context for entity extraction (including agent responses)
            conversation_lines = []
            for turn in memory.short_term:
                conversation_lines.append(f"User: {turn['user']}")
                if turn.get('agent'):
                    conversation_lines.append(f"Assistant: {turn['agent']}")
            conversation_text = "\n".join(conversation_lines)
            
            # Pass current memory state so entity extractor knows what's already set
            entities = entity_extractor.extract_entities(conversation_text, current_memory=memory.entities)
            
            print(f"🔍 LLM Extracted: {entities}")
            print(f"📊 Current Memory: {memory.entities}")
            
            # ===== RULE-BASED VALIDATION (LLM ka backup!) =====
            # Fix: Prevent LLM from overwriting destination with departure_city
            if memory.entities.get("destination") and entities.get("destination"):
                # Destination already set, but LLM returned a new destination
                if entities["destination"] != memory.entities["destination"]:
                    # This is likely a departure_city that LLM confused as destination!
                    if not memory.entities.get("departure_city"):
                        print(f"⚠️  VALIDATION: LLM tried to change destination '{memory.entities['destination']}' to '{entities['destination']}'")
                        print(f"✅ FIXED: Setting '{entities['destination']}' as departure_city instead")
                        entities["departure_city"] = entities["destination"]
                        entities["destination"] = None  # Don't overwrite existing destination!
            
            print(f"✅ After Validation: {entities}")
            
            # Update semantic memory
            if entities.get("destination"):
                memory.update_entity("destination", entities["destination"])
            
            if entities.get("departure_city"):
                memory.update_entity("departure_city", entities["departure_city"])
            
            if entities.get("duration"):
                memory.update_entity("duration", entities["duration"])
            
            if entities.get("budget"):
                memory.update_entity("budget", entities["budget"])
                if entities.get("budget_type"):
                    memory.update_entity("budget_type", entities["budget_type"])
            
            if entities.get("interests"):
                for interest in entities["interests"]:
                    memory.update_entity("interests", interest, append=True)
            
            if entities.get("food_preference"):
                memory.update_entity("food_preference", entities["food_preference"])
            
            if entities.get("cuisine_preference"):
                memory.update_entity("cuisine_preference", entities["cuisine_preference"])
            
            if entities.get("travel_dates"):
                memory.update_entity("travel_dates", entities["travel_dates"])
            
            if entities.get("travel_time_preference"):
                memory.update_entity("travel_time_preference", entities["travel_time_preference"])
            
            if entities.get("companions"):
                memory.update_entity("companions", entities["companions"])
                
        except Exception as e:
            print(f"Entity extraction error (non-fatal): {str(e)}")
        
        # Build context from memory for orchestrator
        context_summary = memory.get_context_summary()
        
        # Legacy: Also maintain old conversation list for backward compatibility
        history = conversations[session_id]
        history.append(query)
        
        # Build full query with context
        if context_summary:
            full_query = f"{context_summary}\n\nCurrent query: {query}"
        else:
            full_query = query
        
        print(f"Memory state: {memory.entities}")
        print(f"Context summary: {context_summary}")

        # Use orchestrator to process the query with memory
        try:
            result = orchestrator.handle_request(full_query, memory=memory)
            print(f"Orchestrator result: {result}")
            
            # Store agent response in memory
            response_text = str(result)[:200]  # Truncate for storage
            memory.short_term[-1]["agent"] = response_text
            
        except Exception as e:
            print(f"Orchestrator error: {str(e)}")
            return jsonify({"error": "Failed to process query"}), 500

        # Persist memory (TODO: implement Redis/MongoDB persistence)
        memory_manager.save(session_id)

        # Add session_id and memory info to response
        result["session_id"] = session_id
        result["memory_entities"] = memory.entities  # Include for debugging
        
        return jsonify(result)
        
    except Exception as e:
        error_response = {"error": str(e)}
        print(f"Error: {error_response}")
        return jsonify(error_response), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
