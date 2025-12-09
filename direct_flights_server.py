#!/usr/bin/env python3
"""
Direct flight cards API endpoint - bypasses conversation flow
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

app = Flask(__name__)
CORS(app)

# Mock memory class
class MockMemory:
    def __init__(self, destination, departure_city):
        self.entities = {
            "destination": destination,
            "departure_city": departure_city,
            "duration": "3 days", 
            "budget": "$800",
            "travel_dates": "Dec 9, 2025 to Dec 12, 2025",
            "interests": ["Shopping", "Food"]
        }

@app.route("/api/direct-flights", methods=["POST"])
def get_direct_flights():
    try:
        data = request.get_json()
        destination = data.get("destination", "Dubai, UAE") 
        departure_city = data.get("departure_city", "Mumbai, India")
        
        # Import orchestrator
        from agents.langchain_orchestrator import LangChainOrchestrator
        
        orchestrator = LangChainOrchestrator()
        memory = MockMemory(destination, departure_city)
        
        # Generate flight cards directly
        flight_cards = orchestrator._create_demo_flights(departure_city, destination, memory)
        
        return jsonify({
            "success": True,
            "visual_data": {
                "flights": flight_cards,
                "departure_city": departure_city,
                "destination": destination,
                "travel_dates": "Dec 9, 2025 to Dec 12, 2025"
            },
            "message": f"✈️ Flight options from {departure_city} to {destination}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)