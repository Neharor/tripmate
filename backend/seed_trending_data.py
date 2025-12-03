"""
Seed trending destinations with realistic travel data
This populates the database with sample trips to make trending destinations more realistic
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Popular destinations with realistic trip data
TRAVEL_DATASET = [
    # Asia
    {"destination": "Bali, Indonesia", "avg_budget": 50, "interests": ["Beach", "Culture", "Adventure", "Surfing", "Temples"], "trips": 245},
    {"destination": "Tokyo, Japan", "avg_budget": 85, "interests": ["City", "Culture", "Food", "Technology", "Shopping"], "trips": 312},
    {"destination": "Bangkok, Thailand", "avg_budget": 40, "interests": ["City", "Food", "Culture", "Nightlife", "Temples"], "trips": 198},
    {"destination": "Singapore", "avg_budget": 120, "interests": ["City", "Food", "Shopping", "Culture", "Gardens"], "trips": 156},
    {"destination": "Dubai, UAE", "avg_budget": 150, "interests": ["Luxury", "Shopping", "Desert", "Beach", "Architecture"], "trips": 187},
    {"destination": "Phuket, Thailand", "avg_budget": 45, "interests": ["Beach", "Water Sports", "Nightlife", "Food", "Islands"], "trips": 167},
    {"destination": "Seoul, South Korea", "avg_budget": 75, "interests": ["City", "Culture", "Food", "Shopping", "K-pop"], "trips": 143},
    {"destination": "Maldives", "avg_budget": 200, "interests": ["Beach", "Luxury", "Diving", "Romance", "Relaxation"], "trips": 134},
    
    # Europe
    {"destination": "Paris, France", "avg_budget": 110, "interests": ["City", "Art", "Culture", "Food", "Romance"], "trips": 298},
    {"destination": "London, UK", "avg_budget": 130, "interests": ["City", "Culture", "History", "Shopping", "Museums"], "trips": 256},
    {"destination": "Rome, Italy", "avg_budget": 95, "interests": ["History", "Culture", "Food", "Architecture", "Art"], "trips": 223},
    {"destination": "Barcelona, Spain", "avg_budget": 85, "interests": ["Beach", "Architecture", "Culture", "Food", "Nightlife"], "trips": 201},
    {"destination": "Amsterdam, Netherlands", "avg_budget": 100, "interests": ["City", "Culture", "Cycling", "Museums", "Nightlife"], "trips": 178},
    {"destination": "Prague, Czech Republic", "avg_budget": 60, "interests": ["History", "Architecture", "Culture", "Nightlife", "Beer"], "trips": 145},
    {"destination": "Santorini, Greece", "avg_budget": 120, "interests": ["Beach", "Romance", "Relaxation", "Photography", "Wine"], "trips": 167},
    
    # Americas
    {"destination": "New York, USA", "avg_budget": 140, "interests": ["City", "Culture", "Shopping", "Food", "Entertainment"], "trips": 287},
    {"destination": "Cancun, Mexico", "avg_budget": 70, "interests": ["Beach", "Water Sports", "Nightlife", "History", "Food"], "trips": 189},
    {"destination": "Los Angeles, USA", "avg_budget": 130, "interests": ["City", "Beach", "Entertainment", "Shopping", "Food"], "trips": 176},
    {"destination": "Miami, USA", "avg_budget": 110, "interests": ["Beach", "Nightlife", "Food", "Water Sports", "Shopping"], "trips": 154},
    
    # Oceania
    {"destination": "Sydney, Australia", "avg_budget": 140, "interests": ["City", "Beach", "Harbor", "Culture", "Wildlife"], "trips": 198},
    {"destination": "Queenstown, New Zealand", "avg_budget": 120, "interests": ["Adventure", "Nature", "Skiing", "Hiking", "Lakes"], "trips": 112},
    
    # Africa & Middle East
    {"destination": "Cape Town, South Africa", "avg_budget": 75, "interests": ["Nature", "Adventure", "Wine", "Beach", "Wildlife"], "trips": 134},
    {"destination": "Marrakech, Morocco", "avg_budget": 55, "interests": ["Culture", "Markets", "History", "Food", "Desert"], "trips": 145},
    
    # India (popular domestic)
    {"destination": "Goa, India", "avg_budget": 35, "interests": ["Beach", "Nightlife", "Food", "Water Sports", "Culture"], "trips": 267},
    {"destination": "Jaipur, India", "avg_budget": 30, "interests": ["History", "Culture", "Architecture", "Shopping", "Food"], "trips": 198},
    {"destination": "Kerala, India", "avg_budget": 40, "interests": ["Nature", "Beach", "Culture", "Food", "Backwaters"], "trips": 223},
    {"destination": "Manali, India", "avg_budget": 35, "interests": ["Mountains", "Adventure", "Skiing", "Trekking", "Nature"], "trips": 189},
]

def seed_database():
    """Seed the database with sample trip data"""
    try:
        # Connect to MongoDB
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in .env file")
            return
        
        client = MongoClient(mongodb_uri)
        db = client['tripmate_db']
        trips_collection = db['trips']
        
        print("🌍 Seeding trending destinations data...")
        print(f"📊 Will create sample trips for {len(TRAVEL_DATASET)} destinations\n")
        
        # Clear existing sample data (optional - comment out to keep existing trips)
        # trips_collection.delete_many({"is_sample": True})
        
        total_trips_created = 0
        
        for dest_data in TRAVEL_DATASET:
            # Create a realistic number of trips (reduced for faster seeding)
            num_trips = min(dest_data['trips'], 20)  # Limit to 20 trips per destination for demo
            
            for i in range(num_trips):
                # Random date in the last 90 days
                days_ago = random.randint(1, 90)
                trip_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Random duration (3-14 days)
                duration = random.randint(3, 14)
                
                # Budget variation (±30%)
                budget_variation = random.uniform(0.7, 1.3)
                per_day_budget = int(dest_data['avg_budget'] * budget_variation)
                
                # Random interests (2-4 from available)
                num_interests = random.randint(2, min(4, len(dest_data['interests'])))
                trip_interests = random.sample(dest_data['interests'], num_interests)
                
                trip_doc = {
                    "user_id": f"sample_user_{random.randint(1, 100)}",
                    "destination": dest_data['destination'],
                    "start_date": trip_date,
                    "end_date": trip_date + timedelta(days=duration),
                    "duration": duration,
                    "budget": {
                        "per_day": per_day_budget,
                        "total": per_day_budget * duration
                    },
                    "interests": trip_interests,
                    "created_at": trip_date,
                    "is_sample": True  # Mark as sample data
                }
                
                trips_collection.insert_one(trip_doc)
                total_trips_created += 1
            
            print(f"✅ {dest_data['destination']:<30} - {num_trips} trips created")
        
        print(f"\n🎉 Successfully seeded {total_trips_created} sample trips!")
        print(f"📍 {len(TRAVEL_DATASET)} destinations now have trending data")
        print("\n💡 Refresh your browser to see real trending destinations!")
        
        # Show top 5 trending
        print("\n🔥 Top 5 Trending Destinations:")
        pipeline = [
            {"$group": {
                "_id": "$destination",
                "count": {"$sum": 1},
                "avg_budget": {"$avg": "$budget.per_day"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        top_destinations = list(trips_collection.aggregate(pipeline))
        for i, dest in enumerate(top_destinations, 1):
            print(f"   {i}. {dest['_id']:<35} ({dest['count']} trips, ${int(dest['avg_budget'])}/day)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("  TripMate - Trending Destinations Data Seeder")
    print("=" * 60)
    print()
    seed_database()
