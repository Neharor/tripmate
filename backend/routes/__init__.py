# API Routes for TripMate
from .trips import trips_bp
from .auth import auth_bp
from .recommendations import recommendations_bp

__all__ = ['trips_bp', 'auth_bp', 'recommendations_bp']
