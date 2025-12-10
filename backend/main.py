from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from collections import defaultdict
import certifi

from agents.orchestrator import OrchestratorAgent  # Import orchestrator
from agents.langchain_orchestrator import LangChainOrchestrator  # Import LangChain orchestrator
from agents.entity_extractor import EntityExtractorAgent
from memory.conversation_memory import memory_manager

# Configuration: Use LangChain orchestrator (True) or classic orchestrator (False)
USE_LANGCHAIN_ORCHESTRATOR = os.getenv("USE_LANGCHAIN_ORCHESTRATOR", "true").lower() == "true"

# Import database models and routes
from models.user import User
from models.trip import Trip
from routes.auth import auth_bp, init_auth_routes
from routes.trips import trips_bp, init_trips_routes
from routes.recommendations import recommendations_bp, init_recommendations_routes
from routes.locations import locations_bp  # Import location search routes
from routes.trending import init_trending_routes  # Import trending routes

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
        # Check if using local MongoDB or Atlas
        is_local = 'localhost' in mongodb_uri or '127.0.0.1' in mongodb_uri
        
        if is_local:
            # Local MongoDB - no TLS needed
            client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
        else:
            # MongoDB Atlas - use certifi for proper SSL/TLS certificates (macOS LibreSSL fix)
            client = MongoClient(
                mongodb_uri, 
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                tlsCAFile=certifi.where()
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
        trending_bp = init_trending_routes(trip_model)  # Initialize trending routes
        
        print("✅ MongoDB connected successfully! Trip storage enabled.")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {str(e)}")
        print("⚠️  Trip storage disabled. Only chat mode available.")
        db = None
        trending_bp = None  # No trending routes without DB
        # Initialize routes with None (they will handle missing DB gracefully)
        init_auth_routes(None)
        init_trips_routes(None, None)
        init_recommendations_routes(None, None)
else:
    print("⚠️  No MONGODB_URI in .env. Trip storage disabled.")
    trending_bp = None  # No trending routes without DB
    # Initialize routes with None
    init_auth_routes(None)
    init_trips_routes(None, None)
    init_recommendations_routes(None, None)

# Always register blueprints (they will return appropriate errors if DB unavailable)
app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(recommendations_bp)
if trending_bp:  # Only register if MongoDB is available
    app.register_blueprint(trending_bp)

# Register location search blueprint (no MongoDB required)
app.register_blueprint(locations_bp)

# Initialize agents once
if USE_LANGCHAIN_ORCHESTRATOR:
    print("🚀 Using LangChain-powered Orchestrator (Agentic AI)")
    orchestrator = LangChainOrchestrator()
else:
    print("📋 Using Classic Orchestrator")
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
        ui_selections = data.get("ui_selections", {})
        
        print(f"Session: {session_id}, Query: {query}")
        if ui_selections:
            print(f"📋 UI Selections: {ui_selections}")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Get or create conversation memory for this session
        memory = memory_manager.get_or_create(session_id)
        
        # Store UI selections in memory context for conflict detection
        if ui_selections:
            context = memory.get_context()
            if "ui_selections" not in context:
                context["ui_selections"] = {}
            context["ui_selections"].update(ui_selections)
        
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
                "💡 **Quick start:** Pick a destination from the carousel or tell me your dream trip!",
                "💡 **Not sure?** Browse our trending destinations or tell me what you love!",
                "💡 **Fun fact:** I can help you plan everything from budget backpacking to luxury getaways!"
            ]
            
            welcome_text = f"""👋 **Welcome to TripMate!** I'm your AI travel companion.

{random.choice(greetings)}

{random.choice(tips)}

**Browse trending destinations above or type any place you're dreaming of!** 🎯"""
            
            return jsonify({
                "response": welcome_text,
                "needs_clarification": True,
                "show_destinations": True,
                "carousel_enabled": True
            })
        
        # Extract entities from current query and update semantic memory
        try:
            # FAST PATH: If UI selections are provided, skip entity extraction for simple acknowledgments
            # (like selecting from chips/dropdowns - no need to run LLM)
            simple_acknowledgments = ['ok', 'yes', 'sure', 'yep', 'yeah', 'go ahead', 'proceed', 'continue']
            is_simple_ack = query.lower().strip() in simple_acknowledgments
            
            if ui_selections and is_simple_ack:
                print(f"⚡ FAST PATH: UI selections detected with simple acknowledgment - skipping entity extraction")
                entities = {}  # Empty - will use ui_selections below
            else:
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
            
            # ===== CHECK FOR CONFLICTING UI SELECTIONS VS TYPED INPUT =====
            # Only check conflicts if entities were NEWLY extracted from THIS query
            # (Not from accumulated memory)
            ui_selections = memory.get_context().get("ui_selections", {})
            conflicts_detected = []
            
            # FAST PATH: Skip conflict detection if user used UI selections (no typed conflicts possible)
            if not (ui_selections and is_simple_ack):
                # Extract entities from JUST this current query with last assistant context
                # Include last assistant message for context awareness
                last_turn_context = ""
                if len(memory.short_term) >= 2 and memory.short_term[-2].get('agent'):
                    last_turn_context = f"Assistant: {memory.short_term[-2]['agent']}\nUser: {query}"
                else:
                    last_turn_context = f"User: {query}"
                
                current_query_entities = entity_extractor.extract_entities(last_turn_context, current_memory={})
            else:
                print(f"⚡ FAST PATH: Skipping conflict detection for UI selections")
                current_query_entities = {}
            
            for key in ["destination", "departure_city", "duration", "budget", "travel_dates"]:
                # Only flag conflict if:
                # 1. User previously selected from UI
                # 2. Current query contains a NEW value for same field
                # 3. Values are different
                if key in ui_selections and key in current_query_entities:
                    ui_value = str(ui_selections[key]).lower().strip()
                    typed_value = str(current_query_entities[key]).lower().strip()
                    
                    # Normalize for comparison (remove extra spaces, special chars)
                    import re
                    ui_norm = re.sub(r'[^\w\s]', '', ui_value)
                    typed_norm = re.sub(r'[^\w\s]', '', typed_value)
                    
                    # Check if values are meaningfully different
                    if ui_norm != typed_norm and not any(part in typed_norm for part in ui_norm.split()):
                        conflicts_detected.append({
                            "field": key,
                            "ui_selection": ui_selections[key],
                            "typed_value": current_query_entities[key]
                        })
            
            # ===== INTELLIGENT UPDATE HANDLING =====
            # Detect explicit change phrases that indicate user wants to UPDATE existing info
            query_lower = query.lower()
            explicit_change_phrases = ['actually', 'instead', 'change to', 'i meant', 'correction', 'no wait', 'make it', 'update to']
            is_explicit_change = any(phrase in query_lower for phrase in explicit_change_phrases)
            
            # If conflicts detected and NOT an explicit change, ask for clarification
            if conflicts_detected and not is_explicit_change:
                conflict_messages = []
                for conflict in conflicts_detected:
                    field_name = conflict["field"].replace("_", " ").title()
                    conflict_messages.append(
                        f"• **{field_name}**: You selected *{conflict['ui_selection']}* but just typed *{conflict['typed_value']}*"
                    )
                
                return jsonify({
                    "needs_clarification": True,
                    "message": f"🤔 I noticed some conflicting information:\n\n" + "\n".join(conflict_messages) + "\n\n**Which one should I use?**\n\nYou can say:\n• 'use what I typed'\n• 'use what I selected'\n• Or just tell me the correct one!",
                    "conflicts": conflicts_detected,
                    "clarification_type": "conflict_resolution"
                })
            
            # If explicit change detected, log the update and clear UI selection
            if is_explicit_change and conflicts_detected:
                print(f"🔄 EXPLICIT CHANGE DETECTED - User typed overrides UI selection")
                for conflict in conflicts_detected:
                    field = conflict["field"]
                    old_val = conflict["ui_selection"]
                    new_val = conflict["typed_value"]
                    print(f"   {field}: '{old_val}' → '{new_val}'")
                    # Clear UI selection for this field
                    if "ui_selections" in memory.get_context():
                        memory.get_context()["ui_selections"].pop(field, None)
            
            # Fix: Prevent LLM from overwriting destination with departure_city (UNLESS user explicitly changed it)
            if memory.entities.get("destination") and entities.get("destination"):
                # Destination already set, but LLM returned a new destination
                if entities["destination"] != memory.entities["destination"]:
                    if is_explicit_change:
                        # User explicitly wants to CHANGE destination
                        print(f"🔄 USER UPDATE: Changing destination from '{memory.entities['destination']}' to '{entities['destination']}'")
                        # Let the update happen below
                    else:
                        # This is likely a departure_city that LLM confused as destination!
                        if not memory.entities.get("departure_city"):
                            print(f"⚠️  VALIDATION: LLM tried to change destination '{memory.entities['destination']}' to '{entities['destination']}'")
                            print(f"✅ FIXED: Setting '{entities['destination']}' as departure_city instead")
                            entities["departure_city"] = entities["destination"]
                            entities["destination"] = None  # Don't overwrite existing destination!
            
            print(f"✅ After Validation: {entities}")
            
            # ===== DURATION & DATE VALIDATION =====
            # Check if duration is too long (max 90 days)
            if entities.get("duration") or entities.get("travel_dates"):
                duration_days = None
                
                # Calculate days from duration string
                if entities.get("duration"):
                    duration_str = entities["duration"].lower()
                    if "year" in duration_str or "month" in duration_str and int(duration_str.split()[0]) > 3:
                        return jsonify({
                            "needs_clarification": True,
                            "message": "⚠️ Whoa! That's quite a long trip! 😅\n\nI can plan trips up to **90 days (3 months)**. Would you like to:\n• Shorten your trip to 90 days or less?\n• Break it into multiple shorter trips?\n\nWhat works best for you?",
                            "validation_error": "duration_too_long"
                        })
                    
                    # Extract number of days
                    import re
                    match = re.search(r'(\d+)\s*(day|week|month)', duration_str)
                    if match:
                        num = int(match.group(1))
                        unit = match.group(2)
                        if unit == "week":
                            duration_days = num * 7
                        elif unit == "month":
                            duration_days = num * 30
                        else:
                            duration_days = num
                
                # Calculate days from date range
                if entities.get("travel_dates") and not duration_days:
                    from datetime import datetime
                    date_str = entities["travel_dates"]
                    try:
                        # Try to parse date range
                        if " to " in date_str:
                            start_str, end_str = date_str.split(" to ")
                            # Parse dates (handle various formats)
                            for fmt in ["%b %d, %Y", "%Y-%m-%d", "%B %d, %Y"]:
                                try:
                                    start_date = datetime.strptime(start_str.strip(), fmt)
                                    end_date = datetime.strptime(end_str.strip(), fmt)
                                    duration_days = (end_date - start_date).days
                                    break
                                except:
                                    continue
                    except Exception as e:
                        print(f"Date parsing error: {e}")
                
                # Validate duration
                if duration_days and duration_days > 90:
                    return jsonify({
                        "needs_clarification": True,
                        "message": f"⚠️ Your selected trip is **{duration_days} days** long! 😮\n\nI can create detailed itineraries for trips up to **90 days**.\n\nWould you like to:\n• Reduce your trip to 90 days?\n• Split it into {(duration_days // 60) + 1} shorter trips?\n• Just plan the first 30 days in detail?\n\nLet me know!",
                        "validation_error": "duration_too_long",
                        "suggested_duration": "30 days"
                    })
            
            # Update semantic memory with change detection
            if entities.get("destination"):
                old_val = memory.entities.get("destination")
                if old_val and old_val != entities["destination"]:
                    print(f"🔄 UPDATING destination: '{old_val}' → '{entities['destination']}'")
                memory.update_entity("destination", entities["destination"])
            
            if entities.get("departure_city"):
                old_val = memory.entities.get("departure_city")
                if old_val and old_val != entities["departure_city"]:
                    print(f"🔄 UPDATING departure_city: '{old_val}' → '{entities['departure_city']}'")
                memory.update_entity("departure_city", entities["departure_city"])
            
            if entities.get("duration"):
                old_val = memory.entities.get("duration")
                if old_val and old_val != entities["duration"]:
                    print(f"🔄 UPDATING duration: '{old_val}' → '{entities['duration']}'")
                memory.update_entity("duration", entities["duration"])
            
            if entities.get("budget"):
                old_val = memory.entities.get("budget")
                if old_val and old_val != entities["budget"]:
                    print(f"🔄 UPDATING budget: '{old_val}' → '{entities['budget']}'")
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
            
            # FALLBACK: If cuisine_preference still missing, use simple regex to detect common cuisines
            if not memory.entities.get("cuisine_preference"):
                cuisine_keywords = {
                    'indian': 'Indian',
                    'chinese': 'Chinese', 
                    'japanese': 'Japanese',
                    'thai': 'Thai',
                    'italian': 'Italian',
                    'mexican': 'Mexican',
                    'french': 'French',
                    'korean': 'Korean',
                    'vietnamese': 'Vietnamese',
                    'local': 'Local/Traditional',
                    'traditional': 'Local/Traditional',
                    'street food': 'Street Food',
                    'fine dining': 'Fine Dining'
                }
                query_lower = query.lower()
                for keyword, cuisine_name in cuisine_keywords.items():
                    if keyword in query_lower:
                        print(f"✅ REGEX FALLBACK: Detected cuisine '{cuisine_name}' from query")
                        memory.update_entity("cuisine_preference", cuisine_name)
                        break
            
            if entities.get("travel_dates"):
                memory.update_entity("travel_dates", entities["travel_dates"])
            
            if entities.get("travel_time_preference"):
                memory.update_entity("travel_time_preference", entities["travel_time_preference"])
            
            if entities.get("companions"):
                memory.update_entity("companions", entities["companions"])
            
            # Handle travel_companion → companions mapping
            if entities.get("travel_companion"):
                memory.update_entity("companions", entities["travel_companion"])
            
            # Handle dietary preferences
            if entities.get("dietary_preference"):
                memory.update_entity("dietary_preference", entities["dietary_preference"])
                
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
    app.run(host="0.0.0.0", port=5002, debug=True)

