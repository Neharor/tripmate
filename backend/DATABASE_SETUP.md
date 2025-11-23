# TripMate Database & Authentication Setup

## 🎯 Why We Need This

Currently, TripMate has **ZERO persistence**:
- ❌ Conversations lost on refresh
- ❌ No user accounts
- ❌ Can't save trips or bookings
- ❌ No personalized recommendations
- ❌ Random session IDs that don't persist

With database integration:
- ✅ User login/signup with secure passwords
- ✅ Save trips, bookings, itineraries
- ✅ Track past trips for recommendations
- ✅ Remember preferences (food, budget, interests)
- ✅ Wishlist destinations
- ✅ Trip history: "Show me my Bali trip from last year"

---

## 📊 Database Architecture

### Tables Created

1. **users** - User accounts with preferences
2. **trips** - All trip plans (past and future)
3. **bookings** - Saved hotels, flights, activities
4. **itineraries** - Day-by-day plans
5. **conversations** - AI chat history for context
6. **saved_destinations** - User wishlist
7. **user_activity** - Analytics for personalization

### Relationships

```
User (1) ──> (Many) Trips
  │
  ├──> (Many) Bookings
  ├──> (Many) Conversations
  └──> (Many) SavedDestinations

Trip (1) ──> (Many) Bookings
  │
  └──> (Many) Itineraries
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New packages added:
- `SQLAlchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL driver
- `PyJWT` - JWT tokens for authentication
- `passlib` - Password hashing
- `bcrypt` - Secure password encryption

### 2. Choose Database

**Option A: SQLite (Quick Start - Development)**
```bash
# No setup needed - uses local file
# File will be created at: backend/tripmate.db
```

**Option B: PostgreSQL (Production - Recommended)**
```bash
# Install PostgreSQL
brew install postgresql  # macOS
# or use Docker:
docker run --name tripmate-db -e POSTGRES_PASSWORD=mysecret -p 5432:5432 -d postgres

# Create database
createdb tripmate

# Set environment variable
export DATABASE_URL="postgresql://username:password@localhost:5432/tripmate"
```

### 3. Initialize Database

```python
# Run this to create all tables
python -c "from database.models import init_database; init_database()"
```

Or create a script:

```bash
cd backend
python << EOF
from database.models import init_database
engine = init_database()
print("✅ Database initialized successfully!")
EOF
```

### 4. Update Environment Variables

Add to `backend/.env`:

```env
# Existing
GROQ_API_KEY=your_groq_key

# New - Database
DATABASE_URL=sqlite:///tripmate.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/tripmate

# JWT Secret (change this to a random string)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 5. Integrate with Flask App

Update `backend/main.py`:

```python
from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.trip_routes import trip_bp
from database.models import init_database

app = Flask(__name__)
CORS(app)

# Initialize database on startup
init_database()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(trip_bp, url_prefix='/api/trips')

# Existing /api/generate route
@app.route('/api/generate', methods=['POST'])
def generate():
    # ... existing code ...
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
```

---

## 🔐 API Endpoints

### Authentication

**Register User**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "John Doe"
}

Response:
{
  "message": "User registered successfully",
  "user": {...},
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

Response:
{
  "message": "Login successful",
  "user": {...},
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Get Profile**
```bash
GET /api/auth/profile
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "preferences": {...},
  "stats": {
    "total_trips": 5,
    "completed_trips": 3,
    "total_bookings": 12
  }
}
```

### Trips

**Create Trip**
```bash
POST /api/trips
Authorization: Bearer <token>
Content-Type: application/json

{
  "destination": "Bali, Indonesia",
  "departure_city": "Bangkok, Thailand",
  "start_date": "2025-12-25",
  "end_date": "2025-12-30",
  "duration": 5,
  "budget_per_day": 200,
  "interests": ["beach", "food", "adventure"],
  "food_preference": "non-vegetarian"
}
```

**Get All Trips**
```bash
GET /api/trips?status=completed
Authorization: Bearer <token>
```

**Save Booking**
```bash
POST /api/trips/1/bookings
Authorization: Bearer <token>

{
  "booking_type": "hotel",
  "provider": "Booking.com",
  "name": "The Griya Villas and Spa",
  "price": 450,
  "booking_url": "https://booking.com/...",
  "booking_details": {
    "check_in": "2025-12-25",
    "check_out": "2025-12-30"
  }
}
```

**Get Recommendations**
```bash
GET /api/trips/recommendations
Authorization: Bearer <token>

Response:
{
  "profile": {
    "destinations_visited": ["Bali", "Thailand", "Paris"],
    "average_budget": 150,
    "top_interests": ["beach", "food", "culture"]
  },
  "suggested_destinations": ["Phuket", "Maldives", "Santorini"]
}
```

---

## 🔄 How It Works Together

### Current Flow (No DB)
```
User → Query → AI Agent → Response → (Lost on refresh)
```

### New Flow (With DB)
```
User Login → JWT Token → Stored in LocalStorage
  ↓
Query → AI Agent → Response
  ↓
Save to Database:
  - Trip created
  - Conversation logged
  - User activity tracked
  ↓
Next time: Load past trips, preferences, personalized suggestions
```

### Personalization Example

**First Trip:**
```
User: "I want to go to Bali"
- Budget: $200/day
- Interests: Beach, Food
- Food: Non-vegetarian
→ Stored in database
```

**Second Trip (Months Later):**
```
User: "Suggest a beach destination"
AI: "Based on your Bali trip (loved beach + food), 
     I recommend Phuket, Thailand or Maldives.
     Your usual budget is $200/day - want similar?"
→ Uses past trip data for smart suggestions
```

---

## 📱 Frontend Integration

Update `frontend/src/api.js`:

```javascript
// Add auth endpoints
export const register = async (email, password, fullName) => {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName })
  });
  const data = await response.json();
  if (data.token) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  return data;
};

export const login = async (email, password) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  if (data.token) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  return data;
};

// Add token to all requests
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

export const createTrip = async (tripData) => {
  const response = await fetch(`${API_BASE}/trips`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(tripData)
  });
  return response.json();
};

export const getUserTrips = async () => {
  const response = await fetch(`${API_BASE}/trips`, {
    headers: getAuthHeaders()
  });
  return response.json();
};
```

---

## 🎨 UI Components Needed

1. **Login/Signup Modal**
   - Email + Password fields
   - "Remember me" checkbox
   - Social login (Google, Facebook) - future

2. **User Profile Page**
   - Past trips timeline
   - Saved bookings
   - Preferences editor
   - Trip statistics

3. **Trip History Page**
   - List of all trips (planned, completed)
   - Click to view details
   - "Book Again" button for past trips

4. **Saved Trips Panel**
   - Heart icon on hotels/flights to save
   - View saved items
   - One-click book from saved

5. **Recommendations Widget**
   - "Based on your past trips..."
   - Suggested destinations
   - Budget recommendations

---

## 🚧 Implementation Priority

**Phase 1: Core Auth (Week 1)**
- ✅ Database schema created
- ✅ User model with password hashing
- ✅ JWT authentication
- ✅ Login/Register endpoints
- ⏳ Frontend login modal
- ⏳ Token storage in localStorage

**Phase 2: Trip Persistence (Week 2)**
- ✅ Trip model and CRUD
- ✅ Booking model
- ✅ Save trip from conversation
- ⏳ "My Trips" page in frontend
- ⏳ Trip details view

**Phase 3: Personalization (Week 3)**
- ✅ User activity tracking
- ✅ Recommendation engine basics
- ⏳ ML-based suggestions (future)
- ⏳ "Similar destinations" feature

**Phase 4: Advanced (Week 4+)**
- ⏳ Social features (share trips)
- ⏳ Collaborative trip planning
- ⏳ Real booking confirmations
- ⏳ Email notifications
- ⏳ Mobile app (React Native)

---

## 🔒 Security Best Practices

1. **Password Security**
   - Hashed with bcrypt (never stored plain text)
   - Salted to prevent rainbow table attacks

2. **JWT Tokens**
   - Expire after 24 hours
   - Stored in httpOnly cookies (not localStorage for production)
   - Refresh token for long sessions

3. **SQL Injection Protection**
   - SQLAlchemy ORM (parameterized queries)
   - Never concatenate user input in SQL

4. **Environment Variables**
   - Never commit `.env` to git
   - Use different secrets for dev/prod

---

## 📈 Analytics & Insights

Track user behavior:

```python
# When user views a hotel
log_user_activity(user_id, 'view_hotel', {
    'hotel_name': 'The Griya Villas',
    'destination': 'Bali',
    'price': 450
})

# When user saves a trip
log_user_activity(user_id, 'save_trip', {
    'destination': 'Bali',
    'budget': 1000
})
```

Query insights:

```sql
-- Most popular destinations
SELECT destination, COUNT(*) as trips
FROM trips
GROUP BY destination
ORDER BY trips DESC
LIMIT 10;

-- Average budget by destination
SELECT destination, AVG(budget_per_day) as avg_budget
FROM trips
WHERE budget_per_day IS NOT NULL
GROUP BY destination;

-- User retention (users who came back)
SELECT COUNT(DISTINCT user_id)
FROM trips
WHERE user_id IN (
    SELECT user_id FROM trips
    GROUP BY user_id
    HAVING COUNT(*) > 1
);
```

---

## 🐛 Troubleshooting

**Error: "Import jwt could not be resolved"**
```bash
pip install PyJWT
```

**Error: "No module named psycopg2"**
```bash
pip install psycopg2-binary
```

**Error: "relation 'users' does not exist"**
```bash
# Run database initialization
python -c "from database.models import init_database; init_database()"
```

**Error: "Invalid token"**
- Token expired (24h limit) - user needs to login again
- Check JWT_SECRET_KEY matches between creation and verification

---

## 🎯 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Initialize database**: Run init script
3. **Update main.py**: Register auth/trip blueprints
4. **Test endpoints**: Use Postman or curl
5. **Build frontend login**: Create LoginModal component
6. **Integrate**: Connect chat to authenticated trips

This gives you a production-ready foundation for user management and trip persistence! 🚀
