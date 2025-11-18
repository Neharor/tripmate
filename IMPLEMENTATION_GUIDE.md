# Quick Implementation Guide - Next Steps

## ✅ Just Implemented

1. **ItineraryAgent** - Generates day-by-day schedules with hour-by-hour activities
2. **FlightAgent** - Provides flight suggestions (ready for API integration)
3. **Frontend** - Now displays itinerary and flights

## 🚀 Quick Wins (Implement Next)

### 1. Add Map Integration (2-3 hours)

**Install Mapbox:**
```bash
cd frontend/trimate-frontend
npm install mapbox-gl react-map-gl
```

**Create Map Component:**
```javascript
// frontend/src/components/Map/TripMap.js
import Map, { Marker, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

export default function TripMap({ locations }) {
  return (
    <Map
      mapboxAccessToken="pk.YOUR_MAPBOX_TOKEN"
      initialViewState={{
        longitude: locations[0]?.lng || 0,
        latitude: locations[0]?.lat || 0,
        zoom: 12
      }}
      style={{width: '100%', height: 400}}
      mapStyle="mapbox://styles/mapbox/streets-v11"
    >
      {locations.map((loc, idx) => (
        <Marker 
          key={idx}
          longitude={loc.lng} 
          latitude={loc.lat}
          color="red"
        />
      ))}
    </Map>
  );
}
```

**Get Mapbox Token:**
1. Go to https://www.mapbox.com/
2. Sign up (free tier: 50,000 loads/month)
3. Copy your access token
4. Add to `.env`: `REACT_APP_MAPBOX_TOKEN=your_token_here`

### 2. Geocoding Service (1-2 hours)

**Backend Service:**
```python
# backend/services/geocoding_service.py
import requests
import os

GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def geocode_location(location_name):
    """
    Convert location name to lat/lng coordinates
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": GOOGLE_MAPS_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return {
            "lat": location['lat'],
            "lng": location['lng'],
            "formatted_address": data['results'][0]['formatted_address']
        }
    return None

# Update ItineraryAgent to include coordinates
def enhance_activity_with_geocoding(activity):
    if 'location' in activity:
        coords = geocode_location(activity['location'])
        if coords:
            activity['coordinates'] = coords
    return activity
```

**Google Maps API Setup:**
1. Go to https://console.cloud.google.com/
2. Enable "Geocoding API" and "Maps JavaScript API"
3. Create API key (free tier: $200 credit/month)
4. Add to `.env`: `GOOGLE_MAPS_API_KEY=your_key_here`

### 3. Real Flight API Integration (3-4 hours)

**Install Amadeus SDK:**
```bash
cd backend
pip install amadeus
```

**Setup Amadeus:**
```python
# backend/integrations/amadeus_client.py
from amadeus import Client, ResponseError

class AmadeusFlightClient:
    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv('AMADEUS_CLIENT_ID'),
            client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
        )
    
    def search_flights(self, origin, destination, departure_date, return_date, adults=1):
        """
        Search for real flight offers
        """
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                returnDate=return_date,
                adults=adults,
                max=5  # Top 5 results
            )
            
            return self.parse_flight_results(response.data)
            
        except ResponseError as error:
            print(f"Amadeus API error: {error}")
            return []
    
    def parse_flight_results(self, flights_data):
        """
        Convert Amadeus response to our format
        """
        parsed_flights = []
        
        for offer in flights_data:
            for itinerary in offer['itineraries']:
                flight = {
                    "airline": self.get_airline_name(itinerary['segments'][0]['carrierCode']),
                    "flight_number": f"{itinerary['segments'][0]['carrierCode']} {itinerary['segments'][0]['number']}",
                    "departure": {
                        "airport": itinerary['segments'][0]['departure']['iataCode'],
                        "time": itinerary['segments'][0]['departure']['at'],
                    },
                    "arrival": {
                        "airport": itinerary['segments'][-1]['arrival']['iataCode'],
                        "time": itinerary['segments'][-1]['arrival']['at'],
                    },
                    "duration": itinerary['duration'],
                    "stops": len(itinerary['segments']) - 1,
                    "price": f"${offer['price']['total']}",
                }
                parsed_flights.append(flight)
        
        return parsed_flights
```

**Get Amadeus API Keys:**
1. Go to https://developers.amadeus.com/
2. Sign up for free tier (2000 API calls/month)
3. Create app and get Client ID + Secret
4. Add to `.env`:
```
AMADEUS_CLIENT_ID=your_client_id
AMADEUS_CLIENT_SECRET=your_secret
```

**Update FlightAgent:**
```python
from integrations.amadeus_client import AmadeusFlightClient

class FlightAgent(BaseAgent):
    def __init__(self):
        super().__init__("FlightAgent", system_prompt)
        self.amadeus_client = AmadeusFlightClient()
    
    def handle_request(self, input_data):
        # Extract destination, dates from memory
        # Call real API
        flights = self.amadeus_client.search_flights(
            origin="JFK",  # Extract from user location or ask
            destination=destination_code,
            departure_date="2024-03-15",  # From memory
            return_date="2024-03-20"
        )
        return {"flights": flights}
```

### 4. Hotel Booking API (3-4 hours)

**Option A: Booking.com API (Affiliate)**
```python
# backend/integrations/booking_client.py
import requests

class BookingComClient:
    def __init__(self):
        self.api_key = os.getenv('BOOKING_COM_API_KEY')
        self.base_url = "https://distribution-xml.booking.com/2.6/json"
    
    def search_hotels(self, city, checkin, checkout, guests=2):
        """
        Search hotels via Booking.com API
        """
        params = {
            "city": city,
            "checkin": checkin,
            "checkout": checkout,
            "guests": guests,
            "rows": 10
        }
        # API call
        # Return real hotel data with booking links
```

**Option B: Google Hotels (Easier)**
```python
def search_hotels_google(city, checkin, checkout):
    """
    Use Google Places API + Hotels search
    """
    # Search for "hotels in {city}"
    # Get place details
    # Include booking.com/expedia links
```

### 5. Export to PDF (2 hours)

**Install PDF Library:**
```bash
pip install reportlab
```

**Create PDF Export:**
```python
# backend/services/pdf_service.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_itinerary_pdf(trip_data):
    """
    Generate downloadable PDF itinerary
    """
    pdf_file = f"itinerary_{trip_data['trip_id']}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, f"Trip to {trip_data['destination']}")
    
    # Dates
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"{trip_data['start_date']} - {trip_data['end_date']}")
    
    # Itinerary
    y = 680
    for day in trip_data['itinerary']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y, f"Day {day['day']}: {day['title']}")
        y -= 20
        
        c.setFont("Helvetica", 10)
        for activity in day['activities']:
            c.drawString(120, y, f"{activity['time']} - {activity['title']}")
            y -= 15
        y -= 10
    
    c.save()
    return pdf_file
```

**Add Download Endpoint:**
```python
@app.route("/api/itinerary/download/<trip_id>", methods=["GET"])
def download_itinerary(trip_id):
    # Get trip data
    # Generate PDF
    # Return file
    return send_file(pdf_file, as_attachment=True)
```

## 📋 Environment Variables Needed

Create `.env` files:

**Backend (.env):**
```bash
GROQ_API_KEY=your_groq_key
GOOGLE_MAPS_API_KEY=your_google_key
AMADEUS_CLIENT_ID=your_amadeus_id
AMADEUS_CLIENT_SECRET=your_amadeus_secret
BOOKING_COM_API_KEY=your_booking_key  # Optional
REDIS_URL=redis://localhost:6379  # When ready
SECRET_KEY=your_flask_secret
```

**Frontend (.env):**
```bash
REACT_APP_MAPBOX_TOKEN=your_mapbox_token
REACT_APP_API_URL=http://localhost:5002
```

## 🎯 Implementation Timeline

**Week 1:**
- ✅ Itinerary agent (Done!)
- ✅ Flight agent structure (Done!)
- ⏳ Map integration
- ⏳ Geocoding service

**Week 2:**
- ⏳ Amadeus flight API
- ⏳ Hotel booking API
- ⏳ Enhanced UI with cards

**Week 3:**
- ⏳ PDF export
- ⏳ Email confirmations
- ⏳ Calendar integration

**Week 4:**
- ⏳ Payment flow (Stripe)
- ⏳ User accounts
- ⏳ Save/load trips

## 📚 Helpful Resources

- Amadeus API Docs: https://developers.amadeus.com/self-service/category/flights
- Google Maps API: https://developers.google.com/maps/documentation
- Mapbox GL JS: https://docs.mapbox.com/mapbox-gl-js/guides/
- Booking.com Partner: https://www.booking.com/affiliate-program
- Stripe Payments: https://stripe.com/docs/payments/quickstart

Let me know which feature you want to implement next!
