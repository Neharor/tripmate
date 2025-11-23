"""
API routes for authentication and user management
"""

from flask import Blueprint, request, jsonify
from services.auth import (
    register_user, 
    login_user, 
    get_user_profile, 
    update_user_preferences,
    token_required
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "full_name": "John Doe"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    result, status = register_user(
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name')
    )
    
    return jsonify(result), status


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    result, status = login_user(
        email=data['email'],
        password=data['password']
    )
    
    return jsonify(result), status


@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile():
    """
    Get user profile (requires authentication)
    
    Headers:
    Authorization: Bearer <token>
    """
    result, status = get_user_profile(request.user_id)
    return jsonify(result), status


@auth_bp.route('/preferences', methods=['PUT'])
@token_required
def preferences():
    """
    Update user preferences
    
    Headers:
    Authorization: Bearer <token>
    
    Request body:
    {
        "food_preference": "non-vegetarian",
        "budget_range": "50-200",
        "travel_style": "adventure",
        "interests": ["beach", "food", "culture"]
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Preferences data is required'}), 400
    
    result, status = update_user_preferences(request.user_id, data)
    return jsonify(result), status
