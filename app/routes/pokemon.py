"""
Pokemon routes module.
Handles Pokemon-related endpoints.
"""
from flask import Blueprint, jsonify, session, request
from app.models.user import UserRepository
from app.services.pokemon_api.client import PokemonAPIClient
from functools import wraps

pokemon_bp = Blueprint('pokemon', __name__)

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Not authenticated'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def init_pokemon_routes(pokemon_api: PokemonAPIClient, user_repository: UserRepository):
    """Initialize Pokemon routes with dependencies."""
    
    @pokemon_bp.route('/pokedex', methods=['GET'])
    @login_required
    def get_pokedex():
        """Get user's Pokedex information."""
        username = session['username']
        user = user_repository.find_by_username(username)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'caught_pokemon': user.get_caught_pokemon()
        })

    @pokemon_bp.route('/pokemon', methods=['GET'])
    def get_pokemon_list():
        """Get paginated list of Pokemon."""
        try:
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 20)), 100)  # Cap at 100
            offset = (page - 1) * per_page
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid parameters'
            }), 400

        pokemon_list = pokemon_api.get_pokemon_list(offset, per_page)
        total_count = pokemon_api.get_pokemon_count()

        return jsonify({
            'status': 'success',
            'pokemon': pokemon_list,
            'total': total_count,
            'page': page,
            'per_page': per_page
        })

    @pokemon_bp.route('/pokemon/<int:pokemon_id>', methods=['GET'])
    def get_pokemon(pokemon_id):
        """Get details for a specific Pokemon."""
        pokemon_data = pokemon_api.get_pokemon(pokemon_id)
        
        if not pokemon_data:
            return jsonify({
                'status': 'error',
                'message': 'Pokemon not found'
            }), 404

        return jsonify({
            'status': 'success',
            'pokemon': pokemon_data
        })

    @pokemon_bp.route('/pokemon/<int:pokemon_id>/catch', methods=['POST'])
    @login_required
    def catch_pokemon(pokemon_id):
        """Mark a Pokemon as caught for the user."""
        username = session['username']
        user = user_repository.find_by_username(username)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        # Verify Pokemon exists
        pokemon_data = pokemon_api.get_pokemon(pokemon_id)
        if not pokemon_data:
            return jsonify({
                'status': 'error',
                'message': 'Pokemon not found'
            }), 404

        # Add to caught list and update user
        user.catch_pokemon(pokemon_id)
        if user_repository.update_user(user):
            return jsonify({
                'status': 'success',
                'message': 'Pokemon caught successfully',
                'pokemon': pokemon_data
            })
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to update user data'
        }), 500

    return pokemon_bp 