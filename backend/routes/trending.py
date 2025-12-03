from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sys
from pathlib import Path

# Add ml directory to path
sys.path.append(str(Path(__file__).parent.parent / 'ml'))

try:
    from kaggle_trending import KaggleTrendingDestinations
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False
    print("⚠️ Kaggle trending module not available")

trending_bp = Blueprint('trending', __name__)

def init_trending_routes(trip_model):
    """Initialize trending routes with database models"""
    
    @trending_bp.route('/api/trending-destinations', methods=['GET'])
    def get_trending_destinations():
        """Get trending destinations based on Kaggle travel dataset + user trip data"""
        try:
            # Option 1: Use Kaggle dataset (Primary)
            if KAGGLE_AVAILABLE:
                print("📊 Using Kaggle dataset for trending destinations")
                analyzer = KaggleTrendingDestinations()
                kaggle_trending = analyzer.get_trending_destinations(top_n=12, days=90)
                
                return jsonify({
                    'success': True,
                    'destinations': kaggle_trending,
                    'data_source': 'kaggle',
                    'total_trips_analyzed': sum(d['trip_count'] for d in kaggle_trending)
                }), 200
            
            # Option 2: Fallback to MongoDB user data
            print("📊 Using MongoDB user trips for trending destinations")
            # Get all trips from the last 90 days
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            # Aggregate trips by destination
            destination_stats = defaultdict(lambda: {
                'count': 0,
                'total_budget': 0,
                'budgets': [],
                'interests': set(),
                'recent_date': None
            })
            
            # Query all trips
            all_trips = trip_model.collection.find({})
            
            for trip in all_trips:
                destination = trip.get('destination', '').strip()
                if not destination:
                    continue
                
                # Normalize destination name (remove extra spaces, capitalize properly)
                destination = ' '.join(word.capitalize() for word in destination.split())
                
                # Update stats
                stats = destination_stats[destination]
                stats['count'] += 1
                
                # Track budget
                budget = trip.get('budget')
                if budget:
                    if isinstance(budget, dict):
                        per_day = budget.get('per_day', 0)
                        if per_day:
                            stats['budgets'].append(per_day)
                            stats['total_budget'] += per_day
                    elif isinstance(budget, (int, float)):
                        stats['budgets'].append(budget)
                        stats['total_budget'] += budget
                
                # Track interests/tags
                interests = trip.get('interests', [])
                if interests:
                    stats['interests'].update(interests)
                
                # Track most recent trip date
                created_at = trip.get('created_at')
                if created_at:
                    if not stats['recent_date'] or created_at > stats['recent_date']:
                        stats['recent_date'] = created_at
            
            # Convert to list and calculate averages
            trending_list = []
            for destination, stats in destination_stats.items():
                avg_budget = int(stats['total_budget'] / len(stats['budgets'])) if stats['budgets'] else 50
                
                trending_list.append({
                    'destination': destination,
                    'trip_count': stats['count'],
                    'avg_budget': avg_budget,
                    'interests': list(stats['interests'])[:5],  # Top 5 interests
                    'recent_activity': stats['recent_date'].isoformat() if stats['recent_date'] else None
                })
            
            # Sort by trip count (most popular first)
            trending_list.sort(key=lambda x: x['trip_count'], reverse=True)
            
            # If we have user data, use it; otherwise provide fallback popular destinations
            if len(trending_list) < 6:
                # Fallback popular destinations when not enough user data
                fallback_destinations = [
                    {
                        'destination': 'Bali, Indonesia',
                        'trip_count': 150,
                        'avg_budget': 50,
                        'interests': ['Beach', 'Culture', 'Adventure'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    },
                    {
                        'destination': 'Tokyo, Japan',
                        'trip_count': 120,
                        'avg_budget': 80,
                        'interests': ['City', 'Culture', 'Food'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    },
                    {
                        'destination': 'Paris, France',
                        'trip_count': 110,
                        'avg_budget': 100,
                        'interests': ['City', 'Romance', 'Art'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    },
                    {
                        'destination': 'Maldives',
                        'trip_count': 95,
                        'avg_budget': 150,
                        'interests': ['Beach', 'Luxury', 'Water Sports'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    },
                    {
                        'destination': 'New York, USA',
                        'trip_count': 105,
                        'avg_budget': 120,
                        'interests': ['City', 'Entertainment', 'Food'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    },
                    {
                        'destination': 'Dubai, UAE',
                        'trip_count': 88,
                        'avg_budget': 130,
                        'interests': ['Luxury', 'Shopping', 'Adventure'],
                        'recent_activity': datetime.utcnow().isoformat(),
                        'is_fallback': True
                    }
                ]
                
                # Merge real data with fallback
                existing_destinations = {item['destination'].lower() for item in trending_list}
                for fallback in fallback_destinations:
                    if fallback['destination'].lower() not in existing_destinations:
                        trending_list.append(fallback)
                        if len(trending_list) >= 12:
                            break
            
            # Return top 12 destinations
            return jsonify({
                'success': True,
                'destinations': trending_list[:12],
                'data_source': 'mixed' if any('is_fallback' in d for d in trending_list) else 'user_data',
                'total_trips_analyzed': sum(d['trip_count'] for d in trending_list if 'is_fallback' not in d)
            }), 200
            
        except Exception as e:
            print(f"Error fetching trending destinations: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return fallback data on error
            return jsonify({
                'success': False,
                'error': str(e),
                'destinations': [
                    {
                        'destination': 'Bali, Indonesia',
                        'trip_count': 150,
                        'avg_budget': 50,
                        'interests': ['Beach', 'Culture', 'Adventure'],
                        'is_fallback': True
                    },
                    {
                        'destination': 'Tokyo, Japan',
                        'trip_count': 120,
                        'avg_budget': 80,
                        'interests': ['City', 'Culture', 'Food'],
                        'is_fallback': True
                    }
                ],
                'data_source': 'error_fallback'
            }), 200  # Return 200 so frontend still works
    
    return trending_bp
