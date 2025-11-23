"""
Trip Model - MongoDB Schema for Trip Itineraries
"""
from datetime import datetime
from bson import ObjectId


class Trip:
    """
    Trip model for storing finalized itineraries
    """
    
    def __init__(self, db):
        """
        Initialize Trip model with MongoDB collection
        
        Args:
            db: MongoDB database instance
        """
        self.collection = db.trips
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for performance"""
        try:
            self.collection.create_index([("user_id", 1), ("created_at", -1)])
            self.collection.create_index([("destination", 1)])
            self.collection.create_index([("travel_dates.start", 1)])
            self.collection.create_index([("metadata.trip_status", 1)])
            self.collection.create_index([("preferences.interests", 1)])
            self.collection.create_index([("budget.per_day", 1)])
        except Exception as e:
            print(f"⚠️  Index creation warning: {e}")
    
    def create_trip(self, user_id, trip_data):
        """
        Create a new trip (save finalized itinerary)
        
        Args:
            user_id: User ObjectId or string
            trip_data: dict with complete trip information
            
        Returns:
            dict: Created trip document
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Create trip document
        trip_doc = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "finalized_at": datetime.utcnow(),
            
            # Trip basics
            "destination": trip_data.get('destination', ''),
            "departure_city": trip_data.get('departure_city', ''),
            "duration_days": trip_data.get('duration_days', 0),
            "travel_dates": {
                "start": trip_data.get('start_date'),
                "end": trip_data.get('end_date')
            },
            
            # Budget info
            "budget": trip_data.get('budget', {}),
            
            # User preferences
            "preferences": trip_data.get('preferences', {}),
            
            # Trip components
            "flights": trip_data.get('flights', {}),
            "stays": trip_data.get('stays', []),
            "itinerary": trip_data.get('itinerary', []),
            "bookable_activities": trip_data.get('bookable_activities', []),
            
            # Metadata
            "metadata": {
                "weather_during_trip": trip_data.get('weather', ''),
                "season": trip_data.get('season', ''),
                "trip_status": "finalized",
                "shared_publicly": False,
                "user_rating": None,
                "user_feedback": None
            },
            
            # ML features for recommendations
            "ml_features": self._extract_ml_features(trip_data)
        }
        
        # Insert into database
        result = self.collection.insert_one(trip_doc)
        trip_doc['_id'] = result.inserted_id
        
        return trip_doc
    
    def _extract_ml_features(self, trip_data):
        """
        Extract ML features from trip data for recommendations
        
        Args:
            trip_data: dict with trip information
            
        Returns:
            dict: ML features
        """
        # Analyze interests distribution
        interests = trip_data.get('preferences', {}).get('interests', [])
        
        # Calculate activity type distribution
        itinerary = trip_data.get('itinerary', [])
        activity_counts = {}
        for day in itinerary:
            for activity in day.get('activities', []):
                activity_type = activity.get('type', 'other')
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        total_activities = sum(activity_counts.values())
        
        return {
            "destination_type": self._classify_destination_type(trip_data.get('destination', '')),
            "activity_diversity": len(activity_counts) / max(total_activities, 1),
            "budget_category": self._classify_budget(trip_data.get('budget', {}).get('per_day', 0)),
            "pace": self._classify_pace(total_activities, trip_data.get('duration_days', 1)),
            "food_focus": activity_counts.get('food', 0) / max(total_activities, 1),
            "adventure_focus": activity_counts.get('activity', 0) / max(total_activities, 1)
        }
    
    def _classify_destination_type(self, destination):
        """Classify destination type (Beach, City, Mountain, etc.)"""
        destination_lower = destination.lower()
        
        if any(word in destination_lower for word in ['bali', 'maldives', 'hawaii', 'phuket', 'cancun']):
            return "Beach + Culture"
        elif any(word in destination_lower for word in ['tokyo', 'paris', 'new york', 'london', 'dubai']):
            return "City + Culture"
        elif any(word in destination_lower for word in ['nepal', 'switzerland', 'colorado', 'patagonia']):
            return "Mountain + Adventure"
        else:
            return "Mixed"
    
    def _classify_budget(self, per_day_budget):
        """Classify budget category"""
        if per_day_budget < 50:
            return "budget"
        elif per_day_budget < 150:
            return "mid-range"
        else:
            return "premium"
    
    def _classify_pace(self, total_activities, duration_days):
        """Classify travel pace"""
        activities_per_day = total_activities / max(duration_days, 1)
        
        if activities_per_day < 3:
            return "slow"
        elif activities_per_day < 5:
            return "moderate"
        else:
            return "fast"
    
    def get_user_trips(self, user_id, limit=20, skip=0, status=None):
        """
        Get all trips for a user
        
        Args:
            user_id: User ObjectId or string
            limit: Maximum trips to return
            skip: Number to skip (pagination)
            status: Optional status filter (finalized, completed, etc.)
            
        Returns:
            list: Trip documents
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        query = {"user_id": user_id}
        if status:
            query["metadata.trip_status"] = status
        
        trips = list(self.collection.find(query)
                    .sort("created_at", -1)
                    .limit(limit)
                    .skip(skip))
        return trips
    
    def get_trip_by_id(self, trip_id, user_id=None):
        """
        Get specific trip by ID
        
        Args:
            trip_id: Trip ObjectId or string
            user_id: Optional user ID to verify ownership
            
        Returns:
            dict: Trip document or None
        """
        if isinstance(trip_id, str):
            trip_id = ObjectId(trip_id)
        
        query = {"_id": trip_id}
        if user_id:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            query["user_id"] = user_id
        
        return self.collection.find_one(query)
    
    def update_trip(self, trip_id, user_id, updates):
        """
        Update trip (e.g., mark as completed, add rating)
        
        Args:
            trip_id: Trip ObjectId or string
            user_id: User ObjectId or string (for ownership verification)
            updates: dict with fields to update
            
        Returns:
            bool: True if updated successfully
        """
        if isinstance(trip_id, str):
            trip_id = ObjectId(trip_id)
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.update_one(
            {"_id": trip_id, "user_id": user_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def delete_trip(self, trip_id, user_id):
        """
        Delete trip
        
        Args:
            trip_id: Trip ObjectId or string
            user_id: User ObjectId or string (for ownership verification)
            
        Returns:
            bool: True if deleted successfully
        """
        if isinstance(trip_id, str):
            trip_id = ObjectId(trip_id)
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.delete_one({
            "_id": trip_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    def get_popular_destinations(self, limit=10):
        """
        Get most popular destinations (for analytics)
        
        Args:
            limit: Number of destinations to return
            
        Returns:
            list: Destinations with trip counts
        """
        pipeline = [
            {"$group": {
                "_id": "$destination",
                "trips_count": {"$sum": 1},
                "avg_duration": {"$avg": "$duration_days"},
                "avg_budget": {"$avg": "$budget.per_day"}
            }},
            {"$sort": {"trips_count": -1}},
            {"$limit": limit}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results
    
    def get_similar_trips(self, user_id, interests, budget_range, limit=5):
        """
        Find similar trips for recommendations
        
        Args:
            user_id: Current user ID (to exclude own trips)
            interests: List of interests
            budget_range: Tuple (min, max) budget per day
            limit: Number of trips to return
            
        Returns:
            list: Similar trip documents
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        query = {
            "user_id": {"$ne": user_id},  # Exclude own trips
            "metadata.trip_status": "finalized",
            "preferences.interests": {"$in": interests},
            "budget.per_day": {
                "$gte": budget_range[0],
                "$lte": budget_range[1]
            }
        }
        
        trips = list(self.collection.find(query)
                    .sort("created_at", -1)
                    .limit(limit))
        return trips
