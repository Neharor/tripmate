"""
API routes for trip management
"""

from flask import Blueprint, request, jsonify
from services.auth import token_required
from services.trip_service import (
    create_trip,
    get_user_trips,
    get_trip_details,
    save_booking,
    get_personalized_recommendations,
    update_trip_status
)

trip_bp = Blueprint('trips', __name__)


@trip_bp.route('', methods=['POST'])
@token_required
def create():
    """
    Create a new trip
    
    Headers:
    Authorization: Bearer <token>
    
    Request body:
    {
        "destination": "Bali, Indonesia",
        "departure_city": "Bangkok, Thailand",
        "start_date": "2025-12-25",
        "end_date": "2025-12-30",
        "duration": 5,
        "budget_per_day": 200,
        "budget_total": 1000,
        "interests": ["beach", "food", "adventure"],
        "food_preference": "non-vegetarian",
        "companions": "couple"
    }
    """
    data = request.get_json()
    
    # DEBUG
    print(f"\n🔍 DEBUG ROUTE: request.data type = {type(request.data)}")
    print(f"🔍 DEBUG ROUTE: request.data = {request.data[:200] if request.data else 'None'}")
    print(f"🔍 DEBUG ROUTE: data type = {type(data)}")
    print(f"🔍 DEBUG ROUTE: data = {str(data)[:200] if data else 'None'}")
    
    # FIX: If data is a string, try to parse it as JSON
    if isinstance(data, str):
        print(f"⚠️ WARNING: data is a string, attempting to parse as JSON")
        import json
        try:
            data = json.loads(data)
            print(f"✅ Successfully parsed string to dict")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return jsonify({'error': 'Invalid JSON data'}), 400
    
    if not data or not data.get('destination'):
        return jsonify({'error': 'Destination is required'}), 400
    
    print(f"🔍 DEBUG ROUTE: Calling create_trip with user_id={request.user_id}")
    result, status = create_trip(request.user_id, data)
    return jsonify(result), status


@trip_bp.route('', methods=['GET'])
@token_required
def list_trips():
    """
    Get all trips for the authenticated user
    
    Query params:
    - status: Filter by status (planned, ongoing, completed, cancelled)
    
    Headers:
    Authorization: Bearer <token>
    """
    status_filter = request.args.get('status')
    result, status = get_user_trips(request.user_id, status_filter)
    return jsonify(result), status


@trip_bp.route('/<int:trip_id>', methods=['GET'])
@token_required
def trip_details(trip_id):
    """
    Get detailed trip information
    
    Headers:
    Authorization: Bearer <token>
    """
    result, status = get_trip_details(request.user_id, trip_id)
    return jsonify(result), status


@trip_bp.route('/<int:trip_id>/status', methods=['PUT'])
@token_required
def update_status(trip_id):
    """
    Update trip status
    
    Headers:
    Authorization: Bearer <token>
    
    Request body:
    {
        "status": "completed"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': 'Status is required'}), 400
    
    result, status = update_trip_status(request.user_id, trip_id, data['status'])
    return jsonify(result), status


@trip_bp.route('/<int:trip_id>/bookings', methods=['POST'])
@token_required
def add_booking(trip_id):
    """
    Save a booking to a trip
    
    Headers:
    Authorization: Bearer <token>
    
    Request body:
    {
        "booking_type": "hotel",
        "provider": "Booking.com",
        "name": "The Griya Villas and Spa",
        "description": "Luxury villa with pool",
        "price": 450,
        "currency": "USD",
        "booking_url": "https://booking.com/...",
        "booking_details": {
            "check_in": "2025-12-25",
            "check_out": "2025-12-30",
            "nights": 5
        }
    }
    """
    data = request.get_json()
    
    if not data or not data.get('booking_type') or not data.get('name'):
        return jsonify({'error': 'booking_type and name are required'}), 400
    
    result, status = save_booking(request.user_id, trip_id, data)
    return jsonify(result), status


@trip_bp.route('/recommendations', methods=['GET'])
@token_required
def recommendations():
    """
    Get personalized recommendations based on past trips
    
    Headers:
    Authorization: Bearer <token>
    """
    result, status = get_personalized_recommendations(request.user_id)
    return jsonify(result), status
