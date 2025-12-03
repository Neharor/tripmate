from .base_agent import BaseAgent
import json
import sys
from pathlib import Path

# Import collaborative filtering recommender
ml_path = Path(__file__).parent.parent / 'ml'
if str(ml_path) not in sys.path:
    sys.path.append(str(ml_path))

try:
    from collaborative_filter import CollaborativeFilterRecommender
    from kaggle_trending import KaggleTrendingDestinations
    CF_AVAILABLE = True
except ImportError:
    CF_AVAILABLE = False
    print("⚠️ Collaborative filtering not available")

class DestinationAgent(BaseAgent):
    """
    Specialized agent for recommending travel destinations.
    Uses Groq AI + Machine Learning (Collaborative Filtering) for personalized suggestions.
    """
    def __init__(self):
        system_prompt = """You are a destination expert. Your ONLY job: recommend travel DESTINATIONS (cities/countries).

DO NOT mention flights, hotels, or prices. ONLY destination names and why they're great.

Keep it super short - 1 line per destination."""
        
        super().__init__("DestinationAgent", system_prompt)
        
        # Initialize collaborative filtering model
        self.cf_recommender = None
        if CF_AVAILABLE:
            try:
                print("🤖 Loading collaborative filtering model...")
                trending = KaggleTrendingDestinations()
                self.cf_recommender = CollaborativeFilterRecommender(trending.df)
                print("✅ ML recommender ready!")
            except Exception as e:
                print(f"⚠️ CF model initialization error: {e}")
                self.cf_recommender = None

    def handle_request(self, input_data):
        """
        Process user query and return destination recommendations
        ONLY suggest destinations if user hasn't specified one yet
        """
        try:
            # Check if user already has a specific destination
            analysis_prompt = f"""Analyze this conversation:

{input_data}

Question: Has the user ALREADY mentioned a SPECIFIC destination (city or country)?

Examples of specific destinations: "Bali", "Paris", "Tokyo", "Thailand", "Italy"
NOT destinations: "somewhere warm", "beach destination", "Asia"

Respond with ONLY: YES or NO"""

            analysis_response = self._call_llm(analysis_prompt)
            
            # If user already specified destination, just acknowledge it
            if "YES" in analysis_response.upper():
                # Extract the destination name
                extract_prompt = f"""From this conversation, what is the destination the user wants to visit?

{input_data}

Respond with ONLY the destination name (e.g., "Bali", "Paris", "Tokyo")"""
                
                destination = self._call_llm(extract_prompt).strip()
                
                return {
                    "plan": [f"Perfect! Let's plan your trip to {destination} 🌴"]
                }
            
            # User needs destination suggestions - they haven't specified one
            # Try ML-based recommendations first
            ml_suggestions = []
            
            if self.cf_recommender:
                try:
                    # Extract interests from query
                    interests_prompt = f"""Extract travel interests from this query (just keywords):

{input_data}

Respond with comma-separated interests (e.g., beach, culture, adventure)"""
                    
                    interests_response = self._call_llm(interests_prompt)
                    interests = [i.strip() for i in interests_response.split(',')]
                    
                    # Get ML recommendations
                    ml_recs = self.cf_recommender.recommend_for_interests(
                        interests=interests,
                        budget=None,  # LLM will handle budget matching
                        top_n=3
                    )
                    
                    if ml_recs:
                        print(f"🤖 ML found {len(ml_recs)} collaborative filtering recommendations")
                        ml_suggestions = [
                            f"🌴 {rec['destination']} - {rec['match_percentage']}% traveler match ({rec['reason'][:50]}...)"
                            for rec in ml_recs[:3]
                        ]
                except Exception as e:
                    print(f"ML recommendation error: {e}")
            
            # If ML provided suggestions, use them; otherwise fall back to LLM
            if ml_suggestions:
                response_text = "Based on machine learning from 6,580+ real traveler patterns:\n\n" + "\n".join(ml_suggestions)
                return {
                    "plan": [response_text]
                }
            
            # Fallback to LLM-based suggestions
            user_prompt = f"""The user needs destination suggestions based on:

{input_data}

Suggest 3 destinations that match their budget, duration, and interests.

Format (one per line):
🌴 [City/Country] - [Why it's perfect for them in 8 words max]

CRITICAL:
- Match their interests and budget
- Keep descriptions under 8 words
- ONLY destination names and reasons
- NO hotels, NO flights, NO prices"""

            llm_response = self._call_llm(user_prompt)
            clean_response = llm_response.replace('```json', '').replace('```', '').strip()
            
            return {
                "plan": [clean_response]
            }
            
        except Exception as e:
            print(f"DestinationAgent error: {str(e)}")
            return {
                "plan": [f"Error getting destinations: {str(e)}"]
            }
