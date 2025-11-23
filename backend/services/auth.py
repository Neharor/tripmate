"""
Authentication service for TripMate
Handles user registration, login, and JWT tokens
"""

from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from flask import request, jsonify
from database.models import User, get_session


SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated


def register_user(email, password, full_name=None):
    """Register a new user"""
    session = get_session()
    
    try:
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            return {'error': 'User with this email already exists'}, 400
        
        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            preferences={}
        )
        user.set_password(password)
        
        session.add(user)
        session.commit()
        
        # Generate token
        token = generate_token(user.id, user.email)
        
        return {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': token
        }, 201
        
    except Exception as e:
        session.rollback()
        return {'error': str(e)}, 500
    finally:
        session.close()


def login_user(email, password):
    """Login user and return token"""
    session = get_session()
    
    try:
        # Find user
        user = session.query(User).filter_by(email=email).first()
        if not user:
            return {'error': 'Invalid email or password'}, 401
        
        # Verify password
        if not user.check_password(password):
            return {'error': 'Invalid email or password'}, 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Generate token
        token = generate_token(user.id, user.email)
        
        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        session.close()


def get_user_profile(user_id):
    """Get user profile with stats"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return {'error': 'User not found'}, 404
        
        # Get user stats
        total_trips = len(user.trips)
        completed_trips = len([t for t in user.trips if t.status == 'completed'])
        total_bookings = len(user.bookings)
        
        profile = user.to_dict()
        profile['stats'] = {
            'total_trips': total_trips,
            'completed_trips': completed_trips,
            'total_bookings': total_bookings
        }
        
        return profile, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        session.close()


def update_user_preferences(user_id, preferences):
    """Update user preferences for personalization"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return {'error': 'User not found'}, 404
        
        # Merge new preferences with existing
        current_prefs = user.preferences or {}
        current_prefs.update(preferences)
        user.preferences = current_prefs
        
        session.commit()
        
        return {
            'message': 'Preferences updated successfully',
            'preferences': user.preferences
        }, 200
        
    except Exception as e:
        session.rollback()
        return {'error': str(e)}, 500
    finally:
        session.close()
