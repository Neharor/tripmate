"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Will be set by main.py
user_model = None


def init_auth_routes(user_model_instance):
    """Initialize routes with User model instance"""
    global user_model
    user_model = user_model_instance


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Create new user account
    
    POST /api/auth/signup
    Body: {
        "email": "user@example.com",
        "password": "password123",
        "name": "John Doe"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Create user
        user = user_model.create_user(email, password, name)
        
        # Set session
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        
        return jsonify({
            "message": "Account created successfully",
            "user": {
                "id": str(user['_id']),
                "email": user['email'],
                "name": user['name']
            }
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Signup failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    
    POST /api/auth/login
    Body: {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Verify credentials
        user = user_model.verify_password(email, password)
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Set session
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(user['_id']),
                "email": user['email'],
                "name": user['name'],
                "stats": user.get('stats', {})
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout user
    
    POST /api/auth/logout
    """
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current logged-in user info
    
    GET /api/auth/me
    """
    try:
        user_id = session.get('user_id')
        user = user_model.find_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": str(user['_id']),
            "email": user['email'],
            "name": user['name'],
            "preferences": user.get('preferences', {}),
            "stats": user.get('stats', {})
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get user: {str(e)}"}), 500


@auth_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """
    Update user preferences
    
    PUT /api/auth/preferences
    Body: {
        "interests": ["Beach", "Adventure"],
        "budget_range": "$100-200/day",
        "food_preference": "Vegetarian"
    }
    """
    try:
        user_id = session.get('user_id')
        preferences = request.get_json()
        
        success = user_model.update_preferences(user_id, preferences)
        
        if success:
            return jsonify({"message": "Preferences updated"}), 200
        else:
            return jsonify({"error": "Update failed"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500
