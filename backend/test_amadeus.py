#!/usr/bin/env python3
"""
Amadeus API Connection Test Script

This script verifies that:
1. Amadeus credentials are correctly set in .env
2. Amadeus API is accessible and working
3. Flight search returns real data

Run this BEFORE integrating Amadeus into the main app.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_amadeus_connection():
    """Test Amadeus API connection and basic flight search"""
    
    print("=" * 60)
    print("🧪 AMADEUS API CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Step 1: Check credentials
    print("📋 Step 1: Checking credentials...")
    api_key = os.getenv('AMADEUS_API_KEY')
    api_secret = os.getenv('AMADEUS_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ ERROR: Amadeus credentials not found!")
        print()
        print("   Please add to your .env file:")
        print("   AMADEUS_API_KEY=your_key_here")
        print("   AMADEUS_API_SECRET=your_secret_here")
        print()
        print("   Get free credentials at: https://developers.amadeus.com/register")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}..." + "*" * 20)
    print(f"✅ API Secret found: {api_secret[:8]}..." + "*" * 20)
    print()
    
    # Step 2: Import Amadeus SDK
    print("📦 Step 2: Importing Amadeus SDK...")
    try:
        from amadeus import Client, ResponseError
        print("✅ Amadeus SDK imported successfully!")
    except ImportError:
        print("❌ ERROR: Amadeus SDK not installed!")
        print()
        print("   Run: pip install amadeus")
        print("   Or:  pip install -r requirements.txt")
        return False
    print()
    
    # Step 3: Initialize client
    print("🔗 Step 3: Connecting to Amadeus API...")
    try:
        amadeus = Client(
            client_id=api_key,
            client_secret=api_secret
        )
        print("✅ Amadeus client initialized!")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize client: {e}")
        return False
    print()
    
    # Step 4: Test flight search
    print("✈️  Step 4: Testing flight search (Tokyo → Bali)...")
    print("   Searching for: NRT (Tokyo) → DPS (Bali)")
    print("   Date: 2024-12-15 | Adults: 1 | Max results: 3")
    print()
    
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='NRT',
            destinationLocationCode='DPS',
            departureDate='2024-12-15',
            adults=1,
            max=3
        )
        
        print("✅ Flight search successful!")
        print()
        print("📊 RESULTS:")
        print("-" * 60)
        
        if not response.data:
            print("⚠️  No flights found for this route/date")
            print("   (This could be normal - try different dates or routes)")
            return True
        
        print(f"Found {len(response.data)} flight offers:\n")
        
        for i, offer in enumerate(response.data, 1):
            price = offer['price']['total']
            currency = offer['price']['currency']
            
            # Get first itinerary
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            # Determine if direct
            is_direct = len(segments) == 1
            stops = len(segments) - 1
            
            # Get airline
            airline_code = segments[0]['carrierCode']
            
            print(f"Flight #{i}:")
            print(f"  💰 Price: {currency} {price}")
            print(f"  ✈️  Airline: {airline_code}")
            print(f"  🛫 Route: {is_direct and 'Direct' or f'{stops} stop(s)'}")
            print(f"  ⏱️  Duration: {itinerary['duration']}")
            
            # Show segments
            for j, seg in enumerate(segments, 1):
                print(f"      Segment {j}: {seg['departure']['iataCode']} → {seg['arrival']['iataCode']}")
                print(f"         Depart: {seg['departure']['at']}")
                print(f"         Arrive: {seg['arrival']['at']}")
            
            print()
        
        print("-" * 60)
        print()
        print("🎉 SUCCESS! Amadeus API is working correctly!")
        print()
        print("Next steps:")
        print("1. ✅ Your credentials are valid")
        print("2. ✅ Amadeus API is accessible")
        print("3. ✅ Flight data is being returned")
        print("4. 🚀 You can now start the backend: python3 main.py")
        print()
        print("The backend will automatically use real Amadeus data!")
        
        return True
        
    except ResponseError as error:
        print(f"❌ API ERROR: {error}")
        print()
        print("Common issues:")
        print("- Invalid credentials (double-check API key/secret)")
        print("- Free tier quota exceeded (2,000 calls/month)")
        print("- Network connectivity issues")
        return False
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_amadeus_connection()
    sys.exit(0 if success else 1)
