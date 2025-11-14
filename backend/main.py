from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import os
import json
import datetime
from dotenv import load_dotenv

from agents.orchestrator import OrchestratorAgent  # Import orchestrator

load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

client = MongoClient(os.getenv("MONGO_URI"))
db = client["tripmate_db"]
trips_collection = db["trips"]

# Initialize orchestrator once
orchestrator = OrchestratorAgent()

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
        print("Received request to /api/generate")
        
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        query = data.get("query", "").strip()
        print(f"Processing query: {query}")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Use orchestrator to process the query
        try:
            result = orchestrator.handle_request(query)
            print(f"Orchestrator result: {result}")
        except Exception as e:
            print(f"Orchestrator error: {str(e)}")
            return jsonify({"error": "Failed to process query"}), 500

        # Store in MongoDB if available
        try:
            trips_collection.insert_one({
                "query": query,
                "result": result,
                "timestamp": datetime.datetime.utcnow()
            })
        except Exception as e:
            print(f"MongoDB error (non-fatal): {str(e)}")

        return jsonify(result)
        
    except Exception as e:
        error_response = {"error": str(e)}
        print(f"Error: {error_response}")
        return jsonify(error_response), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
