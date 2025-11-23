"""
Trip management service
Handles trip CRUD operations and personalized recommendations
"""

from datetime import datetime
from database.models import Trip, Booking, Itinerary, UserActivity, get_session
from sqlalchemy import desc


def create_trip(user_id, trip_data):
    """Create a new trip from conversation data"""
    session = get_session()
    
    try:
        # Extract trip details
        trip = Trip(
            user_id=user_id,
            destination=trip_data.get('destination'),
            departure_city=trip_data.get('departure_city'),
            start_date=trip_data.get('start_date'),
            end_date=trip_data.get('end_date'),
            duration=trip_data.get('duration'),
            budget_total=trip_data.get('budget_total'),
            budget_per_day=trip_data.get('budget_per_day'),
            status='planned',
            interests=trip_data.get('interests', []),
            food_preference=trip_data.get('food_preference'),
            companions=trip_data.get('companions'),
            metadata=trip_data.get('metadata', {})
        )
        
        session.add(trip)
        session.commit()
        
        # Log activity
        log_user_activity(user_id, 'create_trip', {'trip_id': trip.id, 'destination': trip.destination})
        
        return {
            'message': 'Trip created successfully',
            'trip': trip.to_dict()
        }, 201
        
    except Exception as e:
        session.rollback()
        return {'error': str(e)}, 500
    finally:
        session.close()


def get_user_trips(user_id, status=None):
    """Get all trips for a user"""
    session = get_session()
    
    try:
        query = session.query(Trip).filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        trips = query.order_by(desc(Trip.created_at)).all()
        
        return {
            'trips': [trip.to_dict() for trip in trips]
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        session.close()


def get_trip_details(user_id, trip_id):
    """Get detailed trip information including bookings and itinerary"""
    session = get_session()
    
    try:
        trip = session.query(Trip).filter_by(id=trip_id, user_id=user_id).first()
        
        if not trip:
            return {'error': 'Trip not found'}, 404
        
        trip_data = trip.to_dict()
        
        # Include bookings
        trip_data['bookings'] = [b.to_dict() for b in trip.bookings]
        
        # Include itinerary
        trip_data['itinerary'] = [i.to_dict() for i in trip.itineraries]
        
        return trip_data, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        session.close()


def save_booking(user_id, trip_id, booking_data):
    """Save a booking (hotel, flight, or activity)"""
    session = get_session()
    
    try:
        # Verify trip belongs to user
        trip = session.query(Trip).filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return {'error': 'Trip not found'}, 404
        
        booking = Booking(
            trip_id=trip_id,
            user_id=user_id,
            booking_type=booking_data.get('booking_type'),
            provider=booking_data.get('provider'),
            name=booking_data.get('name'),
            description=booking_data.get('description'),
            price=booking_data.get('price'),
            currency=booking_data.get('currency', 'USD'),
            booking_date=booking_data.get('booking_date'),
            status='saved',
            booking_url=booking_data.get('booking_url'),
            booking_details=booking_data.get('booking_details', {})
        )
        
        session.add(booking)
        session.commit()
        
        # Log activity
        log_user_activity(user_id, f'save_{booking.booking_type}', {
            'trip_id': trip_id,
            'booking_id': booking.id,
            'name': booking.name,
            'price': float(booking.price) if booking.price else None
        })
        
        return {
            'message': 'Booking saved successfully',
            'booking': booking.to_dict()
        }, 201
        
    except Exception as e:
        session.rollback()
        return {'error': str(e)}, 500
    finally:
        session.close()


def get_personalized_recommendations(user_id):
    """Generate recommendations based on user's past trips and preferences"""
    session = get_session()
    
    try:
        user_trips = session.query(Trip).filter_by(user_id=user_id).all()
        
        if not user_trips:
            return {
                'recommendations': [],
                'message': 'No past trips to base recommendations on'
            }, 200
        
        # Analyze past trips
        destinations_visited = set()
        preferred_budgets = []
        all_interests = []
        food_prefs = []
        
        for trip in user_trips:
            if trip.destination:
                destinations_visited.add(trip.destination)
            if trip.budget_per_day:
                preferred_budgets.append(float(trip.budget_per_day))
            if trip.interests:
                all_interests.extend(trip.interests)
            if trip.food_preference:
                food_prefs.append(trip.food_preference)
        
        # Calculate average budget
        avg_budget = sum(preferred_budgets) / len(preferred_budgets) if preferred_budgets else None
        
        # Most common interests
        from collections import Counter
        interest_counts = Counter(all_interests)
        top_interests = [interest for interest, count in interest_counts.most_common(3)]
        
        # Most common food preference
        food_pref_counts = Counter(food_prefs)
        common_food_pref = food_pref_counts.most_common(1)[0][0] if food_pref_counts else None
        
        recommendations = {
            'profile': {
                'destinations_visited': list(destinations_visited),
                'total_trips': len(user_trips),
                'average_budget': round(avg_budget, 2) if avg_budget else None,
                'top_interests': top_interests,
                'food_preference': common_food_pref
            },
            'suggested_destinations': _get_similar_destinations(destinations_visited, top_interests),
            'budget_range': {
                'min': round(avg_budget * 0.8, 2) if avg_budget else 50,
                'max': round(avg_budget * 1.2, 2) if avg_budget else 200
            }
        }
        
        return recommendations, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        session.close()


def _get_similar_destinations(visited, interests):
    """Recommend similar destinations based on past visits and interests"""
    # This is a simple example - in production, use ML or a proper recommendation engine
    
    destination_map = {
        ('Bali, Indonesia',): ['Phuket, Thailand', 'Maldives', 'Boracay, Philippines'],
        ('Bangkok, Thailand',): ['Ho Chi Minh, Vietnam', 'Singapore', 'Kuala Lumpur, Malaysia'],
        ('Paris, France',): ['Rome, Italy', 'Barcelona, Spain', 'Amsterdam, Netherlands'],
        ('Tokyo, Japan',): ['Seoul, South Korea', 'Taipei, Taiwan', 'Hong Kong'],
        ('New York, USA',): ['London, UK', 'Toronto, Canada', 'Chicago, USA']
    }
    
    suggestions = []
    for dest in visited:
        for key, values in destination_map.items():
            if dest in key:
                suggestions.extend(values)
    
    # Remove duplicates and visited destinations
    suggestions = list(set(suggestions) - visited)
    
    return suggestions[:5]  # Return top 5


def log_user_activity(user_id, activity_type, activity_data):
    """Log user activity for analytics"""
    session = get_session()
    
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=activity_data
        )
        
        session.add(activity)
        session.commit()
        
    except Exception as e:
        print(f"Error logging activity: {e}")
        session.rollback()
    finally:
        session.close()


def update_trip_status(user_id, trip_id, status):
    """Update trip status (planned -> ongoing -> completed)"""
    session = get_session()
    
    try:
        trip = session.query(Trip).filter_by(id=trip_id, user_id=user_id).first()
        
        if not trip:
            return {'error': 'Trip not found'}, 404
        
        valid_statuses = ['planned', 'ongoing', 'completed', 'cancelled']
        if status not in valid_statuses:
            return {'error': f'Invalid status. Must be one of: {valid_statuses}'}, 400
        
        trip.status = status
        trip.updated_at = datetime.utcnow()
        session.commit()
        
        # Log activity
        log_user_activity(user_id, 'update_trip_status', {
            'trip_id': trip_id,
            'new_status': status
        })
        
        return {
            'message': 'Trip status updated successfully',
            'trip': trip.to_dict()
        }, 200
        
    except Exception as e:
        session.rollback()
        return {'error': str(e)}, 500
    finally:
        session.close()
