# 🗺️ Google Places API Setup Guide

## ✅ **FREE Tier: 28,000+ Requests/Month**

---

## 📋 Step 1: Get Your API Key

### 1. Go to Google Cloud Console
https://console.cloud.google.com/

### 2. Create a New Project (or select existing)
- Click "Select a project" → "New Project"
- Name: `TripMate` or any name
- Click "Create"

### 3. Enable Places API
- Go to: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
- Click "Enable"
- Wait 1-2 minutes for activation

### 4. Create API Key
- Go to: https://console.cloud.google.com/apis/credentials
- Click "+ CREATE CREDENTIALS" → "API key"
- Copy your API key (looks like: `AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### 5. Secure Your API Key (Optional but Recommended)
- Click "Edit API key" (pencil icon)
- Under "API restrictions":
  - Select "Restrict key"
  - Check: ✅ Places API
  - Check: ✅ Maps JavaScript API (if using maps)
- Click "Save"

---

## 🔧 Step 2: Add Key to TripMate

### Open: `backend/.env`
```bash
# Replace this line:
GOOGLE_PLACES_API_KEY=your-google-places-api-key-here

# With your actual key:
GOOGLE_PLACES_API_KEY=AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🚀 Step 3: Restart Backend

```bash
cd /Users/nehaarora/Documents/Q7/Mod01/Project/Project/tripmate/backend
lsof -ti:5002 | xargs kill -9 2>/dev/null
python3 main.py
```

You should see:
```
✅ Google Places API configured (FREE tier)
```

Instead of:
```
⚠️  No activities API configured. Using curated database fallback.
```

---

## 📊 Free Tier Limits

| Feature | Free Tier |
|---------|-----------|
| **Text Search** | 1,000 requests/month FREE |
| **Places Details** | 1,000 requests/month FREE |
| **Photos** | 1,000 requests/month FREE |
| **Autocomplete** | 1,000 requests/month FREE |
| **After Free Tier** | $17 per 1,000 requests |

**For TripMate**: You get ~1,000 FREE activity searches per month!

---

## 🎯 What You'll Get

### Real-Time Data:
- ✅ Live attraction ratings from Google Maps
- ✅ Current open/closed status
- ✅ Real user review counts
- ✅ Actual addresses and locations
- ✅ Price levels (Free, $, $$, $$$, $$$$)
- ✅ Photos from Google Maps

### Examples:
```json
{
  "name": "Grand Palace",
  "rating": 4.6,
  "reviews": 156234,
  "price_range": "$20-40",
  "is_open_now": true,
  "location": "Phra Nakhon, Bangkok 10200, Thailand"
}
```

---

## 🔍 Testing Your Setup

After adding the API key, test with:

```bash
curl -X POST http://localhost:5002/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Bangkok food culture 3 days",
    "session_id": "test_places_api"
  }'
```

Activities should now show real Google Places data!

---

## 💰 Cost Monitoring

### Check Usage:
https://console.cloud.google.com/apis/dashboard

### Set Budget Alert:
1. Go to: https://console.cloud.google.com/billing
2. Click "Budgets & alerts"
3. Set alert at $0 (to get notified when leaving free tier)

---

## 🆘 Troubleshooting

### Error: "API key not valid"
- Wait 5-10 minutes after creating key
- Check if Places API is enabled
- Verify key copied correctly (no spaces)

### Error: "This API project is not authorized"
- Enable "Places API" in Google Cloud Console
- Make sure billing is enabled (even for free tier)

### Still Using Curated Database?
- Check `.env` file has correct key
- Restart backend after adding key
- Check backend logs for "Google Places API configured"

---

## 📝 Summary

**Before**: Curated database (static, manually added)
**After**: Google Places API (real-time, live data from Google Maps)

**Cost**: 100% FREE for first 1,000 searches/month ✅

---

Need help? The code is already integrated - just add your API key! 🚀
