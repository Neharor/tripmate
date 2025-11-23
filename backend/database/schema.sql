-- TripMate Database Schema
-- PostgreSQL Database Design

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb
);

-- User Preferences stored as JSONB
-- Example structure:
-- {
--   "food_preference": "non-vegetarian",
--   "budget_range": "50-200",
--   "travel_style": "adventure",
--   "interests": ["beach", "food", "culture"],
--   "preferred_airlines": ["Emirates", "Singapore Airlines"],
--   "accommodation_type": "hotel"
-- }

-- Trips Table (stores all trip plans)
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    destination VARCHAR(255) NOT NULL,
    departure_city VARCHAR(255),
    start_date DATE,
    end_date DATE,
    duration INTEGER, -- in days
    budget_total DECIMAL(10, 2),
    budget_per_day DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'planned', -- planned, ongoing, completed, cancelled
    interests TEXT[], -- array of interests
    food_preference VARCHAR(50),
    companions VARCHAR(50), -- solo, couple, family, friends
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb -- store additional trip details
);

-- Bookings Table (hotels, flights, activities)
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    booking_type VARCHAR(50) NOT NULL, -- flight, hotel, activity
    provider VARCHAR(100), -- Booking.com, Google Flights, Viator, etc.
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    booking_date DATE,
    status VARCHAR(50) DEFAULT 'saved', -- saved, booked, confirmed, cancelled
    booking_url TEXT,
    booking_details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example booking_details structure:
-- For Hotels: {"nights": 3, "room_type": "deluxe", "check_in": "2025-12-25", "check_out": "2025-12-28"}
-- For Flights: {"airline": "Emirates", "flight_number": "EK123", "departure_time": "10:00", "arrival_time": "14:30"}
-- For Activities: {"duration": "4 hours", "meeting_point": "Ubud Center", "time": "09:00"}

-- Itineraries Table (day-by-day plans)
CREATE TABLE itineraries (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    date DATE,
    activities JSONB NOT NULL, -- array of activities for the day
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example activities JSONB:
-- [
--   {"time": "09:00", "activity": "Breakfast at Cafe X", "type": "food", "price": 15},
--   {"time": "11:00", "activity": "Visit Uluwatu Temple", "type": "sightseeing", "price": 10}
-- ]

-- Conversation History Table (for AI context and learning)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    trip_id INTEGER REFERENCES trips(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    role VARCHAR(20) NOT NULL, -- user or assistant
    message TEXT NOT NULL,
    entities JSONB, -- extracted entities
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Saved Destinations (wishlist)
CREATE TABLE saved_destinations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    destination VARCHAR(255) NOT NULL,
    notes TEXT,
    priority INTEGER DEFAULT 0, -- for ranking wishlist
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, destination)
);

-- User Activity Log (for analytics and personalization)
CREATE TABLE user_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL, -- search, view_hotel, view_flight, save_trip, etc.
    activity_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_status ON trips(status);
CREATE INDEX idx_trips_destination ON trips(destination);
CREATE INDEX idx_bookings_trip_id ON bookings(trip_id);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_type ON user_activity(activity_type);

-- Views for common queries
CREATE VIEW user_trip_summary AS
SELECT 
    u.id as user_id,
    u.email,
    COUNT(DISTINCT t.id) as total_trips,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) as completed_trips,
    COUNT(DISTINCT b.id) as total_bookings,
    SUM(b.price) as total_spent
FROM users u
LEFT JOIN trips t ON u.id = t.user_id
LEFT JOIN bookings b ON u.id = b.user_id
GROUP BY u.id, u.email;
