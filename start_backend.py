#!/usr/bin/env python3
"""
Quick script to start the backend server with proper environment loading
"""

import os
import sys

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Add backend to Python path
sys.path.insert(0, backend_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("🚀 Starting TripMate Backend Server...")
print(f"📂 Working directory: {os.getcwd()}")

# Check Amadeus credentials
api_key = os.getenv('AMADEUS_API_KEY', '')
if api_key:
    print(f"🔑 Amadeus API Key found: {api_key[:10]}...")
else:
    print("⚠️  Amadeus API Key not found")

# Start the Flask app
if __name__ == "__main__":
    from main import app
    print("✅ Backend server starting on http://localhost:5002")
    app.run(host="0.0.0.0", port=5002, debug=True)