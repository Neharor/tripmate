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
        print(f"\n🔍 TRIP MODEL: create_trip called")
        print(f"🔍 TRIP MODEL: user_id type: {type(user_id)}, value: {user_id}")
        print(f"🔍 TRIP MODEL: trip_data type: {type(trip_data)}")
        
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
            print(f"🔍 TRIP MODEL: Converted user_id to ObjectId: {user_id}")
        
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
            "ml_features": self._extract_ml_features_with_logging(trip_data)
        }
        
        print(f"🔍 TRIP MODEL: About to insert trip document into MongoDB")
        print(f"🔍 TRIP MODEL: trip_doc keys: {list(trip_doc.keys())}")
        
        # Insert into database
        result = self.collection.insert_one(trip_doc)
        trip_doc['_id'] = result.inserted_id
        
        print(f"🔍 TRIP MODEL: Trip inserted successfully with _id: {result.inserted_id}")
        return trip_doc
    
    def _extract_ml_features_with_logging(self, trip_data):
        """Wrapper for _extract_ml_features with logging"""
        print(f"🔍 TRIP MODEL: _extract_ml_features_with_logging called")
        try:
            features = self._extract_ml_features(trip_data)
            print(f"🔍 TRIP MODEL: ML features extracted successfully: {features}")
            return features
        except Exception as e:
            print(f"❌ TRIP MODEL: Error in _extract_ml_features: {str(e)}")
            print(f"❌ TRIP MODEL: trip_data causing error: {trip_data}")
            raise
    
    def _extract_ml_features(self, trip_data):
        """
        Extract ML features from trip data for recommendations
        
        Args:
            trip_data: dict with trip information
            
        Returns:
            dict: ML features
        """
        print(f"🔍 ML FEATURES: Starting extraction")
        print(f"🔍 ML FEATURES: trip_data type: {type(trip_data)}")
        
        # Analyze interests distribution
        preferences = trip_data.get('preferences', {})
        print(f"🔍 ML FEATURES: preferences type: {type(preferences)}, value: {preferences}")
        
        if isinstance(preferences, dict):
            interests = preferences.get('interests', [])
        else:
            print(f"❌ ML FEATURES: preferences is not a dict, it's {type(preferences)}")
            interests = []
        
        print(f"🔍 ML FEATURES: interests: {interests}")
        
        # Calculate activity type distribution
        itinerary = trip_data.get('itinerary', [])
        print(f"🔍 ML FEATURES: itinerary type: {type(itinerary)}, value: {itinerary}")
        
        activity_counts = {}
        if isinstance(itinerary, list):
            for i, day in enumerate(itinerary):
                print(f"🔍 ML FEATURES: Processing day {i}, type: {type(day)}, value: {day}")
                if isinstance(day, dict):
                    activities = day.get('activities', [])
                    print(f"🔍 ML FEATURES: Day {i} activities type: {type(activities)}, value: {activities}")
                    
                    if isinstance(activities, list):
                        for j, activity in enumerate(activities):
                            print(f"🔍 ML FEATURES: Activity {j} type: {type(activity)}, value: {activity}")
                            # Handle both string activities and dict activities with type
                            if isinstance(activity, dict):
                                activity_type = activity.get('type', 'other')
                            else:
                                # If activity is a string, classify it based on keywords
                                activity_type = self._classify_activity_type(str(activity))
                            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
                    else:
                        print(f"❌ ML FEATURES: activities is not a list, it's {type(activities)}")
                else:
                    print(f"❌ ML FEATURES: day is not a dict, it's {type(day)}")
        else:
            print(f"❌ ML FEATURES: itinerary is not a list, it's {type(itinerary)}")
        
        total_activities = sum(activity_counts.values())
        print(f"🔍 ML FEATURES: activity_counts: {activity_counts}")
        print(f"🔍 ML FEATURES: total_activities: {total_activities}")
        
        # Process budget safely
        budget = trip_data.get('budget', {})
        print(f"🔍 ML FEATURES: budget type: {type(budget)}, value: {budget}")
        
        if isinstance(budget, dict):
            per_day_budget = budget.get('per_day', 0)
        else:
            print(f"❌ ML FEATURES: budget is not a dict, it's {type(budget)}")
            per_day_budget = 0
        
        print(f"🔍 ML FEATURES: per_day_budget: {per_day_budget}")
        
        destination = trip_data.get('destination', '')
        duration_days = trip_data.get('duration_days', 1)
        
        print(f"🔍 ML FEATURES: destination: {destination}")
        print(f"🔍 ML FEATURES: duration_days: {duration_days}")
        
        features = {
            "destination_type": self._classify_destination_type(destination),
            "activity_diversity": len(activity_counts) / max(total_activities, 1),
            "budget_category": self._classify_budget(per_day_budget),
            "pace": self._classify_pace(total_activities, duration_days),
            "food_focus": activity_counts.get('food', 0) / max(total_activities, 1),
            "adventure_focus": activity_counts.get('activity', 0) / max(total_activities, 1)
        }
        
        print(f"🔍 ML FEATURES: Final features: {features}")
        return features
    
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
    
    def _classify_activity_type(self, activity_str):
        """Classify activity type based on text content"""
        activity_lower = activity_str.lower()
        
        if any(word in activity_lower for word in ['eat', 'restaurant', 'food', 'dining', 'cook', 'market']):
            return "food"
        elif any(word in activity_lower for word in ['museum', 'temple', 'culture', 'historic', 'art', 'gallery']):
            return "culture"
        elif any(word in activity_lower for word in ['hike', 'climb', 'adventure', 'sport', 'activity', 'trek']):
            return "activity"
        elif any(word in activity_lower for word in ['shop', 'shopping', 'market', 'store', 'buy']):
            return "shopping"
        elif any(word in activity_lower for word in ['relax', 'spa', 'beach', 'rest', 'chill']):
            return "relaxation"
        elif any(word in activity_lower for word in ['night', 'bar', 'club', 'party', 'drink']):
            return "nightlife"
        else:
            return "other"
    
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
