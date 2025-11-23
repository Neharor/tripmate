# 🚀 Getting Real Flight Data: Complete Setup Guide

**Current Status**: TripMate is using LLM-generated flight estimates (fake data)  
**Goal**: Connect to Amadeus API for real-time flight prices and availability  
**Time Required**: 10 minutes  

---

## Why You Need This

Right now, when users search for flights, TripMate shows:
- ❌ **Fake airlines** (Lion Air on routes they don't fly)
- ❌ **Impossible routes** (Tokyo→Bali "direct" when no such flight exists)
- ❌ **Estimated prices** (not real bookable prices)
- ❌ **Low confidence** (10% - basically guessing)

After connecting Amadeus API:
- ✅ **Real airlines** (only airlines that actually fly the route)
- ✅ **Actual routes** (shows real stops like Singapore, Jakarta)
- ✅ **Live prices** (actual bookable prices from airlines)
- ✅ **High confidence** (95% - verified real data)

---

## Step 1: Sign Up for Amadeus (5 minutes)

### 1.1 Create Account
1. Go to: **https://developers.amadeus.com/register**
2. Fill in:
   - Email: `your_email@example.com`
   - Password: (choose strong password)
   - Company: `TripMate` (or your company name)
   - Country: Select your country
3. Click **"Create Account"**
4. **Verify email** (check inbox/spam)

### 1.2 Create Your App
1. After login, click **"My Apps"** or **"Create New App"**
2. Fill in:
   - App Name: `TripMate`
   - Description: `AI-powered trip planning assistant`
3. Click **"Create"**

### 1.3 Get API Credentials
You'll see two important values:

```
API Key:    aBcD3fGh1JkLmN0pQrStUvWx  (example)
API Secret: YzX2WvU1tSrQ0pOnMlKjI9hG  (example)
```

**IMPORTANT**: Copy both values immediately! You'll need them in the next step.

---

## Step 2: Add Credentials to Your Project (2 minutes)

### 2.1 Open Your .env File
Navigate to: `/Users/mokalra/Documents/tripmate/backend/.env`

If this file doesn't exist, create it:
```bash
cd /Users/mokalra/Documents/tripmate/backend
touch .env
```

### 2.2 Add Amadeus Credentials
Open `.env` in VS Code or any text editor and add:

```bash
# Amadeus Flight API (Real-time flight data)
AMADEUS_API_KEY=your_actual_api_key_here
AMADEUS_API_SECRET=your_actual_api_secret_here

# Replace "your_actual_api_key_here" with the API Key from Step 1.3
# Replace "your_actual_api_secret_here" with the API Secret from Step 1.3
```

**Example (with fake credentials)**:
```bash
AMADEUS_API_KEY=aBcD3fGh1JkLmN0pQrStUvWx
AMADEUS_API_SECRET=YzX2WvU1tSrQ0pOnMlKjI9hG
```

### 2.3 Keep Your .env Safe
- ✅ `.env` is already in `.gitignore` (won't be committed to git)
- ❌ **NEVER share your .env file or credentials publicly**
- ❌ **NEVER commit .env to GitHub**

---

## Step 3: Install Amadeus SDK (1 minute)

Open terminal and run:

```bash
cd /Users/mokalra/Documents/tripmate/backend
pip install -r requirements.txt
```

This installs:
- `amadeus==8.1.0` (Amadeus Python SDK)
- `Flask-SocketIO==5.3.5` (Real-time updates)
- All other dependencies

**Verify installation**:
```bash
python3 -c "import amadeus; print('✅ Amadeus SDK installed!')"
```

Should output: `✅ Amadeus SDK installed!`

---

## Step 4: Test API Connection (2 minutes)

Before starting the main app, verify Amadeus works:

```bash
cd /Users/mokalra/Documents/tripmate/backend
python3 test_amadeus.py
```

### Expected Output:
```
============================================================
🧪 AMADEUS API CONNECTION TEST
============================================================

📋 Step 1: Checking credentials...
✅ API Key found: aBcD3fGh...
✅ API Secret found: YzX2WvU1...

📦 Step 2: Importing Amadeus SDK...
✅ Amadeus SDK imported successfully!

🔗 Step 3: Connecting to Amadeus API...
✅ Amadeus client initialized!

✈️  Step 4: Testing flight search (Tokyo → Bali)...
✅ Flight search successful!

📊 RESULTS:
Found 3 flight offers:

Flight #1:
  💰 Price: USD 850.00
  ✈️  Airline: SQ
  🛫 Route: 1 stop(s)
  ⏱️  Duration: PT10H30M
      Segment 1: NRT → SIN
         Depart: 2024-12-15T09:30:00
         Arrive: 2024-12-15T16:00:00
      Segment 2: SIN → DPS
         Depart: 2024-12-15T18:15:00
         Arrive: 2024-12-15T21:00:00

🎉 SUCCESS! Amadeus API is working correctly!
```

### If You See Errors:

**❌ "Credentials not found"**
- Solution: Check Step 2 - make sure `.env` file has correct credentials

**❌ "Amadeus SDK not installed"**
- Solution: Run `pip install amadeus` or `pip install -r requirements.txt`

**❌ "Invalid credentials" / "401 Unauthorized"**
- Solution: Double-check API Key and Secret from Amadeus dashboard
- Make sure you copied them exactly (no extra spaces)

**❌ "No flights found"**
- This is OK! It means API works but route/date has no availability
- The test still passed - API connection is working

---

## Step 5: Start Backend with Real Data (30 seconds)

Now start (or restart) your backend:

```bash
cd /Users/mokalra/Documents/tripmate/backend
python3 main.py
```

### Look for This Success Message:
```
✅ Amadeus API connected successfully!
   API Key: aBcD3fGh...
 * Running on http://127.0.0.1:5000
```

If you see this, **CONGRATULATIONS!** 🎉 Your backend is now using real Amadeus data!

### If Backend Won't Start:
- Check for any Python errors in terminal
- Verify `.env` file is in `/backend/` directory (not `/backend/agents/`)
- Make sure all packages installed: `pip install -r requirements.txt`

---

## Step 6: Test Real Flights in Frontend (1 minute)

1. Make sure frontend is running:
   ```bash
   cd /Users/mokalra/Documents/tripmate/frontend/trimate-frontend
   npm start
   ```

2. Open browser: `http://localhost:3000`

3. Search for a flight:
   - Example: "I want to go from Tokyo to Bali on December 15"

4. Check the results:
   - ✅ Should show real airlines (Singapore Airlines, Garuda Indonesia)
   - ✅ Should show actual routes (e.g., "1 stop via Singapore")
   - ✅ Should show real prices in USD
   - ✅ Should NOT show impossible direct flights

---

## Verification Checklist

Before considering setup complete, verify:

- [ ] `.env` file has AMADEUS_API_KEY and AMADEUS_API_SECRET
- [ ] `pip install -r requirements.txt` completed successfully
- [ ] `python3 test_amadeus.py` shows "🎉 SUCCESS!"
- [ ] Backend starts with "✅ Amadeus API connected successfully!"
- [ ] Frontend search returns real flight data
- [ ] No more "Lion Air" on Seoul-Tokyo routes
- [ ] No more "Direct Tokyo→Bali" impossible flights

---

## Understanding Your Free Tier Limits

Amadeus provides a **FREE tier** with:
- **2,000 API calls per month**
- Resets every month
- More than enough for development/testing

### How Many Calls Does TripMate Use?

For each trip search:
- 1 call for outbound flights
- 1 call for return flights (if round-trip)
- **Total: 1-2 calls per search**

So 2,000 calls = **1,000+ trip searches per month** (plenty for testing!)

### Monitoring Your Usage:
1. Login to https://developers.amadeus.com
2. Go to **"My Apps"** → **"TripMate"**
3. Click **"Analytics"**
4. See: Calls made today/this month

---

## Troubleshooting Common Issues

### Issue 1: "API not connected" message in backend logs

**Cause**: `.env` file not found or credentials missing

**Solution**:
```bash
# Check if .env exists
ls -la /Users/mokalra/Documents/tripmate/backend/.env

# If missing, create it:
touch /Users/mokalra/Documents/tripmate/backend/.env

# Add credentials (use your actual values):
echo "AMADEUS_API_KEY=your_key_here" >> /Users/mokalra/Documents/tripmate/backend/.env
echo "AMADEUS_API_SECRET=your_secret_here" >> /Users/mokalra/Documents/tripmate/backend/.env
```

### Issue 2: Still seeing fake flight data

**Cause**: Backend using cached fallback mode

**Solution**:
1. Stop backend (Ctrl+C)
2. Verify `.env` credentials correct
3. Restart backend: `python3 main.py`
4. Check for "✅ Amadeus API connected successfully!" message
5. Clear browser cache and retry search

### Issue 3: "ResponseError: 401 Unauthorized"

**Cause**: Invalid credentials

**Solution**:
1. Go to https://developers.amadeus.com/my-apps
2. Find your "TripMate" app
3. **Regenerate** API Key/Secret if needed
4. Update `.env` with new values
5. Restart backend

### Issue 4: "No flights found" for every search

**Cause**: Could be valid (route/date has no availability) or test environment issue

**Solution**:
1. Try different routes:
   - Tokyo (NRT) → Singapore (SIN)
   - New York (JFK) → London (LHR)
   - Los Angeles (LAX) → Tokyo (NRT)
2. Try dates 30-60 days in the future
3. Check Amadeus dashboard for API status

---

## What Happens Next?

Once Amadeus is connected, TripMate automatically:

1. **FlightService** switches from `fallback_mode` → `real_api_mode`
2. **Every flight search** now queries Amadeus live database
3. **Results include**:
   - Real airline names (Singapore Airlines, Qatar Airways)
   - Actual flight numbers (SQ 622, QR 946)
   - Live prices in USD/local currency
   - Real departure/arrival times
   - Accurate duration and stops
4. **Confidence scores** jump from 10% → 95%+
5. **FlightConfidenceIndicator** shows:
   - "✅ 95% High Confidence"
   - "Checked 47 real flights from Amadeus API"
   - "Data Source: Live API"

---

## Future Enhancements (Already Coded!)

Once Amadeus is working, we can enable:

### 1. FlightOptimizer (Comprehensive Search)
- Searches ±3 days for better prices
- Checks alternative routes via hubs
- Validates routes exist (no fake direct flights)
- Returns confidence score based on data quality

### 2. FlightRanker (Intelligent Scoring)
- Ranks flights by weighted criteria:
  - Price (40%)
  - Duration (25%)
  - Time preference (15%)
  - Number of stops (10%)
  - Airline quality (10%)
- Generates pros/cons for each flight
- Explains why #1 flight is "best"

### 3. Real-Time Status Updates (WebSocket)
- Shows live agent progress: "✈️ Searching flights... 40%"
- Updates as each airline is checked
- Final: "✅ Found best flights in 2.3 seconds!"

All these features are **already built** - they just need Amadeus API to be active!

---

## Support

### Need Help?

1. **Check test_amadeus.py output** - shows exact error
2. **Review backend logs** when starting main.py
3. **Verify .env file location** - must be in `/backend/` not `/backend/agents/`
4. **Confirm credentials** - copy directly from Amadeus dashboard

### Still Stuck?

Common fixes:
```bash
# Reinstall dependencies
pip install --upgrade amadeus

# Verify Python version (3.8+ required)
python3 --version

# Check .env is being loaded
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('AMADEUS_API_KEY'))"
```

---

## Success Metrics

You'll know it's working when:

✅ `test_amadeus.py` shows real flight data  
✅ Backend logs: "✅ Amadeus API connected successfully!"  
✅ Frontend shows realistic airlines for each route  
✅ No more impossible direct flights  
✅ Prices are in real USD amounts (not estimates)  
✅ Flight numbers include airline code (SQ 622, not just "622")  

---

**Ready to start?** Begin with **Step 1** above! 🚀

The entire process takes about 10 minutes and transforms TripMate from showing fake estimates to displaying real, bookable flight data.
