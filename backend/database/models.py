"""
SQLAlchemy database models for TripMate
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Date, Text, ARRAY, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.hash import bcrypt
import os

Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON, default={})  # JSONB in PostgreSQL
    
    # Relationships
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    saved_destinations = relationship("SavedDestination", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.verify(password, self.password_hash)
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'preferences': self.preferences
        }


class Trip(Base):
    """Trip planning model"""
    __tablename__ = 'trips'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    destination = Column(String(255), nullable=False)
    departure_city = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    duration = Column(Integer)  # in days
    budget_total = Column(Numeric(10, 2))
    budget_per_day = Column(Numeric(10, 2))
    status = Column(String(50), default='planned')  # planned, ongoing, completed, cancelled
    interests = Column(ARRAY(String))
    food_preference = Column(String(50))
    companions = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="trip")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'departure_city': self.departure_city,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration': self.duration,
            'budget_total': float(self.budget_total) if self.budget_total else None,
            'budget_per_day': float(self.budget_per_day) if self.budget_per_day else None,
            'status': self.status,
            'interests': self.interests,
            'food_preference': self.food_preference,
            'companions': self.companions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }


class Booking(Base):
    """Booking model for flights, hotels, activities"""
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    booking_type = Column(String(50), nullable=False)  # flight, hotel, activity
    provider = Column(String(100))  # Booking.com, Google Flights, etc.
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    currency = Column(String(10), default='USD')
    booking_date = Column(Date)
    status = Column(String(50), default='saved')  # saved, booked, confirmed, cancelled
    booking_url = Column(Text)
    booking_details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'booking_type': self.booking_type,
            'provider': self.provider,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'status': self.status,
            'booking_url': self.booking_url,
            'booking_details': self.booking_details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Itinerary(Base):
    """Day-by-day itinerary model"""
    __tablename__ = 'itineraries'
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(Date)
    activities = Column(JSON, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = relationship("Trip", back_populates="itineraries")
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'day_number': self.day_number,
            'date': self.date.isoformat() if self.date else None,
            'activities': self.activities,
            'notes': self.notes
        }


class Conversation(Base):
    """Conversation history for AI context"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='SET NULL'))
    session_id = Column(String(255))
    role = Column(String(20), nullable=False)  # user or assistant
    message = Column(Text, nullable=False)
    entities = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    trip = relationship("Trip", back_populates="conversations")
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'message': self.message,
            'entities': self.entities,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class SavedDestination(Base):
    """User's wishlist destinations"""
    __tablename__ = 'saved_destinations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    destination = Column(String(255), nullable=False)
    notes = Column(Text)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_destinations")
    
    def to_dict(self):
        return {
            'id': self.id,
            'destination': self.destination,
            'notes': self.notes,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserActivity(Base):
    """Track user activity for analytics and personalization"""
    __tablename__ = 'user_activity'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(100), nullable=False)
    activity_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'activity_data': self.activity_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# Database setup functions
def get_database_url():
    """Get database URL from environment or use SQLite for development"""
    return os.getenv('DATABASE_URL', 'sqlite:///tripmate.db')


def create_database_engine():
    """Create SQLAlchemy engine"""
    return create_engine(get_database_url(), echo=True)


def init_database():
    """Initialize database tables"""
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()
