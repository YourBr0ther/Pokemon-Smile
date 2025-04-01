"""
Authentication routes module.
Handles user authentication endpoints.
"""
from flask import Blueprint, request, session, jsonify
from app.models.user import User, UserRepository

def init_auth_routes(user_repository: UserRepository):
    """Initialize authentication routes with dependencies."""
    auth_bp = Blueprint('auth', __name__)
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        """Handle user login."""
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing username or password'
            }), 400

        username = data['username']
        password = data['password']
        
        user = user_repository.find_by_username(username)
        
        if not user or not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401

        # Set session data
        session['username'] = username
        session.permanent = True
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': user.to_dict()
        })

    @auth_bp.route('/register', methods=['POST'])
    def register():
        """Handle user registration."""
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing username or password'
            }), 400

        username = data['username']
        password = data['password']
        
        # Check if username already exists
        if user_repository.find_by_username(username):
            return jsonify({
                'status': 'error',
                'message': 'Username already exists'
            }), 409

        # Create new user
        user = User(username=username, password=password)
        if user_repository.create_user(user):
            return jsonify({
                'status': 'success',
                'message': 'Registration successful',
                'user': user.to_dict()
            }), 201
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to create user'
        }), 500

    @auth_bp.route('/logout', methods=['POST'])
    def logout():
        """Handle user logout."""
        session.pop('username', None)
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        })

    @auth_bp.route('/check-auth', methods=['GET'])
    def check_auth():
        """Check if user is authenticated."""
        username = session.get('username')
        if username:
            user = user_repository.find_by_username(username)
            if user:
                return jsonify({
                    'status': 'success',
                    'authenticated': True,
                    'user': user.to_dict()
                })
        
        return jsonify({
            'status': 'success',
            'authenticated': False
        })

    @auth_bp.route('/get_profiles', methods=['GET'])
    def get_profiles():
        """Get all user profiles."""
        try:
            users = user_repository.get_all_users()
            return jsonify([user.to_dict() for user in users])
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    return auth_bp 