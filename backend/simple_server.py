#!/usr/bin/env python3
"""
Simple TripMate Backend Server (Minimal Dependencies)
Use this if the main server has dependency issues
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure proper Unicode handling
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Simple in-memory conversation storage
conversations = {}

@app.route("/")
def home():
    return jsonify({
        "status": "TripMate Simple Backend Running",
        "message": "🚀 Minimal server is working!"
    })

@app.route("/api/trending-destinations", methods=["GET"])
def trending_destinations():
    """Return trending destinations in the format expected by frontend"""
    return jsonify({
        "success": True,
        "data_source": "simple_server",
        "destinations": [
            {
                "destination": "Bali Indonesia",
                "interests": ["beaches", "culture", "temples"],
                "trip_count": 245,
                "avg_budget": 75,
                "best_time": "Apr Oct",
                "rating": 4.8,
                "reviews": 1960,
                "is_fallback": False
            },
            {
                "destination": "Paris France", 
                "interests": ["culture", "romance", "food"],
                "trip_count": 189,
                "avg_budget": 120,
                "best_time": "Apr Oct",
                "rating": 4.7,
                "reviews": 1512,
                "is_fallback": False
            },
            {
                "destination": "Tokyo Japan",
                "interests": ["culture", "food", "technology"],
                "trip_count": 167,
                "avg_budget": 95,
                "best_time": "Mar May Sep Nov",
                "rating": 4.9,
                "reviews": 1336,
                "is_fallback": False
            },
            {
                "destination": "Dubai UAE",
                "interests": ["luxury", "shopping", "adventure"],
                "trip_count": 134,
                "avg_budget": 140,
                "best_time": "Nov Mar",
                "rating": 4.6,
                "reviews": 1072,
                "is_fallback": False
            },
            {
                "destination": "Bangkok Thailand",
                "interests": ["beaches", "culture", "food"],
                "trip_count": 198,
                "avg_budget": 65,
                "best_time": "Nov Mar",
                "rating": 4.8,
                "reviews": 1584,
                "is_fallback": False
            },
            {
                "destination": "Singapore",
                "interests": ["city", "food", "culture"],
                "trip_count": 112,
                "avg_budget": 110,
                "best_time": "Year round",
                "rating": 4.7,
                "reviews": 896,
                "is_fallback": False
            }
        ]
    })

@app.route("/api/locations/popular", methods=["GET"])
def popular_locations():
    """Return popular locations"""
    return jsonify({
        "locations": [
            "Bali", "Paris", "Tokyo", "London", "New York", "Dubai", 
            "Thailand", "Singapore", "Maldives", "Iceland"
        ]
    })

@app.route("/api/locations/search", methods=["GET"])
def search_locations():
    """Search locations"""
    query = request.args.get('q', '').lower()
    all_locations = [
        "Bali, Indonesia", "Paris, France", "Tokyo, Japan", "London, UK", 
        "New York, USA", "Dubai, UAE", "Bangkok, Thailand", "Singapore", 
        "Maldives", "Iceland", "Rome, Italy", "Barcelona, Spain", 
        "Amsterdam, Netherlands", "Sydney, Australia", "Mumbai, India",
        "Delhi, India", "Goa, India", "Jaipur, India", "Kerala, India"
    ]
    
    if query:
        filtered = [loc for loc in all_locations if query in loc.lower()]
        return jsonify({"suggestions": filtered[:10]})
    return jsonify({"suggestions": all_locations[:10]})

@app.route("/api/destinations", methods=["GET"])
def get_destinations():
    """Get destinations for autocomplete"""
    return jsonify({
        "destinations": [
            {"name": "Bali, Indonesia", "code": "BALI", "country": "Indonesia"},
            {"name": "Paris, France", "code": "PAR", "country": "France"},
            {"name": "Tokyo, Japan", "code": "TYO", "country": "Japan"},
            {"name": "London, UK", "code": "LON", "country": "United Kingdom"},
            {"name": "New York, USA", "code": "NYC", "country": "United States"},
            {"name": "Dubai, UAE", "code": "DXB", "country": "UAE"},
            {"name": "Bangkok, Thailand", "code": "BKK", "country": "Thailand"},
            {"name": "Singapore", "code": "SIN", "country": "Singapore"},
            {"name": "Maldives", "code": "MLE", "country": "Maldives"},
            {"name": "Reykjavik, Iceland", "code": "REK", "country": "Iceland"}
        ]
    })

@app.route("/api/generate", methods=["POST"])
def generate_simple():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")
        
        print(f"Query: {query}")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Simple responses based on query content
        query_lower = query.lower()
        
        # First message - welcome
        if query_lower in ['hi', 'hello', 'hey', 'start']:
            return jsonify({
                "response": "👋 **Welcome to TripMate!** I'm your AI travel companion.\n\n🗺️ **Ready to explore the world?**\n\n**Just tell me:**\n• Where do you want to go? (e.g., 'Bali', 'Paris', 'Tokyo')\n• When? (e.g., 'Dec 15 to Dec 20')\n• Your budget? (e.g., '$100 per day')\n• What interests you? (e.g., 'beaches', 'food', 'adventure')\n\n✨ **Let's plan your dream trip!**",
                "needs_clarification": True
            })
        
        # Store conversation
        if session_id not in conversations:
            conversations[session_id] = []
        conversations[session_id].append(query)
        
        # Detect destination
        destinations = ['bali', 'paris', 'tokyo', 'london', 'new york', 'dubai', 'thailand', 'singapore', 'maldives', 'japan']
        detected_dest = None
        for dest in destinations:
            if dest in query_lower:
                detected_dest = dest.title()
                break
        
        # Detect duration/dates
        duration_detected = False
        if any(word in query_lower for word in ['days', 'weeks', 'to', 'december', 'january', 'feb', 'march']):
            duration_detected = True
        
        # Detect budget
        budget_detected = '$' in query or 'budget' in query_lower or any(word in query_lower for word in ['dollar', 'money', 'cost'])
        
        # Generate response
        if detected_dest:
            response = f"🎉 Great choice - {detected_dest}! I'll help you plan an amazing trip. Here are the top attractions and activities you should visit in {detected_dest}. Let me know your dates and budget for a detailed itinerary!"
        else:
            response = """🤔 **I'd love to help you plan a trip!**

Please tell me:
📍 **Where do you want to go?** 
   (Popular options: Bali, Paris, Tokyo, London, Dubai, Thailand, Singapore)

I can help you plan everything once I know your destination! ✨"""
        
        return jsonify({
            "response": response,
            "needs_clarification": not (detected_dest and duration_detected and budget_detected),
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting TripMate Simple Backend Server...")
    print("📍 Server will be available at: http://localhost:5002")
    print("🌐 Frontend should connect automatically")
    print("\n" + "="*50)
    app.run(host="0.0.0.0", port=5002, debug=False)