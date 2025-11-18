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

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tripmate-secret-key-change-in-production")
CORS(app, supports_credentials=True)  # Enable CORS with session support

# MongoDB disabled - causing 30s SSL timeout delays
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["tripmate_db"]
# trips_collection = db["trips"]

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
        
        # Add user query to short-term memory
        memory.add_turn(query)
        
        # Extract entities from current query and update semantic memory
        try:
            # Get full conversation context for entity extraction (including agent responses)
            conversation_lines = []
            for turn in memory.short_term:
                conversation_lines.append(f"User: {turn['user']}")
                if turn.get('agent'):
                    conversation_lines.append(f"Assistant: {turn['agent']}")
            conversation_text = "\n".join(conversation_lines)
            
            entities = entity_extractor.extract_entities(conversation_text)
            
            print(f"Extracted entities: {entities}")
            
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
