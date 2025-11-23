"""
User Model - MongoDB Schema for User Profiles
"""
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """
    User model for storing user profiles and preferences
    """
    
    def __init__(self, db):
        """
        Initialize User model with MongoDB collection
        
        Args:
            db: MongoDB database instance
        """
        self.collection = db.users
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for performance"""
        try:
            self.collection.create_index("email", unique=True)
            self.collection.create_index([("created_at", -1)])
        except Exception as e:
            print(f"⚠️  Index creation warning: {e}")
    
    def create_user(self, email, password, name=None):
        """
        Create a new user
        
        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            name: Optional display name
            
        Returns:
            dict: Created user document (without password)
        """
        # Check if user already exists
        if self.find_by_email(email):
            raise ValueError("User with this email already exists")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create user document
        user_doc = {
            "email": email,
            "password_hash": password_hash,
            "name": name or email.split('@')[0],
            "created_at": datetime.utcnow(),
            "preferences": {
                "favorite_destinations": [],
                "interests": [],
                "budget_range": None,
                "food_preference": None,
                "travel_style": None
            },
            "stats": {
                "total_trips": 0,
                "countries_visited": 0,
                "total_spent": 0
            }
        }
        
        # Insert into database
        result = self.collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        
        # Remove password hash before returning
        del user_doc['password_hash']
        return user_doc
    
    def find_by_email(self, email):
        """
        Find user by email
        
        Args:
            email: User email
            
        Returns:
            dict: User document or None
        """
        return self.collection.find_one({"email": email})
    
    def find_by_id(self, user_id):
        """
        Find user by ID
        
        Args:
            user_id: User ObjectId or string
            
        Returns:
            dict: User document (without password) or None
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        user = self.collection.find_one({"_id": user_id})
        if user and 'password_hash' in user:
            del user['password_hash']
        return user
    
    def verify_password(self, email, password):
        """
        Verify user password
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            dict: User document (without password) if valid, None otherwise
        """
        user = self.find_by_email(email)
        if not user:
            return None
        
        if check_password_hash(user['password_hash'], password):
            del user['password_hash']
            return user
        
        return None
    
    def update_preferences(self, user_id, preferences):
        """
        Update user preferences
        
        Args:
            user_id: User ObjectId or string
            preferences: dict with preference updates
            
        Returns:
            bool: True if updated successfully
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.update_one(
            {"_id": user_id},
            {"$set": {"preferences": preferences}}
        )
        return result.modified_count > 0
    
    def update_stats(self, user_id, trip_data):
        """
        Update user stats after trip creation
        
        Args:
            user_id: User ObjectId or string
            trip_data: dict with trip information
            
        Returns:
            bool: True if updated successfully
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Extract relevant info from trip
        destination = trip_data.get('destination', '')
        total_cost = trip_data.get('budget', {}).get('actual_total', 0)
        
        # Update stats
        result = self.collection.update_one(
            {"_id": user_id},
            {
                "$inc": {
                    "stats.total_trips": 1,
                    "stats.total_spent": total_cost
                },
                "$addToSet": {
                    "preferences.favorite_destinations": destination
                }
            }
        )
        return result.modified_count > 0
    
    def get_all_users(self, limit=100, skip=0):
        """
        Get all users (admin function)
        
        Args:
            limit: Maximum number of users to return
            skip: Number of users to skip (pagination)
            
        Returns:
            list: User documents (without passwords)
        """
        users = list(self.collection.find(
            {},
            {"password_hash": 0}  # Exclude password hash
        ).limit(limit).skip(skip))
        return users
    
    def delete_user(self, user_id):
        """
        Delete user account (GDPR compliance)
        
        Args:
            user_id: User ObjectId or string
            
        Returns:
            bool: True if deleted successfully
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
