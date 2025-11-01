from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

from backend.agents.orchestrator import OrchestratorAgent  # Import orchestrator

load_dotenv()
app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["tripmate_db"]
trips_collection = db["trips"]

# Initialize orchestrator once
orchestrator = OrchestratorAgent()

@app.route("/")
def home():
    return jsonify({"status": "TripMate backend ok"})

@app.route("/api/generate", methods=["POST"])
def generate_itinerary():
    data = request.get_json()
    query = data.get("query", "")

    # Use orchestrator to handle request instead of dummy data
    result = orchestrator.handle_request(query)

    # Save full result to MongoDB
    trips_collection.insert_one({
        "query": query,
        "result": result
    })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
