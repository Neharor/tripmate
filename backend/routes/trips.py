"""
Trip Management Routes
"""
from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from datetime import datetime
from routes.auth import login_required

trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

# Will be set by main.py
trip_model = None
user_model = None


def init_trips_routes(trip_model_instance, user_model_instance):
    """Initialize routes with model instances"""
    global trip_model, user_model
    trip_model = trip_model_instance
    user_model = user_model_instance


@trips_bp.route('', methods=['POST'])
@login_required
def create_trip():
    """
    Save finalized trip itinerary
    
    POST /api/trips
    Body: {
        "destination": "Bali, Indonesia",
        "departure_city": "Los Angeles",
        "duration_days": 5,
        "start_date": "2025-02-15",
        "end_date": "2025-02-20",
        "budget": { ... },
        "preferences": { ... },
        "flights": { ... },
        "stays": [ ... ],
        "itinerary": [ ... ],
        "bookable_activities": [ ... ]
    }
    """
    try:
        print("\n🔍 === TRIP SAVE REQUEST START ===")
        user_id = session.get('user_id')
        print(f"🔍 BACKEND: user_id from session: {user_id}")
        
        # Get JSON data with UTF-8 encoding
        trip_data = request.get_json(force=True)
        print(f"🔍 BACKEND: Raw request data type: {type(trip_data)}")
        
        # Clean any corrupted text in itinerary
        if 'itinerary' in trip_data and isinstance(trip_data['itinerary'], str):
            trip_data['itinerary'] = trip_data['itinerary'].encode('utf-8', 'ignore').decode('utf-8')
            print(f"🔍 BACKEND: Cleaned itinerary text encoding")
        print(f"🔍 BACKEND: Raw request data: {trip_data}")
        
        if not isinstance(trip_data, dict):
            print(f"❌ BACKEND: Expected dict, got {type(trip_data)}")
            return jsonify({"error": f"Invalid data format: expected object, got {type(trip_data).__name__}"}), 400
        
        print(f"🔍 BACKEND: trip_data keys: {list(trip_data.keys())}")
        
        # Check specific fields that might cause issues
        for key in ['itinerary', 'flights', 'stays', 'budget', 'preferences']:
            if key in trip_data:
                print(f"🔍 BACKEND: {key} type: {type(trip_data[key])}, value: {trip_data[key]}")
        
        # Convert date strings to datetime objects
        if 'start_date' in trip_data and isinstance(trip_data['start_date'], str):
            try:
                # Try ISO format first
                trip_data['start_date'] = datetime.fromisoformat(trip_data['start_date'].replace('Z', '+00:00'))
            except ValueError:
                # Try parsing common formats like "Nov 25", "Nov 25 2025", etc.
                from dateutil import parser
                trip_data['start_date'] = parser.parse(trip_data['start_date'])
        
        if 'end_date' in trip_data and isinstance(trip_data['end_date'], str):
            try:
                trip_data['end_date'] = datetime.fromisoformat(trip_data['end_date'].replace('Z', '+00:00'))
            except ValueError:
                from dateutil import parser
                trip_data['end_date'] = parser.parse(trip_data['end_date'])
        
        # Create trip
        print(f"🔍 BACKEND: About to call trip_model.create_trip with user_id={user_id}")
        print(f"🔍 BACKEND: trip_model type: {type(trip_model)}")
        print(f"🔍 BACKEND: Processed trip_data keys: {list(trip_data.keys())}")
        
        trip = trip_model.create_trip(user_id, trip_data)
        print(f"🔍 BACKEND: Trip created successfully with id: {trip.get('_id')}")
        
        # Update user stats
        user_model.update_stats(user_id, trip_data)
        
        return jsonify({
            "message": "Trip saved successfully! 🎉",
            "trip": {
                "id": str(trip['_id']),
                "destination": trip['destination'],
                "dates": {
                    "start": trip['travel_dates']['start'].isoformat() if trip['travel_dates']['start'] else None,
                    "end": trip['travel_dates']['end'].isoformat() if trip['travel_dates']['end'] else None
                },
                "duration_days": trip['duration_days']
            }
        }), 201
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR creating trip: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Full traceback:")
        print(traceback.format_exc())
        print("🔍 === TRIP SAVE REQUEST END (ERROR) ===\n")
        return jsonify({"error": f"Failed to save trip: {str(e)}"}), 500


@trips_bp.route('', methods=['GET'])
# @login_required  # Temporarily disabled for development/testing
def get_trips():
    """
    Get all trips for current user
    
    GET /api/trips?limit=20&skip=0&status=finalized
    """
    try:
        user_id = session.get('user_id')
        
        # DEVELOPMENT: If no user session, return empty trips for testing
        if not user_id:
            print("🔍 DEV MODE: No user session, returning empty trips for testing")
            return jsonify({
                "trips": [],
                "total": 0,
                "message": "No user session - development mode"
            }), 200
        
        # Query parameters
        limit = int(request.args.get('limit', 20))
        skip = int(request.args.get('skip', 0))
        status = request.args.get('status')
        
        # Get trips
        trips = trip_model.get_user_trips(user_id, limit=limit, skip=skip, status=status)
        
        # Format response
        trips_list = []
        for trip in trips:
            trips_list.append({
                "id": str(trip['_id']),
                "destination": trip['destination'],
                "departure_city": trip.get('departure_city', ''),
                "duration_days": trip['duration_days'],
                "dates": {
                    "start": trip['travel_dates']['start'].isoformat() if trip['travel_dates'].get('start') else None,
                    "end": trip['travel_dates']['end'].isoformat() if trip['travel_dates'].get('end') else None
                },
                "budget": trip.get('budget', {}),
                "status": trip['metadata']['trip_status'],
                "created_at": trip['created_at'].isoformat(),
                "itinerary": trip.get('itinerary', []),
                "interests": trip.get('preferences', {}).get('interests', [])
            })
        
        return jsonify({
            "trips": trips_list,
            "count": len(trips_list)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting trips: {str(e)}")
        # Return empty array instead of error to avoid breaking frontend
        return jsonify({
            "trips": [],
            "count": 0,
            "error": "Database connection issue. Please try again later."
        }), 200


@trips_bp.route('/<trip_id>', methods=['GET'])
@login_required
def get_trip(trip_id):
    """
    Get specific trip by ID
    
    GET /api/trips/:trip_id
    """
    try:
        user_id = session.get('user_id')
        
        # Get trip
        trip = trip_model.get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        
        # Convert ObjectId to string
        trip['_id'] = str(trip['_id'])
        trip['user_id'] = str(trip['user_id'])
        
        # Convert dates to ISO format
        if trip['travel_dates'].get('start'):
            trip['travel_dates']['start'] = trip['travel_dates']['start'].isoformat()
        if trip['travel_dates'].get('end'):
            trip['travel_dates']['end'] = trip['travel_dates']['end'].isoformat()
        trip['created_at'] = trip['created_at'].isoformat()
        if trip.get('finalized_at'):
            trip['finalized_at'] = trip['finalized_at'].isoformat()
        
        return jsonify(trip), 200
        
    except Exception as e:
        print(f"❌ Error getting trip: {str(e)}")
        return jsonify({"error": f"Failed to get trip: {str(e)}"}), 500


@trips_bp.route('/<trip_id>', methods=['PUT'])
@login_required
def update_trip(trip_id):
    """
    Update trip (e.g., mark as completed, add rating)
    
    PUT /api/trips/:trip_id
    Body: {
        "metadata.trip_status": "completed",
        "metadata.user_rating": 5,
        "metadata.user_feedback": "Amazing trip!"
    }
    """
    try:
        user_id = session.get('user_id')
        updates = request.get_json()
        
        # Update trip
        success = trip_model.update_trip(trip_id, user_id, updates)
        
        if success:
            return jsonify({"message": "Trip updated successfully"}), 200
        else:
            return jsonify({"error": "Update failed or trip not found"}), 404
            
    except Exception as e:
        print(f"❌ Error updating trip: {str(e)}")
        return jsonify({"error": f"Failed to update trip: {str(e)}"}), 500


@trips_bp.route('/<trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    """
    Delete trip
    
    DELETE /api/trips/:trip_id
    """
    try:
        user_id = session.get('user_id')
        
        # Delete trip
        success = trip_model.delete_trip(trip_id, user_id)
        
        if success:
            return jsonify({"message": "Trip deleted successfully"}), 200
        else:
            return jsonify({"error": "Delete failed or trip not found"}), 404
            
    except Exception as e:
        print(f"❌ Error deleting trip: {str(e)}")
        return jsonify({"error": f"Failed to delete trip: {str(e)}"}), 500


@trips_bp.route('/<trip_id>/share', methods=['POST'])
@login_required
def share_trip(trip_id):
    """
    Generate shareable link for trip
    
    POST /api/trips/:trip_id/share
    """
    try:
        user_id = session.get('user_id')
        
        # Verify ownership
        trip = trip_model.get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        
        # Update trip to make it publicly shareable
        trip_model.update_trip(trip_id, user_id, {
            "metadata.shared_publicly": True
        })
        
        # Generate shareable URL
        share_url = f"https://tripmate.com/shared/{trip_id}"
        
        return jsonify({
            "message": "Trip is now shareable!",
            "share_url": share_url
        }), 200
        
    except Exception as e:
        print(f"❌ Error sharing trip: {str(e)}")
        return jsonify({"error": f"Failed to share trip: {str(e)}"}), 500
