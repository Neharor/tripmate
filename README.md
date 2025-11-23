# TripMate 🌍✈️

AI-powered travel planning assistant that helps you plan trips in seconds with real flight data, hotel recommendations, and personalized itineraries.

## 🚨 **Important: Connect Real Flight API**

**Current Status**: TripMate is using AI-generated flight estimates (not real data)

To get **real flight prices and availability**, follow the setup guide:

📖 **[GETTING_REAL_FLIGHTS.md](./GETTING_REAL_FLIGHTS.md)** - Complete step-by-step guide (10 minutes)

### Quick Setup:
1. Sign up at [Amadeus for Developers](https://developers.amadeus.com/register) (FREE - 2,000 calls/month)
2. Get API Key + Secret
3. Add to `backend/.env`:
   ```bash
   AMADEUS_API_KEY=your_key_here
   AMADEUS_API_SECRET=your_secret_here
   ```
4. Test connection: `python3 backend/test_amadeus.py`
5. Start backend: `python3 backend/main.py`

**After setup**:
- ✅ Real airline prices (not estimates)
- ✅ Actual flight routes (no fake direct flights)
- ✅ Live availability data
- ✅ 95% confidence scores (vs 10% estimates)

---

## Features

- 🤖 **AI-Powered Planning**: Multi-agent system (Destination, Flight, Hotel, Weather, Budget, Stays)
- ✈️ **Real Flight Data**: Live prices from Amadeus API (200+ airlines worldwide)
- 🏨 **Hotel Recommendations**: AI-curated stays based on your preferences
- 💰 **Smart Budget Planning**: Cost breakdown for flights, hotels, food, activities
- 🌤️ **Weather Intelligence**: Climate data to optimize travel dates
- 📊 **Transparency**: Confidence scores showing data quality for each recommendation
- ⚡ **Fast**: Complete trip plans in 5-10 seconds

## Architecture

### Backend (Python/Flask)
- **Orchestrator Agent**: Coordinates all other agents
- **Destination Agent**: Suggests destinations based on preferences
- **Flight Agent**: Searches real flights via Amadeus API
- **Hotel Agent**: Recommends accommodations
- **Weather Agent**: Provides climate insights
- **Budget Agent**: Calculates total trip cost
- **Stays Agent**: Plans daily itineraries

### Frontend (React)
- Material-UI components
- Real-time chat interface
- Confidence indicators
- Trip comparison views

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Amadeus API credentials (free tier available)

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - AMADEUS_API_KEY
   # - AMADEUS_API_SECRET
   # - GROQ_API_KEY
   ```

4. **Test Amadeus connection:**
   ```bash
   python3 test_amadeus.py
   ```
   Should output: `🎉 SUCCESS! Amadeus API is working correctly!`

5. **Start backend server:**
   ```bash
   python3 main.py
   ```
   Backend runs on: `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend/trimate-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```
   Frontend runs on: `http://localhost:3000`

## Usage

1. Open browser to `http://localhost:3000`
2. Enter your travel preferences in the chat:
   - "I want to go to Bali from Tokyo in December"
   - "Find me a beach vacation under $2000"
   - "Plan a 5-day trip to Europe next month"
3. TripMate analyzes your request and returns:
   - Real flight options with prices
   - Hotel recommendations
   - Daily itinerary
   - Budget breakdown
   - Weather forecast
   - Confidence scores for each recommendation

## Project Structure

```
tripmate/
├── backend/
│   ├── main.py                 # Flask app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── test_amadeus.py        # API connection test
│   ├── agents/
│   │   ├── orchestrator.py    # Coordinates all agents
│   │   ├── destination.py     # Destination suggestions
│   │   ├── flight.py          # Flight search (Amadeus)
│   │   ├── stays.py           # Hotel/accommodation
│   │   ├── weather.py         # Weather data
│   │   └── budget.py          # Cost calculations
│   ├── services/
│   │   ├── flight_service.py  # Amadeus API integration
│   │   ├── flight_ranker.py   # Flight scoring system
│   │   └── flight_optimizer.py # Comprehensive search
│   └── realtime/
│       └── socketio_server.py # WebSocket updates
├── frontend/
│   └── trimate-frontend/
│       ├── src/
│       │   ├── App.js         # Main React app
│       │   ├── api.js         # Backend API client
│       │   └── components/
│       │       ├── QueryForm.js              # Search input
│       │       ├── ResultsDisplay.js         # Trip results
│       │       ├── FlightConfidenceIndicator.js  # Transparency UI
│       │       └── ...
│       └── package.json
└── docs/
    ├── GETTING_REAL_FLIGHTS.md      # Flight API setup guide
    ├── AMADEUS_SETUP.md             # Quick Amadeus guide
    ├── PRODUCTION_ARCHITECTURE.md   # System design
    ├── USER_JOURNEY.md              # User experience flows
    └── FLIGHT_TRANSPARENCY.md       # Confidence scoring
```

## API Keys & Environment Variables

### Required:
- `AMADEUS_API_KEY` - Get from [Amadeus for Developers](https://developers.amadeus.com)
- `AMADEUS_API_SECRET` - Get from [Amadeus for Developers](https://developers.amadeus.com)
- `GROQ_API_KEY` - Get from [Groq Cloud](https://console.groq.com)

### Optional:
- `WEATHERAPI_KEY` - For weather data
- `GOOGLE_PLACES_API_KEY` - For hotel search (future)

All keys should be added to `backend/.env` file (never commit this file!)

## Development

### Running Tests
```bash
cd backend
python3 test_amadeus.py  # Test Amadeus API
pytest tests/            # Run unit tests (if implemented)
```

### Debugging
- Backend logs: Check terminal running `main.py`
- Frontend logs: Check browser console (F12)
- API errors: Look for "❌" symbols in backend terminal

## Troubleshooting

### "Amadeus API credentials not found"
- Ensure `.env` file is in `backend/` directory
- Verify `AMADEUS_API_KEY` and `AMADEUS_API_SECRET` are set
- Check for typos or extra spaces in credentials

### "No flights found"
- Try different routes (e.g., JFK→LHR, LAX→NRT)
- Use dates 30-60 days in the future
- Check [Amadeus API Status](https://developers.amadeus.com/status)

### Frontend won't connect to backend
- Ensure backend is running on port 5000
- Check CORS settings in `main.py`
- Verify `api.js` has correct backend URL

### Still showing fake flight data
- Restart backend (Ctrl+C then `python3 main.py`)
- Look for "✅ Amadeus API connected successfully!" message
- Clear browser cache and retry

See **[GETTING_REAL_FLIGHTS.md](./GETTING_REAL_FLIGHTS.md)** for detailed troubleshooting.

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Roadmap

- [x] Multi-agent planning system
- [x] Amadeus flight API integration
- [x] Flight ranking & confidence scoring
- [x] Transparency UI (FlightConfidenceIndicator)
- [ ] Real-time WebSocket updates
- [ ] Hotel API integration (Booking.com / Hotels.com)
- [ ] User authentication & saved trips
- [ ] Trip comparison tool
- [ ] Mobile app (React Native)
- [ ] Email/SMS notifications
- [ ] Social sharing of itineraries

## Support

For questions or issues:
1. Check **[GETTING_REAL_FLIGHTS.md](./GETTING_REAL_FLIGHTS.md)** for setup help
2. Review **[PRODUCTION_ARCHITECTURE.md](./PRODUCTION_ARCHITECTURE.md)** for system design
3. Open an issue on GitHub

---

**Built with ❤️ using AI, Flask, React, and Amadeus API**

