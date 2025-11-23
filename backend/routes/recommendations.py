"""
Recommendations Routes - Personalized trip recommendations based on user history
"""
from flask import Blueprint, request, jsonify, session
from routes.auth import login_required

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

# Will be set by main.py
trip_model = None
user_model = None


def init_recommendations_routes(trip_model_instance, user_model_instance):
    """Initialize routes with model instances"""
    global trip_model, user_model
    trip_model = trip_model_instance
    user_model = user_model_instance


@recommendations_bp.route('', methods=['GET'])
@login_required
def get_recommendations():
    """
    Get personalized destination recommendations
    
    GET /api/recommendations?limit=5
    """
    try:
        user_id = session.get('user_id')
        limit = int(request.args.get('limit', 5))
        
        # Get user profile
        user = user_model.find_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get user's trip history
        user_trips = trip_model.get_user_trips(user_id, limit=100)
        
        # Extract user preferences
        interests = user.get('preferences', {}).get('interests', [])
        budget_range = _parse_budget_range(user.get('preferences', {}).get('budget_range'))
        
        # Find similar trips from other users
        similar_trips = trip_model.get_similar_trips(
            user_id=user_id,
            interests=interests if interests else ["Adventure", "Culture"],
            budget_range=budget_range,
            limit=20
        )
        
        # Generate recommendations based on similar trips
        recommendations = _generate_recommendations(user, user_trips, similar_trips, limit)
        
        return jsonify({
            "recommendations": recommendations,
            "based_on": {
                "interests": interests,
                "budget_range": user.get('preferences', {}).get('budget_range'),
                "trips_analyzed": len(similar_trips)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {str(e)}")
        return jsonify({"error": f"Failed to get recommendations: {str(e)}"}), 500


@recommendations_bp.route('/popular', methods=['GET'])
def get_popular_destinations():
    """
    Get most popular destinations (public endpoint)
    
    GET /api/recommendations/popular?limit=10
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        # Get popular destinations
        popular = trip_model.get_popular_destinations(limit=limit)
        
        # Format response
        destinations = []
        for dest in popular:
            destinations.append({
                "destination": dest['_id'],
                "trips_count": dest['trips_count'],
                "avg_duration": round(dest.get('avg_duration', 0), 1),
                "avg_budget": round(dest.get('avg_budget', 0))
            })
        
        return jsonify({
            "popular_destinations": destinations
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting popular destinations: {str(e)}")
        return jsonify({"error": f"Failed to get popular destinations: {str(e)}"}), 500


def _parse_budget_range(budget_str):
    """
    Parse budget range string to tuple
    
    Args:
        budget_str: e.g., "$100-200/day"
        
    Returns:
        tuple: (min, max) or (0, 999999)
    """
    if not budget_str:
        return (0, 999999)
    
    try:
        # Extract numbers from string like "$100-200/day"
        import re
        numbers = re.findall(r'\d+', budget_str)
        if len(numbers) >= 2:
            return (int(numbers[0]), int(numbers[1]))
        elif len(numbers) == 1:
            budget = int(numbers[0])
            return (budget * 0.8, budget * 1.2)
        else:
            return (0, 999999)
    except:
        return (0, 999999)


def _generate_recommendations(user, user_trips, similar_trips, limit):
    """
    Generate personalized recommendations based on user history and similar users
    
    Args:
        user: User document
        user_trips: List of user's trips
        similar_trips: List of trips from similar users
        limit: Number of recommendations to return
        
    Returns:
        list: Recommended destinations with confidence scores
    """
    recommendations = []
    
    # Extract destinations user has already visited
    visited_destinations = set([trip['destination'] for trip in user_trips])
    
    # Count destination occurrences in similar trips
    destination_counts = {}
    destination_data = {}
    
    for trip in similar_trips:
        dest = trip['destination']
        
        # Skip if user already visited
        if dest in visited_destinations:
            continue
        
        # Count occurrence
        destination_counts[dest] = destination_counts.get(dest, 0) + 1
        
        # Store trip data for this destination
        if dest not in destination_data:
            destination_data[dest] = {
                'total_cost': [],
                'durations': [],
                'interests': set()
            }
        
        destination_data[dest]['total_cost'].append(trip.get('budget', {}).get('actual_total', 0))
        destination_data[dest]['durations'].append(trip['duration_days'])
        destination_data[dest]['interests'].update(trip.get('preferences', {}).get('interests', []))
    
    # Sort destinations by popularity
    sorted_destinations = sorted(destination_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Generate recommendations
    for dest, count in sorted_destinations[:limit]:
        data = destination_data[dest]
        
        # Calculate confidence score (0-100)
        confidence = min(100, (count / len(similar_trips)) * 100 + 50)
        
        # Calculate average cost
        avg_cost = sum(data['total_cost']) / len(data['total_cost']) if data['total_cost'] else 0
        
        # Calculate average duration
        avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 5
        
        # Generate reasons
        reasons = []
        
        # Check interest overlap
        user_interests = set(user.get('preferences', {}).get('interests', []))
        common_interests = user_interests.intersection(data['interests'])
        if common_interests:
            reasons.append(f"Matches your interests: {', '.join(list(common_interests)[:2])}")
        
        # Popularity reason
        reasons.append(f"{count} similar travelers loved this destination")
        
        # Budget reason
        user_budget_str = user.get('preferences', {}).get('budget_range', '')
        if user_budget_str:
            reasons.append(f"Within your budget range")
        
        recommendations.append({
            "destination": dest,
            "confidence_score": round(confidence, 1),
            "reasons": reasons,
            "estimated_cost": {
                "total": round(avg_cost),
                "per_day": round(avg_cost / avg_duration) if avg_duration > 0 else 0
            },
            "avg_duration_days": round(avg_duration, 1),
            "based_on_trips": count
        })
    
    # If not enough recommendations, add popular destinations
    if len(recommendations) < limit:
        popular = trip_model.get_popular_destinations(limit=limit - len(recommendations))
        for dest in popular:
            if dest['_id'] not in visited_destinations and dest['_id'] not in [r['destination'] for r in recommendations]:
                recommendations.append({
                    "destination": dest['_id'],
                    "confidence_score": 60.0,
                    "reasons": [
                        f"Popular destination ({dest['trips_count']} trips)",
                        "Highly rated by travelers"
                    ],
                    "estimated_cost": {
                        "total": round(dest.get('avg_budget', 0) * dest.get('avg_duration', 5)),
                        "per_day": round(dest.get('avg_budget', 0))
                    },
                    "avg_duration_days": round(dest.get('avg_duration', 5), 1),
                    "based_on_trips": dest['trips_count']
                })
    
    return recommendations[:limit]
