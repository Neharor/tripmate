"""
Dataset Manager - Load and process Kaggle datasets
Handles: Traveler trips, hotel bookings, tourism data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import os


class DatasetManager:
    """
    Centralized manager for all Kaggle datasets
    """
    
    def __init__(self, data_dir='data/kaggle'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.datasets = {
            'traveler_trips': None,
            'hotel_bookings': None,
            'tourism': None,
            'flight_prices': None
        }
        
    def load_traveler_trips(self, csv_path=None):
        """
        Load: Traveler Trip Dataset
        Source: https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data
        
        Columns: traveler_id, destination, duration, start_date, end_date, 
                 budget, interests, accommodation_type, transportation
        """
        try:
            if csv_path is None:
                csv_path = self.data_dir / 'traveler_trips.csv'
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"✓ Loaded {len(df)} traveler trip records")
                self.datasets['traveler_trips'] = df
                return df
            else:
                print(f"⚠️ Dataset not found: {csv_path}")
                print("   Download from: https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data")
                return self._generate_sample_traveler_data()
                
        except Exception as e:
            print(f"Error loading traveler trips: {e}")
            return self._generate_sample_traveler_data()
    
    def load_hotel_bookings(self, csv_path=None):
        """
        Load: Hotel Booking Demand Dataset
        Source: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
        
        Columns: hotel, is_canceled, lead_time, arrival_date, stays_in_weekend_nights,
                 stays_in_week_nights, adults, children, babies, meal, country, 
                 distribution_channel, adr (average daily rate), total_of_special_requests
        """
        try:
            if csv_path is None:
                csv_path = self.data_dir / 'hotel_bookings.csv'
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"✓ Loaded {len(df)} hotel booking records")
                self.datasets['hotel_bookings'] = df
                return df
            else:
                print(f"⚠️ Dataset not found: {csv_path}")
                print("   Download from: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand")
                return self._generate_sample_hotel_data()
                
        except Exception as e:
            print(f"Error loading hotel bookings: {e}")
            return self._generate_sample_hotel_data()
    
    def load_tourism_data(self, csv_path=None):
        """
        Load: Tourism Dataset with climate variables
        Source: https://www.kaggle.com/datasets/umeradnaan/tourism-dataset
        
        Columns: destination, season, avg_temperature, precipitation, 
                 tourist_arrivals, popular_activities, best_time_to_visit
        """
        try:
            if csv_path is None:
                csv_path = self.data_dir / 'tourism_data.csv'
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"✓ Loaded {len(df)} tourism records")
                self.datasets['tourism'] = df
                return df
            else:
                print(f"⚠️ Dataset not found: {csv_path}")
                print("   Download from: https://www.kaggle.com/datasets/umeradnaan/tourism-dataset")
                return self._generate_sample_tourism_data()
                
        except Exception as e:
            print(f"Error loading tourism data: {e}")
            return self._generate_sample_tourism_data()
    
    def get_destination_insights(self, destination):
        """
        Get insights for a destination from all datasets
        """
        insights = {
            'destination': destination,
            'popular_duration': None,
            'avg_budget': None,
            'peak_season': None,
            'popular_activities': [],
            'avg_hotel_price': None,
            'cancellation_rate': None
        }
        
        # From traveler trips
        if self.datasets['traveler_trips'] is not None:
            dest_trips = self.datasets['traveler_trips'][
                self.datasets['traveler_trips']['destination'].str.contains(destination, case=False, na=False)
            ]
            if len(dest_trips) > 0:
                insights['popular_duration'] = dest_trips['duration'].mode().values[0] if 'duration' in dest_trips.columns else None
                insights['avg_budget'] = dest_trips['budget'].mean() if 'budget' in dest_trips.columns else None
        
        # From hotel bookings
        if self.datasets['hotel_bookings'] is not None:
            dest_hotels = self.datasets['hotel_bookings'][
                self.datasets['hotel_bookings'].get('country', '').str.contains(destination, case=False, na=False)
            ]
            if len(dest_hotels) > 0:
                insights['avg_hotel_price'] = dest_hotels['adr'].mean() if 'adr' in dest_hotels.columns else None
                insights['cancellation_rate'] = dest_hotels['is_canceled'].mean() if 'is_canceled' in dest_hotels.columns else None
        
        # From tourism data
        if self.datasets['tourism'] is not None:
            dest_tourism = self.datasets['tourism'][
                self.datasets['tourism']['destination'].str.contains(destination, case=False, na=False)
            ]
            if len(dest_tourism) > 0:
                insights['peak_season'] = dest_tourism['season'].mode().values[0] if 'season' in dest_tourism.columns else None
                insights['popular_activities'] = dest_tourism['popular_activities'].values[0] if 'popular_activities' in dest_tourism.columns else []
        
        return insights
    
    def _generate_sample_traveler_data(self, n_samples=500):
        """Generate synthetic traveler trip data for demo"""
        print("⚠️ Using synthetic traveler data (replace with real Kaggle dataset)")
        
        destinations = ['Bali', 'Tokyo', 'Paris', 'New York', 'Dubai', 'London', 'Bangkok', 'Rome', 'Barcelona', 'Singapore']
        interests = ['beach', 'culture', 'adventure', 'food', 'shopping', 'nightlife', 'nature', 'history']
        
        data = []
        for i in range(n_samples):
            duration = np.random.choice([3, 5, 7, 10, 14])
            budget = np.random.randint(500, 5000)
            
            data.append({
                'traveler_id': f'T{i:04d}',
                'destination': np.random.choice(destinations),
                'duration': duration,
                'budget': budget,
                'interests': ','.join(np.random.choice(interests, size=np.random.randint(2, 4), replace=False)),
                'accommodation_type': np.random.choice(['hotel', 'hostel', 'resort', 'airbnb']),
                'transportation': np.random.choice(['flight', 'train', 'car', 'bus'])
            })
        
        df = pd.DataFrame(data)
        self.datasets['traveler_trips'] = df
        return df
    
    def _generate_sample_hotel_data(self, n_samples=500):
        """Generate synthetic hotel booking data for demo"""
        print("⚠️ Using synthetic hotel data (replace with real Kaggle dataset)")
        
        countries = ['Indonesia', 'Japan', 'France', 'USA', 'UAE', 'UK', 'Thailand', 'Italy', 'Spain', 'Singapore']
        
        data = []
        for i in range(n_samples):
            lead_time = np.random.randint(1, 120)
            adr = np.random.randint(50, 300)  # Average daily rate
            
            data.append({
                'hotel': f'Hotel_{i}',
                'is_canceled': np.random.choice([0, 1], p=[0.7, 0.3]),
                'lead_time': lead_time,
                'stays_in_week_nights': np.random.randint(2, 10),
                'adults': np.random.randint(1, 4),
                'adr': adr,
                'country': np.random.choice(countries)
            })
        
        df = pd.DataFrame(data)
        self.datasets['hotel_bookings'] = df
        return df
    
    def _generate_sample_tourism_data(self, n_samples=50):
        """Generate synthetic tourism data for demo"""
        print("⚠️ Using synthetic tourism data (replace with real Kaggle dataset)")
        
        destinations = ['Bali', 'Tokyo', 'Paris', 'New York', 'Dubai', 'London', 'Bangkok', 'Rome', 'Barcelona', 'Singapore']
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        
        data = []
        for dest in destinations:
            for season in seasons:
                data.append({
                    'destination': dest,
                    'season': season,
                    'avg_temperature': np.random.randint(15, 35),
                    'precipitation': np.random.randint(0, 200),
                    'tourist_arrivals': np.random.randint(10000, 100000),
                    'popular_activities': 'beach,culture,food' if 'Bali' in dest else 'culture,shopping,food',
                    'best_time_to_visit': np.random.choice(seasons)
                })
        
        df = pd.DataFrame(data)
        self.datasets['tourism'] = df
        return df
    
    def load_all_datasets(self):
        """Load all available datasets"""
        print("\n=== Loading Kaggle Datasets ===")
        self.load_traveler_trips()
        self.load_hotel_bookings()
        self.load_tourism_data()
        print("=== Dataset Loading Complete ===\n")
        
        return self.datasets


# Singleton instance
_dataset_manager = None

def get_dataset_manager():
    """Get or create dataset manager instance"""
    global _dataset_manager
    if _dataset_manager is None:
        _dataset_manager = DatasetManager()
        _dataset_manager.load_all_datasets()
    return _dataset_manager
