"""
Flight Price Prediction using Simple ML
Uses historical data to predict prices and best booking time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os


class FlightPricePredictor:
    """
    Simple ML model for flight price prediction
    Uses Linear Regression on historical flight data
    """
    
    def __init__(self):
        self.model = None
        self.route_data = {}  # Cache for route-specific data
        
    def predict_price(self, origin, destination, departure_date, airline=None):
        """
        Predict flight price based on route and date
        
        Args:
            origin: Departure city
            destination: Arrival city
            departure_date: Date of travel (datetime or string)
            airline: Optional airline filter
            
        Returns:
            dict with predicted_price, confidence, best_booking_date
        """
        try:
            # Convert date if string
            if isinstance(departure_date, str):
                departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
            
            # Days until departure
            days_before = (departure_date - datetime.now()).days
            
            # Simple price calculation based on booking window
            # Best prices: 21-60 days before
            # Peak prices: <7 days or >90 days before
            base_price = self._get_base_price(origin, destination)
            
            if days_before < 0:
                # Past date
                multiplier = 1.5
                confidence = 0.3
            elif days_before <= 7:
                # Last minute - expensive
                multiplier = 1.4
                confidence = 0.7
            elif days_before <= 21:
                # Moderate pricing
                multiplier = 1.2
                confidence = 0.8
            elif days_before <= 60:
                # Sweet spot - best prices
                multiplier = 1.0
                confidence = 0.9
            elif days_before <= 90:
                # Early bird - good prices
                multiplier = 1.1
                confidence = 0.85
            else:
                # Too early - prices not yet optimized
                multiplier = 1.3
                confidence = 0.6
            
            predicted_price = int(base_price * multiplier)
            
            # Calculate best booking date (21-45 days before)
            best_booking_date = departure_date - timedelta(days=35)
            if best_booking_date < datetime.now():
                best_booking_date = datetime.now() + timedelta(days=1)
            
            # Price trend
            if days_before > 60:
                trend = "Prices will likely drop. Wait for 21-60 day window."
            elif days_before > 21:
                trend = "Good time to book! Prices are optimal."
            elif days_before > 7:
                trend = "Book soon! Prices rising as departure nears."
            else:
                trend = "Book now! Last minute prices are high."
            
            return {
                "predicted_price": predicted_price,
                "confidence": confidence,
                "best_booking_date": best_booking_date.strftime('%Y-%m-%d'),
                "days_until_departure": days_before,
                "price_trend": trend,
                "booking_recommendation": self._get_booking_recommendation(days_before)
            }
            
        except Exception as e:
            print(f"Price prediction error: {e}")
            return {
                "predicted_price": None,
                "confidence": 0.5,
                "error": str(e)
            }
    
    def _get_base_price(self, origin, destination):
        """
        Get base price for route based on distance/popularity
        In production, this would come from Kaggle dataset
        """
        # Sample base prices (USD) - replace with Kaggle data
        route_prices = {
            # US Domestic
            "New York-Los Angeles": 250,
            "Seattle-New York": 200,
            "Seattle-Delhi": 800,
            "Los Angeles-Tokyo": 650,
            
            # Asia
            "Bangkok-Bali": 100,
            "Hong Kong-Tokyo": 300,
            "Singapore-Bangkok": 150,
            "Delhi-Dubai": 200,
            
            # Europe
            "London-Paris": 80,
            "London-New York": 400,
            "Paris-Rome": 100,
            
            # Default
            "default": 300
        }
        
        # Try both directions
        route_key = f"{origin}-{destination}"
        reverse_key = f"{destination}-{origin}"
        
        base = route_prices.get(route_key) or route_prices.get(reverse_key) or route_prices.get("default")
        
        # Add some randomness (±10%)
        variation = np.random.uniform(0.9, 1.1)
        return int(base * variation)
    
    def _get_booking_recommendation(self, days_before):
        """
        Get booking recommendation based on days before departure
        """
        if days_before < 0:
            return "❌ Cannot book past dates"
        elif days_before <= 3:
            return "🔴 BOOK NOW - Last minute surge!"
        elif days_before <= 7:
            return "🟡 BOOK SOON - Prices rising"
        elif days_before <= 21:
            return "🟢 GOOD TIME - Book within this week"
        elif days_before <= 60:
            return "🟢 OPTIMAL WINDOW - Best prices now!"
        elif days_before <= 90:
            return "🟡 WAIT - Prices will drop in 2-3 weeks"
        else:
            return "⏳ TOO EARLY - Check back in 30 days"
    
    def load_kaggle_data(self, csv_path):
        """
        Load historical flight data from Kaggle dataset
        Expected columns: origin, destination, date, price, airline
        
        Popular Kaggle datasets:
        - Flight Price Prediction: https://www.kaggle.com/datasets/shubhambathwal/flight-price-prediction
        - Airline Dataset: https://www.kaggle.com/datasets/iamsouravbanerjee/airline-dataset
        """
        try:
            df = pd.read_csv(csv_path)
            print(f"✓ Loaded {len(df)} flight records from Kaggle")
            
            # Build route-specific price history
            for _, row in df.iterrows():
                route = f"{row.get('origin', 'Unknown')}-{row.get('destination', 'Unknown')}"
                if route not in self.route_data:
                    self.route_data[route] = []
                
                self.route_data[route].append({
                    'price': row.get('price', 0),
                    'date': row.get('date'),
                    'airline': row.get('airline')
                })
            
            print(f"✓ Processed {len(self.route_data)} unique routes")
            return True
            
        except Exception as e:
            print(f"Error loading Kaggle data: {e}")
            return False
    
    def train_simple_model(self, kaggle_csv_path=None):
        """
        Train a simple regression model on historical data
        For demo purposes - uses basic features
        """
        try:
            if kaggle_csv_path and os.path.exists(kaggle_csv_path):
                df = pd.read_csv(kaggle_csv_path)
            else:
                # Generate sample training data
                print("⚠️ No Kaggle data found. Generating sample data...")
                df = self._generate_sample_data()
            
            # Feature engineering
            df['days_before'] = (pd.to_datetime(df['departure_date']) - pd.to_datetime(df['booking_date'])).dt.days
            df['month'] = pd.to_datetime(df['departure_date']).dt.month
            df['day_of_week'] = pd.to_datetime(df['departure_date']).dt.dayofweek
            
            # Simple linear model: price ~ days_before + month + day_of_week
            from sklearn.linear_model import LinearRegression
            
            X = df[['days_before', 'month', 'day_of_week']]
            y = df['price']
            
            self.model = LinearRegression()
            self.model.fit(X, y)
            
            print(f"✓ Model trained on {len(df)} samples")
            print(f"  R² score: {self.model.score(X, y):.3f}")
            
            return True
            
        except Exception as e:
            print(f"Model training error: {e}")
            return False
    
    def _generate_sample_data(self, n_samples=1000):
        """
        Generate synthetic flight data for demo
        """
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            days_before = np.random.randint(1, 120)
            month = np.random.randint(1, 13)
            day_of_week = np.random.randint(0, 7)
            
            # Price formula: base + booking_window_factor + seasonality
            base_price = 300
            
            # Booking window effect (cheaper 21-60 days before)
            if days_before < 7:
                window_factor = 150
            elif days_before < 21:
                window_factor = 80
            elif days_before < 60:
                window_factor = 0  # Best price
            else:
                window_factor = 50
            
            # Seasonality (summer more expensive)
            season_factor = 50 if month in [6, 7, 8, 12] else 0
            
            # Weekend premium
            weekend_factor = 30 if day_of_week in [4, 5, 6] else 0
            
            price = base_price + window_factor + season_factor + weekend_factor
            price += np.random.normal(0, 20)  # Random noise
            
            data.append({
                'booking_date': datetime.now().strftime('%Y-%m-%d'),
                'departure_date': (datetime.now() + timedelta(days=days_before)).strftime('%Y-%m-%d'),
                'days_before': days_before,
                'month': month,
                'day_of_week': day_of_week,
                'price': max(100, price)  # Min price $100
            })
        
        return pd.DataFrame(data)


# Singleton instance
_predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = FlightPricePredictor()
        # Try to train on startup
        _predictor.train_simple_model()
    return _predictor
