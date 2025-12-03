"""
Collaborative Filtering Recommender for Destinations
Uses user-item matrix to find similar destinations and make personalized recommendations
Similar to how Netflix recommends movies based on viewing patterns
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from typing import List, Dict, Tuple


class CollaborativeFilterRecommender:
    """
    Item-based Collaborative Filtering for destination recommendations
    
    How it works:
    1. Build user-destination matrix from trip data
    2. Calculate destination similarity using cosine similarity
    3. Recommend destinations similar to ones user is interested in
    
    Example: If many users who visited Bali also visited Phuket,
             then Bali and Phuket are considered similar destinations
    """
    
    def __init__(self, trip_data: pd.DataFrame = None):
        self.trip_data = trip_data
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.destination_index = {}
        self.index_destination = {}
        
        if trip_data is not None:
            self._build_model()
    
    def _build_model(self):
        """
        Build collaborative filtering model from trip data
        Creates user-item matrix and calculates item similarities
        """
        print("🔧 Building collaborative filtering model...")
        
        # Create user-destination interaction matrix
        # 1 = user visited destination, 0 = not visited
        user_dest_counts = self.trip_data.groupby(['traveler_id', 'destination']).size().reset_index(name='visits')
        
        # Pivot to create user-item matrix
        self.user_item_matrix = user_dest_counts.pivot_table(
            index='traveler_id',
            columns='destination',
            values='visits',
            fill_value=0
        )
        
        # Normalize: convert to binary (visited=1, not visited=0)
        self.user_item_matrix = (self.user_item_matrix > 0).astype(int)
        
        # Calculate destination similarity using cosine similarity
        # This finds destinations that are visited by similar groups of users
        destination_vectors = self.user_item_matrix.T.values  # Transpose to get destination rows
        self.item_similarity_matrix = cosine_similarity(destination_vectors)
        
        # Create destination index mapping
        destinations = self.user_item_matrix.columns.tolist()
        self.destination_index = {dest: idx for idx, dest in enumerate(destinations)}
        self.index_destination = {idx: dest for idx, dest in enumerate(destinations)}
        
        print(f"✅ Model built: {len(destinations)} destinations, {len(self.user_item_matrix)} users")
        print(f"   Similarity matrix shape: {self.item_similarity_matrix.shape}")
    
    def get_similar_destinations(
        self, 
        destination: str, 
        top_n: int = 5,
        min_similarity: float = 0.1
    ) -> List[Dict]:
        """
        Find destinations similar to the given destination
        
        Args:
            destination: Reference destination
            top_n: Number of similar destinations to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar destinations with similarity scores
        """
        if self.item_similarity_matrix is None:
            return []
        
        # Find exact match or partial match
        matched_dest = self._find_destination(destination)
        if not matched_dest:
            return []
        
        dest_idx = self.destination_index[matched_dest]
        
        # Get similarity scores for this destination
        similarity_scores = self.item_similarity_matrix[dest_idx]
        
        # Get indices of most similar destinations (excluding itself)
        similar_indices = np.argsort(similarity_scores)[::-1][1:top_n+1]
        
        # Build result list
        similar_destinations = []
        for idx in similar_indices:
            similarity = similarity_scores[idx]
            
            if similarity >= min_similarity:
                dest_name = self.index_destination[idx]
                similar_destinations.append({
                    'destination': dest_name,
                    'similarity_score': round(float(similarity), 3),
                    'match_percentage': round(float(similarity) * 100, 1),
                    'reason': f"{int(similarity * 100)}% of travelers who visited {matched_dest.split(',')[0]} also enjoyed this destination"
                })
        
        return similar_destinations
    
    def recommend_for_interests(
        self,
        interests: List[str],
        budget: int = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Recommend destinations based on user interests using collaborative patterns
        
        Args:
            interests: User's travel interests
            budget: Daily budget (optional)
            top_n: Number of recommendations
            
        Returns:
            List of recommended destinations
        """
        if self.trip_data is None or self.item_similarity_matrix is None:
            return []
        
        # Find destinations that match user interests
        interest_keywords = [i.lower() for i in interests]
        
        matching_destinations = []
        for dest in self.destination_index.keys():
            # Get trips to this destination
            dest_trips = self.trip_data[self.trip_data['destination'] == dest]
            
            if len(dest_trips) == 0:
                continue
            
            # Extract interests from trips
            all_interests = []
            for interests_str in dest_trips['interests'].values:
                all_interests.extend([i.strip().lower() for i in str(interests_str).split(',')])
            
            # Calculate interest match score
            interest_matches = sum(1 for interest in interest_keywords if interest in all_interests)
            
            if interest_matches > 0:
                avg_budget = int(dest_trips['budget_per_day'].mean())
                
                # Budget filter if provided
                if budget and avg_budget > budget * 1.3:  # Allow 30% flexibility
                    continue
                
                matching_destinations.append({
                    'destination': dest,
                    'interest_match_score': interest_matches,
                    'avg_budget': avg_budget
                })
        
        # If we found matching destinations, use collaborative filtering
        if matching_destinations:
            # Get top matching destination
            matching_destinations.sort(key=lambda x: x['interest_match_score'], reverse=True)
            seed_destination = matching_destinations[0]['destination']
            
            # Find similar destinations using collaborative filtering
            similar_dests = self.get_similar_destinations(seed_destination, top_n=top_n)
            
            # Enrich with trip statistics
            recommendations = []
            for dest_info in similar_dests:
                dest = dest_info['destination']
                dest_trips = self.trip_data[self.trip_data['destination'] == dest]
                
                if len(dest_trips) > 0:
                    recommendations.append({
                        'destination': dest,
                        'similarity_score': dest_info['similarity_score'],
                        'match_percentage': dest_info['match_percentage'],
                        'reason': dest_info['reason'],
                        'avg_budget': int(dest_trips['budget_per_day'].mean()),
                        'trip_count': len(dest_trips),
                        'avg_duration': int(dest_trips['duration'].mean()),
                        'recommendation_type': 'collaborative_filtering'
                    })
            
            return recommendations
        
        return []
    
    def get_user_recommendations(
        self,
        user_past_trips: List[str],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Recommend destinations based on user's past trips
        "Users who visited X also visited Y"
        
        Args:
            user_past_trips: List of destinations user has visited
            top_n: Number of recommendations
            
        Returns:
            List of recommended destinations
        """
        if self.item_similarity_matrix is None:
            return []
        
        # Aggregate similarity scores across all past trips
        aggregated_scores = defaultdict(float)
        
        for past_dest in user_past_trips:
            similar = self.get_similar_destinations(past_dest, top_n=20)
            
            for dest_info in similar:
                dest = dest_info['destination']
                # Skip if already visited
                if dest not in user_past_trips:
                    # Weight by similarity score
                    aggregated_scores[dest] += dest_info['similarity_score']
        
        # Sort by aggregated score
        sorted_recommendations = sorted(
            aggregated_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        # Build detailed recommendations
        recommendations = []
        for dest, score in sorted_recommendations:
            dest_trips = self.trip_data[self.trip_data['destination'] == dest]
            
            if len(dest_trips) > 0:
                recommendations.append({
                    'destination': dest,
                    'recommendation_score': round(score, 3),
                    'reason': f"Based on your travel history, travelers with similar preferences loved this destination",
                    'avg_budget': int(dest_trips['budget_per_day'].mean()),
                    'trip_count': len(dest_trips),
                    'recommendation_type': 'personalized_collaborative'
                })
        
        return recommendations
    
    def _find_destination(self, query: str) -> str:
        """Find matching destination from query (exact or partial match)"""
        query_lower = query.lower()
        
        # Exact match
        for dest in self.destination_index.keys():
            if dest.lower() == query_lower:
                return dest
        
        # Partial match (city name)
        for dest in self.destination_index.keys():
            if query_lower in dest.lower() or dest.lower().startswith(query_lower):
                return dest
        
        return None
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the collaborative filtering model"""
        if self.item_similarity_matrix is None:
            return {'status': 'not_built'}
        
        # Calculate average similarity
        # Exclude diagonal (self-similarity = 1.0)
        mask = ~np.eye(self.item_similarity_matrix.shape[0], dtype=bool)
        avg_similarity = self.item_similarity_matrix[mask].mean()
        
        return {
            'status': 'ready',
            'total_destinations': len(self.destination_index),
            'total_users': len(self.user_item_matrix),
            'avg_similarity': round(float(avg_similarity), 3),
            'matrix_sparsity': round(1 - (self.user_item_matrix.sum().sum() / self.user_item_matrix.size), 3),
            'model_type': 'item_based_collaborative_filtering'
        }


# Integration with existing KaggleTrendingDestinations
def integrate_collaborative_filtering(trip_data: pd.DataFrame) -> CollaborativeFilterRecommender:
    """
    Create collaborative filtering model from Kaggle trip data
    
    Args:
        trip_data: DataFrame with columns: traveler_id, destination, interests, budget_per_day, duration
        
    Returns:
        Trained CollaborativeFilterRecommender instance
    """
    recommender = CollaborativeFilterRecommender(trip_data)
    return recommender


# Test function
if __name__ == "__main__":
    print("=== Collaborative Filtering Recommender Test ===\n")
    
    # Load Kaggle data
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    
    from kaggle_trending import KaggleTrendingDestinations
    
    # Get trip data
    trending_analyzer = KaggleTrendingDestinations()
    trip_data = trending_analyzer.df
    
    # Build collaborative filtering model
    cf_recommender = CollaborativeFilterRecommender(trip_data)
    
    # Test 1: Find similar destinations
    print("\n📍 Test 1: Destinations similar to 'Bali'")
    similar = cf_recommender.get_similar_destinations('Bali', top_n=5)
    for i, dest in enumerate(similar, 1):
        print(f"{i}. {dest['destination']:<35} {dest['match_percentage']:>5.1f}% match")
        print(f"   {dest['reason']}")
    
    # Test 2: Recommend based on interests
    print("\n\n🎯 Test 2: Recommendations for interests=['beach', 'adventure']")
    interest_recs = cf_recommender.recommend_for_interests(
        interests=['beach', 'adventure'],
        budget=100,
        top_n=5
    )
    for i, dest in enumerate(interest_recs, 1):
        print(f"{i}. {dest['destination']:<35} ${dest['avg_budget']}/day ({dest['match_percentage']}% match)")
    
    # Test 3: Personalized recommendations
    print("\n\n👤 Test 3: Recommendations for user who visited ['Bali, Indonesia', 'Phuket, Thailand']")
    user_recs = cf_recommender.get_user_recommendations(
        user_past_trips=['Bali, Indonesia', 'Phuket, Thailand'],
        top_n=5
    )
    for i, dest in enumerate(user_recs, 1):
        print(f"{i}. {dest['destination']:<35} Score: {dest['recommendation_score']:.3f}")
        print(f"   {dest['reason']}")
    
    # Model stats
    print("\n\n📊 Model Statistics:")
    stats = cf_recommender.get_model_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n Collaborative filtering ready!")
