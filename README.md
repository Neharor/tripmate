# 🌍 TripMate - AI-Powered Travel Planner

> Your intelligent travel companion that creates personalized trip itineraries using machine learning and real-time APIs

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0+-61dafb.svg)](https://reactjs.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🤖 **Machine Learning Recommendations**
- **Collaborative Filtering** (Netflix-style) for destination recommendations
- Trained on 6,580+ real trip records from Kaggle dataset
- Item-based similarity using cosine similarity algorithm
- Personalized suggestions: "Users who visited X also visited Y"

### 🛫 **Real-Time Travel Data**
- **Flights**: Live prices from Amadeus API (Cheapest, Fastest, Best Overall)
- **Hotels**: Real-time availability and pricing via Amadeus
- **Activities**: Google Places API integration with ratings and reviews
- **Local Events**: AI-discovered festivals, concerts, and cultural happenings

### 🧠 **Intelligent Orchestration**
- **LangChain ReAct Agent** with Groq LLM (llama-3.1-8b-instant)
- Multi-step reasoning and tool selection
- Sequential question flow with form field suggestions
- Conversational memory for context-aware planning

### 📊 **Data-Driven Insights**
- Trending destinations from real traveler patterns
- ML-powered activity recommendations from Kaggle data
- Budget-aware filtering and personalization
- Interactive destination carousel with live statistics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           USER INTERFACE (React)            │
│  • Chat Interface  • Trending Carousel      │
│  • Trip Planner    • My Saved Trips         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      LANGCHAIN ORCHESTRATOR (Groq LLM)      │
│  • ReAct Pattern  • Tool Selection          │
│  • Multi-step Execution  • Error Handling   │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼─────────┐  ┌───────▼─────────────┐
│  ML MODELS      │  │  LIVE APIs          │
│  (Offline)      │  │  (Real-time)        │
├─────────────────┤  ├─────────────────────┤
│ • Collaborative │  │ • Amadeus Flights   │
│   Filtering     │  │ • Amadeus Hotels    │
│ • Kaggle Data   │  │ • Google Places     │
│   Analysis      │  │ • Event Discovery   │
└─────────────────┘  └─────────────────────┘
```

### 🎯 **Single Agent Architecture**
- **ONE Trip Planner Agent** with LangChain orchestration
- **5 Specialized Tools**: FlightPlanner, HotelPlanner, ActivityRecommender, DestinationRecommender, LocalEventsDiscoverer

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB Atlas account (optional - works without it)
- API Keys: Amadeus, Groq, Google Places (optional)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Neharor/tripmate.git
cd tripmate
```

### 2️⃣ Backend Setup
```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
cp .env.example .env

# Add your API keys to .env:
# GROQ_API_KEY=your_groq_api_key
# AMADEUS_CLIENT_ID=your_amadeus_client_id
# AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
# GOOGLE_PLACES_API_KEY=your_google_places_key (optional)
# MONGODB_URI=your_mongodb_uri (optional)

# Start backend server
python3 main.py
```

Backend runs on: `http://localhost:5002`

### 3️⃣ Frontend Setup
```bash
cd frontend/trimate-frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: `http://localhost:3000`

---

## 📦 Tech Stack

### **Backend**
- **Framework**: Flask (Python)
- **AI/ML**: LangChain, scikit-learn, pandas, numpy
- **LLM**: Groq API (llama-3.1-8b-instant)
- **APIs**: Amadeus (flights/hotels), Google Places (activities)
- **Database**: MongoDB Atlas (optional)
- **Memory**: In-process conversation storage

### **Frontend**
- **Framework**: React 18
- **UI Library**: Material-UI (MUI)
- **Carousel**: Swiper
- **HTTP Client**: Axios
- **Styling**: CSS Modules

### **Machine Learning**
- **Algorithm**: Item-based collaborative filtering
- **Similarity**: Cosine similarity (sklearn)
- **Dataset**: 6,580 trip records, 25 destinations, 4,614 users
- **Matrix Sparsity**: 94.4% (realistic for travel data)

---

## 🎓 How It Works

### 1️⃣ **User Starts Conversation**
```
User: "Plan a 5-day trip to Bangkok for food lovers, budget $100/day"
```

### 2️⃣ **LangChain Agent Analyzes Query**
- Extracts entities: destination (Bangkok), duration (5 days), interests (food), budget ($100)
- Identifies missing information (departure city, travel dates)
- Asks sequential questions with form suggestions

### 3️⃣ **Agent Uses Tools**
```
Thought: User wants Bangkok trip, need to find flights
Action: FlightPlanner
Action Input: "Delhi to Bangkok, 5 days, Dec 15-20"

Thought: Now need accommodation
Action: HotelPlanner  
Action Input: "Bangkok hotels, food lovers, $100/day budget"

Thought: Need activities for food culture
Action: ActivityRecommender
Action Input: "Bangkok food activities, 5 days"

Thought: Check local events during trip
Action: LocalEventsDiscoverer
Action Input: "Bangkok events Dec 15-20"
```

### 4️⃣ **ML Recommendation (Destinations)**
```python
# Collaborative filtering finds similar destinations
similar_destinations = cf_model.get_similar_destinations('Bangkok')
# Returns: Phuket (85% similar), Chiang Mai (72% similar)...
```

### 5️⃣ **Complete Itinerary Generated**
- Day-by-day plan with morning/afternoon/evening activities
- Flight options (Cheapest, Fastest, Best Overall)
- Hotel recommendations at different price tiers
- Local events happening during travel dates
- Budget breakdown

---

## 📊 Machine Learning Details

### **Collaborative Filtering Model**

```python
# User-Item Matrix (Binary: 1 = visited, 0 = not visited)
User  | Bali | Tokyo | Paris | Bangkok | ...
------|------|-------|-------|---------|----
U001  |   1  |   0   |   1   |    0    | ...
U002  |   1  |   1   |   0   |    1    | ...
U003  |   0  |   1   |   1   |    0    | ...

# Cosine Similarity Matrix (Destination × Destination)
        Bali   Tokyo  Paris  Bangkok
Bali    1.000  0.245  0.189  0.312
Tokyo   0.245  1.000  0.234  0.289
Paris   0.189  0.234  1.000  0.198
Bangkok 0.312  0.289  0.198  1.000
```

**Model Statistics:**
- Training Data: 6,580 trip records
- Destinations: 25 popular locations
- Users: 4,614 synthetic travelers
- Avg Similarity: 0.029 (distinct destination clusters)
- Sparsity: 94.4%

**Recommendation Methods:**
1. `get_similar_destinations()` - Find destinations similar to query
2. `recommend_for_interests()` - Interest-based with CF enhancement
3. `get_user_recommendations()` - Personalized based on past trips

---

## 🗂️ Project Structure

```
tripmate/
├── backend/
│   ├── agents/                    # AI Agents
│   │   ├── langchain_orchestrator.py  # Main LangChain agent
│   │   ├── langchain_tools.py         # Tool definitions
│   │   ├── destination.py             # ML-powered recommendations
│   │   ├── flight.py                  # Amadeus flight integration
│   │   ├── stays.py                   # Hotel recommendations
│   │   ├── activities.py              # Activity suggestions
│   │   └── local_events.py            # Event discovery
│   ├── ml/                        # Machine Learning
│   │   ├── collaborative_filter.py    # CF recommender
│   │   ├── kaggle_trending.py         # Trending analysis
│   │   └── kaggle_activities.py       # Activity patterns
│   ├── services/                  # External Services
│   │   ├── api_clients.py             # Amadeus API client
│   │   ├── activities_service.py      # Google Places integration
│   │   └── flight_service.py          # Flight search logic
│   ├── routes/                    # API Routes
│   │   ├── auth_routes.py             # Authentication
│   │   ├── trip_routes.py             # Trip CRUD
│   │   └── trending.py                # Trending destinations
│   ├── memory/                    # Conversation Memory
│   │   └── conversation_memory.py     # In-memory storage
│   ├── database/                  # Database
│   │   └── models.py                  # MongoDB models
│   └── main.py                    # Flask app entry point
│
└── frontend/
    └── trimate-frontend/
        ├── src/
        │   ├── components/            # React Components
        │   │   ├── ChatInterface.js       # Main chat UI
        │   │   ├── DestinationCarousel.js # Trending carousel
        │   │   ├── FlightCard.js          # Flight display
        │   │   ├── HotelCard.js           # Hotel display
        │   │   └── ActivityCard.js        # Activity display
        │   ├── styles/                # CSS Styles
        │   ├── App.js                 # Main app component
        │   └── MyTrips.js             # Saved trips view
        └── package.json
```

---

## 🔧 Configuration

### **Environment Variables (.env)**

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

# Optional (Enhances features)
GOOGLE_PLACES_API_KEY=your_google_places_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/tripmate_db

# Optional (Additional APIs)
GETYOURGUIDE_API_KEY=your_getyourguide_key
VIATOR_API_KEY=your_viator_key
```

### **API Key Setup Guides**
- **Amadeus**: See `GETTING_REAL_FLIGHTS.md` (FREE tier available)
- **Google Places**: See `GOOGLE_PLACES_SETUP.md` (28,000 requests/month FREE)
- **Groq**: Visit https://console.groq.com (FREE tier available)

---

## 📈 Data Sources

| Component | Data Source | Type | Status |
|-----------|-------------|------|--------|
| **Destinations** | Collaborative Filtering (Kaggle) | ML Model | ✅ Active |
| **Trending** | Kaggle Trip Dataset (6,580 records) | Historical Data | ✅ Active |
| **Flights** | Amadeus API | Live API | ✅ Active |
| **Hotels** | Amadeus API | Live API | ✅ Active |
| **Activities** | Google Places API + Kaggle Patterns | Hybrid | ✅ Active |
| **Events** | Groq LLM (Cultural Calendar) | AI-Generated | ✅ Active |

---

## 🎯 Key Features Breakdown

### **1. Collaborative Filtering (Netflix-style)**
```python
# Example: Find destinations similar to Bali
cf_recommender.get_similar_destinations('Bali', top_n=5)
# Returns:
# 1. Phuket, Thailand - 85% match
# 2. Maldives - 78% match  
# 3. Krabi, Thailand - 72% match
```

### **2. Real-Time Flight Search**
```python
# Amadeus API returns 3 options
flights = flight_service.search_flights(
    origin='DEL',
    destination='BKK', 
    dates='2025-12-15 to 2025-12-20'
)
# Returns: Cheapest, Fastest, Best Overall
```

### **3. Sequential Question Flow**
```
Bot: "Where would you like to go?" → Destination autocomplete
User: "Bangkok"

Bot: "Where will you be flying from?" → City autocomplete  
User: "Delhi"

Bot: "How long do you want to stay?" → Days slider (1-90)
User: "5 days"

Bot: "What's your budget?" → Budget slider ($20-$1000/day)
User: "$100/day"

Bot: "What are your interests?" → Multi-select tags
User: [Food, Culture, Nightlife]

→ Complete itinerary generated
```

### **4. Trending Destinations Carousel**
- Live data from 6,580+ trip records
- Displays: Trip count, avg budget, best time to visit
- Interactive cards with ratings and reviews
- Click to auto-populate trip planner

---

## 🚦 API Endpoints

### **Core Endpoints**
```
POST   /api/generate          # Main chat endpoint
GET    /api/trending-destinations  # ML-powered trending
POST   /api/trips             # Save trip
GET    /api/trips             # Get user trips
DELETE /api/trips/:id         # Delete trip
GET    /api/locations/popular # Popular destinations
GET    /api/locations/search  # Search destinations
```

### **Example Request**
```bash
curl -X POST http://localhost:5002/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Bangkok food culture 5 days $100 per day from Delhi",
    "session_id": "user123"
  }'
```

---

## 🧪 Testing

### **Test Collaborative Filtering**
```bash
cd backend
python3 ml/collaborative_filter.py
```

### **Test Trending Destinations**
```bash
python3 ml/kaggle_trending.py
```

### **Test Backend**
```bash
# Terminal 1: Start backend
cd backend && python3 main.py

# Terminal 2: Test trending API
curl http://localhost:5002/api/trending-destinations | jq
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Kaggle** for travel dataset (6,580 trip records)
- **Amadeus** for flight and hotel APIs
- **Google Places** for activity data
- **Groq** for ultra-fast LLM inference
- **LangChain** for agent orchestration framework

---

## 📧 Contact

**Neha Arora** - [@Neharor](https://github.com/Neharor)

Project Link: [https://github.com/Neharor/tripmate](https://github.com/Neharor/tripmate)

---

## 🎉 What's Next?

- [ ] Add more ML models (price prediction, sentiment analysis)
- [ ] Implement user authentication with JWT
- [ ] Add real-time chat with WebSockets
- [ ] Create mobile app (React Native)
- [ ] Integrate more travel APIs (Skyscanner, Booking.com)
- [ ] Add multi-language support
- [ ] Implement Redis for production memory

---

**Made with ❤️ using AI, ML, and Real-Time APIs**
