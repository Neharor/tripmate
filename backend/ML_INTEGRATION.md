# 🤖 ML & Dataset Integration - TripMate

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIPMATE AGENTS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Destination  │  │    Stays     │  │   Weather    │     │
│  │    Agent     │  │    Agent     │  │    Agent     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────┬───────┴──────────────────┘             │
│                    │                                        │
│         ┌──────────▼────────────┐                          │
│         │   Orchestrator Agent   │                          │
│         │  (LangChain + Groq)    │                          │
│         └──────────┬────────────┘                          │
│                    │                                        │
├────────────────────┼────────────────────────────────────────┤
│                    │                                        │
│         ┌──────────▼────────────┐                          │
│         │    Data Layer         │                          │
│         ├───────────────────────┤                          │
│         │ • Kaggle Datasets     │                          │
│         │ • ML Models (LSTM)    │                          │
│         │ • External APIs       │                          │
│         │ • Redis Cache         │                          │
│         └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Datasets Integration

### 1. **Traveler Trip Dataset**
**Source:** https://www.kaggle.com/datasets/rkiattisak/traveler-trip-data

**Used By:** Destination Agent, Budget Agent

**Columns:**
- `traveler_id` - Unique traveler identifier
- `destination` - Trip destination
- `duration` - Trip length (days)
- `budget` - Total budget
- `interests` - Activities/preferences
- `accommodation_type` - Hotel, hostel, resort
- `transportation` - Flight, train, car

**ML Use Case:**
- **LSTM Model:** Predict popular trip durations for destinations
- **Collaborative Filtering:** Recommend destinations based on similar travelers
- **Clustering:** Group travelers by preferences

**File:** `backend/ml/dataset_manager.py` → `load_traveler_trips()`

---

### 2. **Hotel Booking Demand**
**Source:** https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand

**Used By:** Stays Agent

**Columns:**
- `hotel` - Hotel name
- `is_canceled` - Cancellation status (0/1)
- `lead_time` - Days between booking and arrival
- `adr` - Average Daily Rate (price)
- `stays_in_week_nights` - Number of nights
- `adults`, `children`, `babies` - Guest count
- `country` - Destination country

**ML Use Case:**
- **Price Prediction:** Forecast hotel prices based on lead time
- **Cancellation Risk:** Predict booking cancellation probability
- **Demand Forecasting:** LSTM for occupancy prediction

**File:** `backend/ml/dataset_manager.py` → `load_hotel_bookings()`

---

### 3. **Tourism Dataset (Climate + Activities)**
**Source:** https://www.kaggle.com/datasets/umeradnaan/tourism-dataset

**Used By:** Weather Agent, Destination Agent

**Columns:**
- `destination` - Location
- `season` - Spring/Summer/Fall/Winter
- `avg_temperature` - Average temp (°C)
- `precipitation` - Rainfall (mm)
- `tourist_arrivals` - Visitor count
- `popular_activities` - Common activities
- `best_time_to_visit` - Optimal season

**ML Use Case:**
- **Weather Forecasting:** Combine with OpenWeatherMap API
- **Activity Recommendation:** Match weather with suitable activities
- **Seasonal Trends:** Predict peak/off-peak seasons

**File:** `backend/ml/dataset_manager.py` → `load_tourism_data()`

---

## 🤖 ML Models

### 1. **Demand Predictor (LSTM)**
**File:** `backend/ml/predictors.py` → `DemandPredictor`

**Purpose:** Forecast tourist demand for destinations

**Features:**
- Time series forecasting (7-30 days ahead)
- Considers seasonality, trends, events
- Outputs: demand level, trend direction, confidence

**Algorithm:**
```python
# Simplified version (replace with LSTM in production)
- Input: Historical arrivals (past 30 days)
- LSTM layers: 50 → 25 → 1
- Output: Predicted arrivals (next 7 days)
```

**Usage:**
```python
from ml.predictors import get_demand_predictor

predictor = get_demand_predictor()
result = predictor.predict_demand('Bali', days_ahead=7)
# {'predictions': [1200, 1250, ...], 'trend': 'increasing'}
```

---

### 2. **Price Predictor**
**File:** `backend/ml/predictors.py` → `PricePredictor`

**Purpose:** Forecast flight/hotel price changes

**Features:**
- Booking window optimization (21-60 days = best prices)
- Demand-based pricing (high demand = higher prices)
- Price trend analysis

**Algorithm:**
```python
price(t) = base_price × time_factor(t) × demand_factor(t)

where:
  time_factor(t) = {
    1.4  if t < 7 days    (last minute)
    1.2  if t < 21 days   (moderate)
    1.0  if t < 60 days   (optimal)
    1.1  if t > 60 days   (too early)
  }
```

**Usage:**
```python
from ml.predictors import get_price_predictor

predictor = get_price_predictor()
result = predictor.predict_price_trend(
    current_price=500,
    days_until_travel=45,
    demand_level='high'
)
# {'predicted_price': 600, 'recommendation': '🟢 OPTIMAL'}
```

---

### 3. **Interest Predictor (Collaborative Filtering)**
**File:** `backend/ml/predictors.py` → `InterestPredictor`

**Purpose:** Recommend activities based on user profile

**Algorithm:**
- Find similar users (cosine similarity on interest vectors)
- Recommend activities liked by similar users
- Personalize itinerary suggestions

**Usage:**
```python
from ml.predictors import get_interest_predictor

predictor = get_interest_predictor()
interests = predictor.predict_interests({
    'past_trips': ['Bali', 'Phuket'],
    'interests': ['beach', 'food']
})
# ['beach', 'adventure', 'water sports', 'relaxation']
```

---

## 🌐 External APIs

### 1. **OpenTripMap API**
**Used By:** Destination Agent, Activities Agent

**Endpoint:** `https://api.opentripmap.com/0.1/en/places/`

**Features:**
- Find attractions near coordinates
- Get place details, ratings, photos
- Filter by category (museums, parks, restaurants)

**Integration:**
```python
# File: backend/services/api_clients.py
def get_attractions(lat, lon, radius=5000, kinds='interesting_places'):
    url = f"https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        'apikey': OPENTRIPMAP_API_KEY,
        'lat': lat,
        'lon': lon,
        'radius': radius,
        'kinds': kinds
    }
    return requests.get(url, params=params).json()
```

---

### 2. **Amadeus Hotels API**
**Used By:** Stays Agent

**Endpoint:** `https://test.api.amadeus.com/v1/shopping/hotel-offers`

**Features:**
- Real-time hotel prices
- Availability, ratings, amenities
- Direct booking links

**Already Implemented:** `backend/services/flight_service.py` (similar for hotels)

---

### 3. **OpenWeatherMap API**
**Used By:** Weather Agent

**Endpoint:** `https://api.openweathermap.org/data/2.5/forecast`

**Features:**
- 5-day forecast
- Hourly weather updates
- Temperature, precipitation, wind

**Integration:**
```python
# File: backend/agents/weather.py (enhance existing)
def get_forecast(city, days=5):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    return requests.get(url, params=params).json()
```

---

### 4. **Numbeo API**
**Used By:** Budget Agent

**Endpoint:** `https://www.numbeo.com/api/`

**Features:**
- Cost of living data
- Restaurant prices, grocery costs
- Local transportation costs

**Integration:**
```python
# File: backend/services/api_clients.py
def get_cost_of_living(city):
    url = f"https://www.numbeo.com/api/city_prices"
    params = {
        'api_key': NUMBEO_API_KEY,
        'query': city
    }
    return requests.get(url, params=params).json()
```

---

## 📦 Implementation Status

### ✅ **Completed**
1. Dataset Manager (`ml/dataset_manager.py`)
2. ML Predictors (`ml/predictors.py`)
3. Flight Price Predictor (`ml/flight_price_predictor.py`)
4. Basic agent structure (all 7 agents)

### 🔧 **In Progress**
1. Installing ML dependencies (`pip install -r requirements.txt`)
2. Downloading Kaggle datasets
3. Training LSTM models

### ⏳ **Pending**
1. Redis integration for shared context
2. API key setup (OpenTripMap, OpenWeatherMap, Numbeo)
3. LSTM model implementation (currently using Linear Regression)
4. Real-time data pipeline

---

## 🚀 Setup Instructions

### 1. **Install ML Dependencies**
```bash
cd backend
pip install -r requirements.txt
# Installs: pandas, numpy, scikit-learn
```

### 2. **Download Kaggle Datasets**
```bash
# Install Kaggle CLI
pip install kaggle

# Setup API credentials
mkdir ~/.kaggle
# Place kaggle.json in ~/.kaggle/

# Download datasets
kaggle datasets download -d rkiattisak/traveler-trip-data
kaggle datasets download -d jessemostipak/hotel-booking-demand
kaggle datasets download -d umeradnaan/tourism-dataset

# Extract to backend/data/kaggle/
unzip traveler-trip-data.zip -d backend/data/kaggle/
unzip hotel-booking-demand.zip -d backend/data/kaggle/
unzip tourism-dataset.zip -d backend/data/kaggle/
```

### 3. **Setup API Keys**
Create `backend/.env`:
```bash
# Amadeus (Flights & Hotels)
AMADEUS_API_KEY=your_key
AMADEUS_API_SECRET=your_secret

# OpenTripMap (Attractions)
OPENTRIPMAP_API_KEY=your_key

# OpenWeatherMap
OPENWEATHER_API_KEY=your_key

# Numbeo (Cost of Living)
NUMBEO_API_KEY=your_key

# Redis (Shared Context)
REDIS_URL=redis://localhost:6379
```

### 4. **Train ML Models**
```python
# Run training script
cd backend
python -c "
from ml.dataset_manager import get_dataset_manager
from ml.predictors import get_demand_predictor, get_price_predictor

# Load datasets
dm = get_dataset_manager()
dm.load_all_datasets()

# Train models
demand_predictor = get_demand_predictor()
demand_predictor.train_simple_model(historical_data=[...])

print('✓ ML models trained!')
"
```

---

## 📈 Agent Enhancement Summary

| Agent | Current | Added ML | Added API | Added Dataset |
|-------|---------|----------|-----------|---------------|
| **Destination** | ✓ Basic | LSTM demand forecast | OpenTripMap | Traveler Trips |
| **Stays** | ✓ Basic | Price prediction | Amadeus Hotels | Hotel Bookings |
| **Weather** | ✓ Basic | Weather pattern LSTM | OpenWeatherMap | Tourism Dataset |
| **Budget** | ✓ Basic | Cost forecasting | Numbeo API | Traveler Trips |
| **Flight** | ✓ Partial | Price prediction (done) | Amadeus Flights | Flight Prices |
| **Activities** | ✓ Basic | Interest prediction | OpenTripMap | Tourism Dataset |
| **Orchestrator** | ✓ Working | Aggregate predictions | Redis | All datasets |

---

## 🎯 Next Steps

1. **Install Dependencies:**
   ```bash
   pip install pandas numpy scikit-learn redis
   ```

2. **Download 1 Dataset (Start Small):**
   ```bash
   kaggle datasets download -d rkiattisak/traveler-trip-data
   ```

3. **Test ML Pipeline:**
   ```bash
   python -m ml.dataset_manager  # Test data loading
   python -m ml.predictors       # Test predictions
   ```

4. **Enhance Agents One-by-One:**
   - Start with Destination Agent (most impactful)
   - Add OpenTripMap API
   - Integrate LSTM demand forecasting

---

## 📝 Code Examples

### Enhanced Destination Agent (with ML)
```python
from ml.dataset_manager import get_dataset_manager
from ml.predictors import get_demand_predictor

class DestinationAgent(BaseAgent):
    def handle_request(self, input_data):
        # Get historical insights
        dm = get_dataset_manager()
        insights = dm.get_destination_insights('Bali')
        
        # Predict demand
        predictor = get_demand_predictor()
        demand = predictor.predict_demand('Bali', days_ahead=7)
        
        # Generate LLM response with ML insights
        prompt = f"""
        Destination: Bali
        
        Historical Data:
        - Popular duration: {insights['popular_duration']} days
        - Average budget: ${insights['avg_budget']}
        - Peak season: {insights['peak_season']}
        
        ML Predictions:
        - Demand trend: {demand['trend']}
        - Predicted arrivals: {demand['predictions']}
        
        Recommend optimal travel plan.
        """
        
        return self._call_llm(prompt)
```

---

**Status:** 🟢 Architecture Complete | 🟡 Implementation 60% | ⏳ Testing Pending
