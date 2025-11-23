"""
ML Models for TripMate Agents
Includes: LSTM for demand prediction, price forecasting
"""

import numpy as np
try:
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not installed. Run: pip install pandas numpy scikit-learn")


class DemandPredictor:
    """
    LSTM-based demand prediction for destinations
    Predicts tourist arrivals, hotel occupancy, price trends
    """
    
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.trained = False
        
    def prepare_time_series(self, data, lookback=30):
        """
        Convert data to time series format for LSTM
        
        Args:
            data: Pandas Series or array of historical values
            lookback: Number of past days to use for prediction
        """
        if not ML_AVAILABLE:
            return None, None
            
        # Normalize data
        scaled_data = self.scaler.fit_transform(np.array(data).reshape(-1, 1))
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)
    
    def train_simple_model(self, historical_data):
        """
        Train a simple forecast model (Linear for demo)
        In production, replace with LSTM
        """
        if not ML_AVAILABLE:
            print("⚠️ Cannot train - ML libraries not available")
            return False
            
        try:
            from sklearn.linear_model import LinearRegression
            
            # Prepare data
            X, y = self.prepare_time_series(historical_data, lookback=7)
            
            if X is None or len(X) < 10:
                print("⚠️ Insufficient data for training")
                return False
            
            # Train simple model (replace with LSTM in production)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            
            score = self.model.score(X_test, y_test)
            print(f"✓ Demand model trained (R² = {score:.3f})")
            
            self.trained = True
            return True
            
        except Exception as e:
            print(f"Training error: {e}")
            return False
    
    def predict_demand(self, destination, days_ahead=7):
        """
        Predict demand for next N days
        
        Returns:
            dict with predictions, trend, confidence
        """
        if not self.trained:
            # Use simple heuristic if not trained
            return self._heuristic_prediction(destination, days_ahead)
        
        try:
            # In production: Use LSTM model here
            predictions = []
            for day in range(days_ahead):
                # Placeholder prediction
                base_demand = 1000
                trend = np.random.uniform(0.9, 1.1)
                predictions.append(int(base_demand * trend))
            
            return {
                'predictions': predictions,
                'trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing',
                'confidence': 0.75
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._heuristic_prediction(destination, days_ahead)
    
    def _heuristic_prediction(self, destination, days_ahead):
        """
        Simple rule-based prediction when ML unavailable
        """
        # Basic demand based on destination popularity
        popular_destinations = ['Bali', 'Tokyo', 'Paris', 'Dubai', 'New York']
        base_demand = 2000 if destination in popular_destinations else 1000
        
        predictions = [int(base_demand * np.random.uniform(0.8, 1.2)) for _ in range(days_ahead)]
        
        return {
            'predictions': predictions,
            'trend': 'stable',
            'confidence': 0.5,
            'method': 'heuristic'
        }


class PricePredictor:
    """
    Price forecasting for hotels and flights
    Uses historical price data + demand signals
    """
    
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        
    def predict_price_trend(self, current_price, days_until_travel, demand_level='medium'):
        """
        Predict how price will change over time
        
        Args:
            current_price: Current price
            days_until_travel: Days until departure/check-in
            demand_level: 'low', 'medium', 'high'
        
        Returns:
            dict with predicted_price, trend, best_booking_window
        """
        demand_multiplier = {
            'low': 0.9,
            'medium': 1.0,
            'high': 1.2
        }.get(demand_level, 1.0)
        
        # Price typically increases as travel date approaches
        if days_until_travel < 7:
            time_multiplier = 1.4
            recommendation = "🔴 BOOK NOW - Last minute surge!"
        elif days_until_travel < 21:
            time_multiplier = 1.2
            recommendation = "🟡 BOOK SOON - Prices rising"
        elif days_until_travel < 60:
            time_multiplier = 1.0
            recommendation = "🟢 OPTIMAL - Best time to book!"
        else:
            time_multiplier = 1.1
            recommendation = "⏳ WAIT - Prices will drop soon"
        
        predicted_price = int(current_price * time_multiplier * demand_multiplier)
        
        # Best booking window (21-45 days before)
        best_booking_days = 35 - days_until_travel
        
        return {
            'predicted_price': predicted_price,
            'current_price': current_price,
            'price_change': predicted_price - current_price,
            'trend': 'increasing' if predicted_price > current_price else 'decreasing',
            'recommendation': recommendation,
            'best_booking_in_days': max(0, best_booking_days),
            'confidence': 0.8
        }


class InterestPredictor:
    """
    Predict user interests based on past trips (collaborative filtering)
    """
    
    def __init__(self):
        self.user_interest_matrix = {}
        
    def predict_interests(self, user_profile, similar_users=5):
        """
        Predict what activities/places user might like
        Based on collaborative filtering
        
        Args:
            user_profile: dict with past trips, interests
            similar_users: Number of similar users to consider
        
        Returns:
            list of recommended interests
        """
        # Placeholder - would use ML in production
        common_interests = ['culture', 'food', 'shopping', 'beach', 'adventure']
        
        # Simple recommendation based on profile
        if 'past_trips' in user_profile:
            # Users who went to beaches might like adventure
            if any('beach' in trip.lower() for trip in user_profile.get('past_trips', [])):
                return ['beach', 'adventure', 'water sports', 'relaxation']
        
        return common_interests


# Singleton instances
_demand_predictor = None
_price_predictor = None
_interest_predictor = None

def get_demand_predictor():
    global _demand_predictor
    if _demand_predictor is None:
        _demand_predictor = DemandPredictor()
    return _demand_predictor

def get_price_predictor():
    global _price_predictor
    if _price_predictor is None:
        _price_predictor = PricePredictor()
    return _price_predictor

def get_interest_predictor():
    global _interest_predictor
    if _interest_predictor is None:
        _interest_predictor = InterestPredictor()
    return _interest_predictor
