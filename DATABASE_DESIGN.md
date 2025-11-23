# TripMate Database Schema Design

## Purpose
Store finalized itineraries for:
- User trip history
- Personalized recommendations
- ML-based insights
- Analytics and trends
- Social sharing

---

## Database Choice: MongoDB (NoSQL)

**Why MongoDB over PostgreSQL?**
- ✅ Flexible schema (trips vary: 3-day vs 30-day, different activities)
- ✅ Easy to store nested data (itinerary days, flights, hotels as subdocuments)
- ✅ Fast reads for recommendations
- ✅ JSON-like structure matches our API responses
- ✅ Horizontal scaling for growth

**Already configured**: MongoDB Atlas connection exists in `.env`

---

## Collections

### 1. `users` Collection
Stores user profiles and preferences

```javascript
{
  _id: ObjectId("..."),
  email: "user@example.com",
  name: "John Doe",
  created_at: ISODate("2025-01-15T10:00:00Z"),
  preferences: {
    favorite_destinations: ["Bali", "Tokyo", "Paris"],
    interests: ["Beach", "Adventure", "Food"],
    budget_range: "$100-200/day",
    food_preference: "Non-vegetarian",
    travel_style: "Adventure"
  },
  stats: {
    total_trips: 5,
    countries_visited: 12,
    total_spent: 15000
  }
}
```

### 2. `trips` Collection
Stores complete trip plans (finalized itineraries)

```javascript
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),  // Reference to users collection
  created_at: ISODate("2025-01-15T10:30:00Z"),
  finalized_at: ISODate("2025-01-15T11:00:00Z"),
  
  // Trip basics
  destination: "Bali, Indonesia",
  departure_city: "Los Angeles",
  duration_days: 5,
  travel_dates: {
    start: ISODate("2025-02-15"),
    end: ISODate("2025-02-20")
  },
  
  // Budget info
  budget: {
    per_day: 100,
    total: 500,
    actual_flights: 950,
    actual_accommodation: 325,
    actual_activities: 180,
    actual_total: 1455
  },
  
  // User preferences for this trip
  preferences: {
    interests: ["Adventure", "Food"],
    food_preference: "Non-vegetarian",
    flight_time_preference: "Morning"
  },
  
  // Flights booked/selected
  flights: {
    outbound: {
      airline: "Singapore Airlines",
      flight_number: "SQ 622",
      departure: {
        airport: "LAX",
        time: ISODate("2025-02-15T11:00:00Z")
      },
      arrival: {
        airport: "DPS",
        time: ISODate("2025-02-16T18:30:00Z")
      },
      duration_mins: 1110,
      stops: 1,
      layover_city: "Singapore",
      price: 950,
      is_real: true,
      data_source: "Amadeus API"
    },
    return: {
      airline: "Singapore Airlines",
      flight_number: "SQ 623",
      departure: {
        airport: "DPS",
        time: ISODate("2025-02-20T20:00:00Z")
      },
      arrival: {
        airport: "LAX",
        time: ISODate("2025-02-21T15:30:00Z")
      },
      duration_mins: 1090,
      stops: 1,
      layover_city: "Singapore",
      price: 0,  // Included in outbound price
      is_real: true
    }
  },
  
  // Accommodation
  stays: [
    {
      name: "The Kayon Resort",
      neighborhood: "Ubud Valley",
      style: "Mid-range boutique",
      price_per_night: 65,
      total_nights: 5,
      total_cost: 325,
      amenities: ["Pool", "Breakfast", "Wifi"],
      rating: 4.5,
      why_chosen: "Infinity pool with rice terraces + onsite restaurant"
    }
  ],
  
  // Day-by-day itinerary
  itinerary: [
    {
      day: 1,
      date: ISODate("2025-02-15"),
      theme: "Ubud Adventure + Food",
      activities: [
        {
          time: "09:00",
          name: "Arrival at DPS Airport",
          type: "travel",
          duration_mins: 0,
          cost: 0
        },
        {
          time: "12:00",
          name: "Lunch at Naughty Nuri's",
          type: "food",
          cuisine: "BBQ",
          food_type: "Non-vegetarian",
          description: "Famous ribs",
          duration_mins: 60,
          cost: 15
        },
        {
          time: "13:30",
          name: "Ubud Monkey Forest",
          type: "activity",
          category: "Culture",
          description: "Sacred forest with macaques",
          duration_mins: 90,
          cost: 5
        },
        {
          time: "17:00",
          name: "Campuhan Ridge Walk",
          type: "activity",
          category: "Nature",
          description: "Scenic valley trail",
          duration_mins: 90,
          cost: 0
        },
        {
          time: "19:00",
          name: "Dinner at Kubu at Mandapa",
          type: "food",
          cuisine: "Fine dining",
          food_type: "Non-vegetarian",
          description: "Fine dining by river",
          duration_mins: 120,
          cost: 45
        }
      ],
      total_cost: 65
    },
    // ... more days
  ],
  
  // Bookable activities/experiences
  bookable_activities: [
    {
      name: "White Water Rafting - Ayung River",
      description: "2-hour rafting through jungle rapids + lunch",
      category: "Adventure",
      price: 35,
      duration_mins: 180,
      booked: true,
      booking_date: ISODate("2025-02-16")
    },
    {
      name: "Balinese Cooking Class at Paon Bali",
      description: "Market visit + hands-on cooking + recipes",
      category: "Food",
      price: 40,
      duration_mins: 180,
      booked: false
    }
  ],
  
  // Metadata for ML/recommendations
  metadata: {
    weather_during_trip: "Sunny, 28-32°C",
    season: "Dry season",
    trip_status: "finalized",  // draft, finalized, completed
    shared_publicly: false,
    user_rating: null,  // After trip completion
    user_feedback: null
  },
  
  // ML features for recommendations
  ml_features: {
    destination_type: "Beach + Culture",
    activity_diversity: 0.85,  // 0-1 score
    budget_category: "mid-range",
    pace: "moderate",  // slow, moderate, fast
    food_focus: 0.4,  // 40% food activities
    adventure_focus: 0.6  // 60% adventure
  }
}
```

### 3. `recommendations_cache` Collection
Cache ML-based recommendations for performance

```javascript
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),
  generated_at: ISODate("2025-01-15T10:00:00Z"),
  expires_at: ISODate("2025-01-16T10:00:00Z"),  // 24-hour cache
  
  recommendations: [
    {
      destination: "Tokyo, Japan",
      confidence_score: 0.92,
      reasons: [
        "Similar to your Bali trip (Culture + Food)",
        "Matches your adventure interests",
        "Within your $100-200/day budget"
      ],
      estimated_cost: {
        flights: 850,
        accommodation: 420,
        activities: 300,
        total: 1570
      }
    },
    // ... more recommendations
  ]
}
```

### 4. `analytics` Collection
Aggregate data for insights and trends

```javascript
{
  _id: ObjectId("..."),
  date: ISODate("2025-01-15"),
  
  popular_destinations: [
    { name: "Bali", trips_count: 245, avg_duration: 5.2, avg_budget: 105 },
    { name: "Tokyo", trips_count: 189, avg_duration: 4.8, avg_budget: 145 }
  ],
  
  popular_routes: [
    { 
      from: "Los Angeles", 
      to: "Bali", 
      trips: 45, 
      avg_price: 920,
      popular_airlines: ["Singapore Airlines", "Korean Air"]
    }
  ],
  
  trending_activities: [
    { name: "White Water Rafting", bookings: 89, avg_price: 35 },
    { name: "Cooking Classes", bookings: 67, avg_price: 42 }
  ]
}
```

---

## Indexes for Performance

```javascript
// users collection
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })

// trips collection
db.trips.createIndex({ "user_id": 1, "created_at": -1 })
db.trips.createIndex({ "destination": 1 })
db.trips.createIndex({ "travel_dates.start": 1 })
db.trips.createIndex({ "metadata.trip_status": 1 })
db.trips.createIndex({ "preferences.interests": 1 })
db.trips.createIndex({ "budget.per_day": 1 })

// recommendations_cache
db.recommendations_cache.createIndex({ "user_id": 1 })
db.recommendations_cache.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })  // TTL index

// analytics
db.analytics.createIndex({ "date": -1 })
```

---

## API Endpoints to Implement

### Trip Management
```
POST   /api/trips              - Save new trip (finalize itinerary)
GET    /api/trips              - Get user's trip history
GET    /api/trips/:id          - Get specific trip details
PUT    /api/trips/:id          - Update trip (e.g., mark as completed)
DELETE /api/trips/:id          - Delete trip
POST   /api/trips/:id/share    - Generate shareable link
```

### Recommendations
```
GET    /api/recommendations    - Get personalized destination recommendations
POST   /api/recommendations/refresh - Force refresh recommendations
```

### Analytics (Admin)
```
GET    /api/analytics/popular-destinations
GET    /api/analytics/price-trends
GET    /api/analytics/user-insights
```

---

## ML Recommendation Algorithm

### Collaborative Filtering
```python
# Find similar users based on:
1. Destinations visited (overlap)
2. Budget range similarity
3. Interest alignment
4. Travel style (pace, food focus, adventure focus)

# Recommend destinations that similar users enjoyed
# but current user hasn't visited yet
```

### Content-Based Filtering
```python
# Analyze user's trip history:
1. Extract features: destination_type, activities, budget, pace
2. Find destinations with similar features
3. Score based on:
   - Interest match (80% weight)
   - Budget compatibility (15% weight)
   - Season/weather alignment (5% weight)
```

### Hybrid Approach
```python
recommendation_score = (
    0.6 * collaborative_score +
    0.4 * content_based_score
)
```

---

## Privacy & Security

### User Data Protection
- Email stored encrypted
- Trips private by default
- Shareable links with UUID (not sequential IDs)
- GDPR compliance: Users can export/delete all data

### Data Retention
- Draft trips: Auto-delete after 30 days of inactivity
- Finalized trips: Keep forever (user history)
- Recommendations cache: Auto-expire after 24 hours
- Analytics: Anonymized aggregate data only

---

## Benefits of This System

### 1. Personalization
```
User books: Bali (Adventure + Food), Tokyo (Culture), Paris (Food)
→ Recommend: Thailand (Adventure + Food + Culture)
→ Skip: Dubai (Luxury + Shopping) - doesn't match interests
```

### 2. Budget Optimization
```
User's Bali trip: $1,455 for 5 days
→ Recommend similar trips: $1,200-1,700 range
→ Show: "Users with similar trips spent $1,350 on average"
```

### 3. Social Proof
```
→ "245 users have planned Bali trips this month"
→ "89% of adventure travelers loved White Water Rafting"
→ "Most popular hotel for your budget: The Kayon Resort"
```

### 4. Continuous Improvement
```
→ Track which recommendations users finalized
→ Learn: Adventure + Food → 85% choose Bali/Thailand/Vietnam
→ Improve: Rank these destinations higher for similar users
```

---

## Implementation Priority

### Phase 1: Basic Storage (Week 1)
- ✅ Create trips collection schema
- ✅ Implement POST /api/trips (save finalized trip)
- ✅ Implement GET /api/trips (user history)
- ✅ Add "Save Trip" button to frontend

### Phase 2: User Profiles (Week 2)
- ✅ Create users collection
- ✅ Simple authentication (email + password)
- ✅ Link trips to users
- ✅ User dashboard showing trip history

### Phase 3: Recommendations (Week 3)
- ✅ Build collaborative filtering
- ✅ Implement GET /api/recommendations
- ✅ Show "Recommended for You" on homepage

### Phase 4: Analytics (Week 4)
- ✅ Build analytics pipeline
- ✅ Admin dashboard
- ✅ Public insights (popular destinations)

---

## Next Steps

1. **Implement MongoDB models** in `backend/models/`
2. **Create API routes** in `backend/routes/`
3. **Add authentication** (JWT or sessions)
4. **Frontend integration** (Save Trip button, My Trips page)
5. **ML recommendation engine** (Python scikit-learn)

Ready to start implementation?
