# Amadeus API Setup Guide

## 🚀 Get FREE Real-Time Flight Data

### Step 1: Create Account (2 minutes)
1. Go to: https://developers.amadeus.com/register
2. Fill in:
   - Email
   - Password
   - Company: "TripMate" or "Personal Project"
   - Use case: "Travel Planning Application"
3. Verify email

### Step 2: Create App & Get Credentials (1 minute)
1. Login to: https://developers.amadeus.com/my-apps
2. Click "Create New App"
3. Name: "TripMate"
4. Get your credentials:
   ```
   API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   API Secret: yyyyyyyyyyyyyyyyyyyy
   ```

### Step 3: Add to Environment Variables
```bash
# In /Users/mokalra/Documents/tripmate/backend/.env
AMADEUS_API_KEY=your_api_key_here
AMADEUS_API_SECRET=your_api_secret_here
```

### Free Tier Limits
- ✅ 2,000 API calls per month (FREE!)
- ✅ Access to:
  - Flight Offers Search (real-time prices)
  - Flight Inspiration Search
  - Airport & City Search
  - Hotel Search
  - Points of Interest

### Test Your Credentials
```bash
cd /Users/mokalra/Documents/tripmate/backend
pip install amadeus
python3 -c "
from amadeus import Client, ResponseError
import os
from dotenv import load_dotenv

load_dotenv()

amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='NRT',  # Tokyo Narita
        destinationLocationCode='DPS',  # Bali
        departureDate='2024-12-01',
        adults=1
    )
    print(f'✅ SUCCESS! Found {len(response.data)} flights')
    print(f'First flight: {response.data[0][\"price\"][\"total\"]} {response.data[0][\"price\"][\"currency\"]}')
except ResponseError as error:
    print(f'❌ ERROR: {error}')
"
```

If you see "✅ SUCCESS!" - you're ready to go! 🎉
