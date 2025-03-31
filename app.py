from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import requests
import random
import os
import secrets
from bson.objectid import ObjectId
import sys
from datetime import datetime, timedelta
import json
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Add CORS support to allow cross-origin requests
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Make sessions last longer
app.config['SERVER_NAME'] = os.environ.get("BASE_URL", "").replace("http://", "").replace("https://", "")

# Global variables for service status
mongodb_status = {
    'status': 'unknown',
    'last_checked': None,
    'error': None
}

def check_mongodb_connection():
    """Check MongoDB connection and update status."""
    global mongodb_status
    try:
        client.admin.command('ping')
        mongodb_status = {
            'status': 'healthy',
            'last_checked': datetime.now(),
            'error': None
        }
        return True
    except Exception as e:
        mongodb_status = {
            'status': 'error',
            'last_checked': datetime.now(),
            'error': str(e)
        }
        return False

@app.route('/api/health')
def health_check():
    """Health check endpoint that verifies all services are running."""
    # Check MongoDB connection
    mongodb_healthy = check_mongodb_connection()
    
    # Get Pokemon API status
    try:
        pokemon_api = requests.get(f"{POKEAPI_BASE}/pokemon/1", timeout=5)
        pokemon_api_healthy = pokemon_api.status_code == 200
    except:
        pokemon_api_healthy = False
    
    status = {
        'status': 'healthy' if mongodb_healthy and pokemon_api_healthy else 'degraded',
        'services': {
            'mongodb': {
                'status': mongodb_status['status'],
                'last_checked': mongodb_status['last_checked'].isoformat() if mongodb_status['last_checked'] else None,
                'error': mongodb_status['error']
            },
            'pokemon_api': {
                'status': 'healthy' if pokemon_api_healthy else 'error'
            }
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status), 200 if status['status'] == 'healthy' else 503

@app.before_request
def check_service_status():
    """Check service status before each request."""
    # Skip health check endpoint to avoid infinite loop
    if request.endpoint == 'health_check':
        return
        
    # Skip static files
    if request.endpoint == 'static':
        return
        
    # Check MongoDB connection
    if not check_mongodb_connection():
        # If it's an API request, return JSON error
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Service Unavailable',
                'message': 'Database connection error. Please try again later.',
                'status': mongodb_status
            }), 503
        
        # For regular requests, show error page
        return render_template('error.html',
            error_title='Service Unavailable',
            error_message='We are experiencing technical difficulties. Please try again later.',
            status=mongodb_status
        ), 503

# Make sessions permanent by default
@app.before_request
def make_session_permanent():
    session.permanent = True

POKEAPI_BASE = "https://pokeapi.co/api/v2"
# Use service name 'mongo' for Docker Compose, fallback to localhost for local dev
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/")

# Initialize MongoDB client with longer timeout for Docker environment
try:
    print(f"Attempting to connect to MongoDB at {MONGO_URI}")
    client = MongoClient(MONGO_URI, 
                        serverSelectionTimeoutMS=20000,  # 20 second timeout
                        connectTimeoutMS=20000,
                        socketTimeoutMS=20000,
                        retryWrites=True)
    # Force a connection to verify it works
    client.admin.command('ping')
    print("MongoDB connection successful!")
    db = client["pokemon_smile"]
    profiles_collection = db["profiles"]
    
    # Initialize MongoDB status
    mongodb_status = {
        'status': 'healthy',
        'last_checked': datetime.now(),
        'error': None
    }
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"ERROR: Could not connect to MongoDB: {e}")
    print("Please make sure MongoDB is running and the connection string is correct.")
    print("If using Docker Compose, ensure the mongo service is up with:")
    print("  docker-compose ps")
    print("  docker-compose logs mongo")
    
    # Update MongoDB status
    mongodb_status = {
        'status': 'error',
        'last_checked': datetime.now(),
        'error': str(e)
    }
    
    # Don't exit, let the app run in degraded mode
    client = None
    db = None
    profiles_collection = None

# Wrap MongoDB operations in try/except
def safe_db_operation(operation):
    """Safely execute a MongoDB operation with proper error handling."""
    try:
        if client is None:
            raise ServerSelectionTimeoutError("MongoDB is not available")
        return operation()
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        # Update MongoDB status
        global mongodb_status
        mongodb_status = {
            'status': 'error',
            'last_checked': datetime.now(),
            'error': str(e)
        }
        # Re-raise the exception to be caught by the request handler
        raise

# -------------------
# HOME PAGE
# -------------------
def get_random_pokemon_sprite():
    total_pokemon = 898
    random_id = random.randint(1, total_pokemon)
    url = f"{POKEAPI_BASE}/pokemon/{random_id}"
    data = requests.get(url).json()
    name = data['name'].capitalize()
    sprite_url = data['sprites']['front_default'] or ''
    return {'name': name, 'sprite': sprite_url}

@app.route('/')
def main_menu():
    # Check if user is logged in
    if 'user_id' in session:
        # Get the user's profile
        user_id = session['user_id']
        try:
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
                
            def get_profile():
                return profiles_collection.find_one({"_id": user_id})
            
            profile = safe_db_operation(get_profile)
            
            if profile and 'buddyPokemon' in profile:
                # Use the buddy Pokémon from the profile
                buddy = profile['buddyPokemon']
                print(f"User logged in: {profile.get('name', 'User')} with buddy: {buddy.get('name', 'Unknown')}")
                return render_template('index.html', 
                                    sprite_url=buddy.get('sprite', ''),
                                    pokemon_name=buddy.get('name', 'Buddy'),
                                    logged_in=True,
                                    username=profile.get('name', 'User'))
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            # Show error page for MongoDB connection issues
            return render_template('error.html',
                error_title='Service Unavailable',
                error_message='We are experiencing technical difficulties. Please try again later.',
                status=mongodb_status
            ), 503
    
    # Not logged in or no profile found - show random Pokémon
    print("No user logged in or no buddy - showing random Pokémon")
    random_pokemon = get_random_pokemon_sprite()
    return render_template('index.html', 
                        sprite_url=random_pokemon['sprite'], 
                        pokemon_name=random_pokemon['name'],
                        logged_in=False)

# -------------------
# AUTH ROUTES
# -------------------
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session data
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/logout')  # Keep the GET route for direct browser navigation
def logout_redirect():
    session.clear()  # Clear all session data
    return redirect(url_for('main_menu'))

# -------------------
# NEW SINGLE-PAGE POKEDEX ROUTE
# -------------------
@app.route('/pokedex')
def pokedex():
    # Check if user is logged in
    if 'user_id' not in session:
        # Return to main menu - the profile selection popup will appear automatically
        return redirect(url_for('main_menu'))
    
    return render_template('pokedex.html')

# -------------------
# BRUSHING SCREEN ROUTE
# -------------------
@app.route('/brushing')
def brushing():
    # Check if user is logged in
    if 'user_id' not in session:
        # Return to main menu - the profile selection popup will appear automatically
        return redirect(url_for('main_menu'))
    
    return render_template('brushing.html')

# -------------------
# API ROUTES FOR MONGODB
# -------------------
@app.route('/api/save_profile', methods=['POST'])
def save_profile():
    profile_data = request.json
    
    # Log the received data for debugging
    print(f"Received profile data: {profile_data}")
    
    # Check if this is an update to an existing profile
    if '_id' in profile_data:
        try:
            # Convert string ID to ObjectId if needed
            if not isinstance(profile_data['_id'], ObjectId):
                profile_id = ObjectId(profile_data['_id'])
            else:
                profile_id = profile_data['_id']
            
            # Get the existing profile
            existing_profile = profiles_collection.find_one({"_id": profile_id})
            if not existing_profile:
                return jsonify({"status": "error", "message": "Profile not found"}), 404
            
            # Handle password change if requested
            if 'currentPassword' in profile_data and 'newPassword' in profile_data:
                if existing_profile['password'] != profile_data['currentPassword']:
                    return jsonify({"status": "error", "message": "Current password is incorrect"}), 400
                profile_data['password'] = profile_data['newPassword']
                # Remove the temporary password fields
                del profile_data['currentPassword']
                del profile_data['newPassword']
            
            # Remove _id from the update data
            update_data = {k: v for k, v in profile_data.items() if k != '_id'}
            
            # Ensure brushingTime is stored as an integer
            if 'brushingTime' in update_data:
                update_data['brushingTime'] = int(update_data['brushingTime'])
                
            # Update the profile
            result = profiles_collection.update_one(
                {"_id": profile_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"Updated profile with ID: {profile_id}")
                # Update session with the latest profile data
                if 'user_id' in session and str(session['user_id']) == str(profile_id):
                    print("Updating session with new profile data")
                
                return jsonify({"status": "success", "message": "Profile updated"})
            else:
                print(f"No changes made to profile with ID: {profile_id}")
                return jsonify({"status": "success", "message": "No changes needed"})
                
        except Exception as e:
            print(f"Error updating profile: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # This is a new profile
    else:
        try:
            # Ensure brushingTime is stored as an integer
            if 'brushingTime' in profile_data:
                profile_data['brushingTime'] = int(profile_data['brushingTime'])
                
            # Insert the new profile
            result = profiles_collection.insert_one(profile_data)
            profile_data['_id'] = str(result.inserted_id)
            
            # Set the user_id in session for immediate login
            session['user_id'] = str(result.inserted_id)
            
            print(f"Created new profile with ID: {result.inserted_id}")
            return jsonify({"status": "success", "message": "Profile created", "profile": profile_data})
            
        except Exception as e:
            print(f"Error creating profile: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/load_profile/<name>')
def load_profile(name):
    profile = profiles_collection.find_one({"name": name})
    if profile:
        # Convert ObjectId to string for JSON serialization
        profile['_id'] = str(profile['_id'])
        # Store user ID in session
        session['user_id'] = profile['_id']
        return jsonify(profile)
    return jsonify({})

@app.route('/api/save_pokemon/<profile_name>', methods=['POST'])
def save_pokemon(profile_name):
    data = request.json
    
    # Add more detailed logging
    print(f"POST /api/save_pokemon/{profile_name}")
    print(f"Request data: {data}")
    print(f"Session data: {session}")
    
    # Only save if user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        try:
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
        except Exception as e:
            print(f"Error converting user_id to ObjectId: {e}")
            return jsonify({"status": "error", "message": "Invalid user ID format"}), 400
            
        # Log the save attempt for debugging
        print(f"Attempting to save Pokémon for user_id: {user_id}")
        print(f"Pokémon data: {data}")
        
        try:
            # First check if the user profile exists
            profile = profiles_collection.find_one({"_id": user_id})
            if not profile:
                print(f"Profile not found for user_id: {user_id}")
                return jsonify({"status": "error", "message": "User profile not found"}), 404
            
            # Now update with the new Pokemon
            result = profiles_collection.update_one(
                {"_id": user_id},
                {"$push": {"caught_pokemon": data}}
            )
            
            # Check if the update was successful
            if result.modified_count > 0:
                print(f"Successfully saved Pokémon to database")
                return jsonify({"status": "success", "message": "Pokémon saved successfully"})
            else:
                print(f"No changes made to database. This might be expected behavior if the document didn't change.")
                return jsonify({"status": "success", "message": "No changes made"}), 200
        except Exception as e:
            print(f"Database error when saving Pokémon: {e}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    else:
        print("User not logged in when trying to save Pokémon")
        return jsonify({"status": "error", "message": "Not logged in"}), 401

@app.route('/api/get_pokedex')
def get_pokedex():
    # Only return Pokémon for logged in user
    if 'user_id' not in session:
        print("User not logged in when trying to access Pokédex")
        return jsonify({"error": "Not logged in"}), 401
    
    # Convert string ID back to ObjectId for MongoDB query
    user_id = session['user_id']
    try:
        # If it's already an ObjectId, this will fail
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
    except Exception as e:
        print(f"Error converting user_id to ObjectId: {e}")
        # If conversion fails, use as is (it might be a string)
        pass
        
    profile = profiles_collection.find_one({"_id": user_id})
    if profile:
        caught_pokemon = profile.get("caught_pokemon", [])
        print(f"Found {len(caught_pokemon)} Pokémon for user {profile.get('name', 'Unknown')}")
        return jsonify(caught_pokemon)
    else:
        print(f"No profile found for user_id: {user_id}")
        return jsonify([])

@app.route('/api/get_profiles')
def get_profiles():
    try:
        print("\n=== GET /api/get_profiles ===")
        print("Fetching all profiles from MongoDB...")
        
        # Get all profiles from the database with no filters
        cursor = profiles_collection.find({})
        profiles = list(cursor)
        
        print(f"Found {len(profiles)} profiles in database")
        print("Profile IDs found:", [str(p['_id']) for p in profiles])
        print("Profile names found:", [p.get('name', 'MISSING') for p in profiles])
        
        # Convert ObjectId to string for JSON serialization
        serialized_profiles = []
        for profile in profiles:
            try:
                profile_copy = profile.copy()
                profile_copy['_id'] = str(profile['_id'])
                
                # Log profile details for debugging
                print(f"\nProcessing profile:")
                print(f"ID: {profile_copy['_id']}")
                print(f"Name: {profile_copy.get('name', 'MISSING')}")
                print(f"Has password: {bool(profile_copy.get('password'))}")
                print(f"Buddy Pokemon: {profile_copy.get('buddyPokemon', 'MISSING')}")
                
                # Add profile to list
                serialized_profiles.append(profile_copy)
                
            except Exception as e:
                print(f"Error processing profile {profile.get('_id')}: {e}")
                continue
        
        print(f"\nReturning {len(serialized_profiles)} serialized profiles")
        return jsonify(serialized_profiles)
    except Exception as e:
        print(f"Error getting profiles: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/active_profile')
def get_active_profile():
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
                
            profile = profiles_collection.find_one({"_id": user_id})
            if profile:
                # Convert ObjectId to string for JSON serialization
                profile['_id'] = str(profile['_id'])
                
                # Ensure brushingTime is present and is an integer
                if 'brushingTime' not in profile:
                    profile['brushingTime'] = 60
                else:
                    profile['brushingTime'] = int(profile['brushingTime'])
                    
                print(f"Active profile: {profile.get('name')} with brushing time: {profile.get('brushingTime')}")
                return jsonify({"profile": profile})
        except Exception as e:
            print(f"Error retrieving active profile: {e}")
    
    return jsonify({"profile": None})

@app.route('/debug/session')
def debug_session():
    print("Session debug requested")
    print(f"Current session: {dict(session)}")
    
    if 'user_id' in session:
        user_id = session['user_id']
        print(f"User ID in session: {user_id}")
        
        try:
            if not isinstance(user_id, ObjectId):
                user_id = ObjectId(user_id)
                print(f"Converted user_id to ObjectId: {user_id}")
        except Exception as e:
            print(f"Error converting user_id to ObjectId: {e}")
            pass
            
        profile = profiles_collection.find_one({"_id": user_id})
        if profile:
            print(f"Found profile: {profile.get('name')}")
            return jsonify({
                "status": "logged_in",
                "user_id": session['user_id'],
                "username": profile.get('name', 'Unknown'),
                "buddy": profile.get('buddyPokemon', {}),
                "session_data": dict(session)
            })
        else:
            print(f"No profile found for user_id: {user_id}")
    else:
        print("No user_id in session")
    
    return jsonify({
        "status": "not_logged_in",
        "session_data": dict(session)
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    profile_id = data.get('profile_id')
    
    # Debug logging
    print(f"Login attempt for user: {name} with profile_id: {profile_id}")
    
    if not name or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    
    # Try MongoDB first
    try:
        # Find user in database using profile_id if provided
        query = {"name": name, "password": password}
        if profile_id:
            try:
                query["_id"] = ObjectId(profile_id)
            except Exception as e:
                print(f"Error converting profile_id to ObjectId: {e}")
                return jsonify({"success": False, "message": "Invalid profile ID"}), 400
        
        user = profiles_collection.find_one(query)
        
        if user:
            # Convert ObjectId to string before storing in session
            session['user_id'] = str(user['_id'])
            return jsonify({"success": True, "message": "Login successful"})
    except Exception as e:
        print(f"MongoDB login error: {e}")
    
    # No matching profile found
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/all_pokemon')
def all_pokemon():
    try:
        # Get all Pokémon from the first 3 generations (1-386)
        pokemon_list = []
        
        # First, check if we have a cached version
        cache_file = 'pokemon_cache.json'
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    pokemon_list = json.load(f)
                    print(f"Loaded {len(pokemon_list)} Pokémon from cache")
                    return jsonify(pokemon_list)
            except Exception as e:
                print(f"Error loading from cache: {e}")
                # Continue to fetch from API if cache fails
        
        # Fetch from API if no cache
        for pokemon_id in range(1, 387):  # First 3 generations
            try:
                url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Get species data for description and generation
                    species_url = data['species']['url']
                    species_response = requests.get(species_url)
                    species_data = species_response.json()
                    
                    # Find English description
                    description = ""
                    for entry in species_data['flavor_text_entries']:
                        if entry['language']['name'] == 'en':
                            description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                            break
                    
                    # Determine generation
                    generation = species_data['generation']['url'].split('/')[-2].replace('generation-', '')
                    
                    # Get types
                    types = [t['type']['name'].capitalize() for t in data['types']]
                    
                    pokemon = {
                        'id': pokemon_id,
                        'name': data['name'],
                        'sprite': data['sprites']['front_default'],
                        'types': types,
                        'generation': generation,
                        'description': description,
                        'cry': f"/static/cries/{pokemon_id}.mp3" if os.path.exists(f"static/cries/{pokemon_id}.mp3") else None
                    }
                    
                    pokemon_list.append(pokemon)
                    
                    # Log progress every 10 Pokémon
                    if pokemon_id % 10 == 0:
                        print(f"Fetched {pokemon_id} Pokémon...")
                
            except Exception as e:
                print(f"Error fetching Pokémon {pokemon_id}: {e}")
                continue
        
        # Cache the results
        try:
            with open(cache_file, 'w') as f:
                json.dump(pokemon_list, f)
                print(f"Cached {len(pokemon_list)} Pokémon")
        except Exception as e:
            print(f"Error caching Pokémon: {e}")
        
        return jsonify(pokemon_list)
    
    except Exception as e:
        print(f"Error in all_pokemon route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search_pokemon')
def search_pokemon():
    query = request.args.get('name', '').lower()
    
    if not query:
        return jsonify([])
    
    try:
        # First try to get exact match from PokeAPI
        url = f"{POKEAPI_BASE}/pokemon/{query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            pokemon = {
                'id': data['id'],
                'name': data['name'],
                'sprite': data['sprites']['front_default'],
                'types': [t['type']['name'].capitalize() for t in data['types']]
            }
            return jsonify([pokemon])
        
        # If no exact match, search through all Pokémon
        # This would be better with a database, but for simplicity we'll use the API
        results = []
        for i in range(1, 152):  # Limit to first generation for performance
            try:
                url = f"{POKEAPI_BASE}/pokemon/{i}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if query in data['name'].lower():
                        pokemon = {
                            'id': data['id'],
                            'name': data['name'],
                            'sprite': data['sprites']['front_default'],
                            'types': [t['type']['name'].capitalize() for t in data['types']]
                        }
                        results.append(pokemon)
                        
                        # Limit to 10 results for performance
                        if len(results) >= 10:
                            break
            except:
                continue
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error in search_pokemon: {e}")
        return jsonify([])

@app.route('/api/user_pokedex')
def user_pokedex():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        user_id = session['user_id']
        if not isinstance(user_id, ObjectId):
            try:
                user_id = ObjectId(user_id)
            except:
                pass
        
        # Get user profile from MongoDB
        profile = profiles_collection.find_one({"_id": user_id})
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        
        # Debug: Print the entire profile
        print(f"User profile: {profile}")
        
        # Check if caught_pokemon exists and is a list
        if 'caught_pokemon' in profile and isinstance(profile['caught_pokemon'], list):
            caught_pokemon = profile['caught_pokemon']
            
            # Print raw caught_pokemon for debugging
            print(f"Raw caught_pokemon: {caught_pokemon}")
            
            # Normalize the data format - extract IDs from various formats
            normalized_pokemon = []
            for pokemon in caught_pokemon:
                if isinstance(pokemon, int):
                    normalized_pokemon.append(pokemon)
                elif isinstance(pokemon, str) and pokemon.isdigit():
                    normalized_pokemon.append(int(pokemon))
                elif isinstance(pokemon, dict):
                    # Try to get ID from id or pokemon_id fields
                    if 'id' in pokemon and isinstance(pokemon['id'], (int, str)):
                        pokemon_id = int(pokemon['id']) if isinstance(pokemon['id'], str) else pokemon['id']
                        normalized_pokemon.append(pokemon_id)
                    elif 'pokemon_id' in pokemon and isinstance(pokemon['pokemon_id'], (int, str)):
                        pokemon_id = int(pokemon['pokemon_id']) if isinstance(pokemon['pokemon_id'], str) else pokemon['pokemon_id']
                        normalized_pokemon.append(pokemon_id)
                    # Try to extract ID from sprite URL
                    elif 'sprite' in pokemon and isinstance(pokemon['sprite'], str):
                        # Extract ID from URL like "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
                        try:
                            url_parts = pokemon['sprite'].split('/')
                            filename = url_parts[-1]  # Get "25.png"
                            pokemon_id = int(filename.split('.')[0])  # Get "25"
                            normalized_pokemon.append(pokemon_id)
                        except (ValueError, IndexError):
                            print(f"Could not extract ID from sprite URL: {pokemon['sprite']}")
            
            print(f"Normalized Pokémon IDs: {normalized_pokemon}")
            return jsonify(normalized_pokemon)
        else:
            # If no caught_pokemon or not a list, return empty list
            print(f"No caught_pokemon found for user {profile.get('name', 'Unknown')}")
            return jsonify([])
    
    except Exception as e:
        print(f"Error in user_pokedex: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pokemon/<int:pokemon_id>')
def get_pokemon(pokemon_id):
    try:
        # First check if we have it in cache
        cache_file = 'pokemon_cache.json'
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    pokemon_list = json.load(f)
                    for pokemon in pokemon_list:
                        if pokemon['id'] == pokemon_id:
                            # Update the cry URL to use PokeAPI
                            pokemon['cry'] = f"https://play.pokemonshowdown.com/audio/cries/{pokemon['name'].lower()}.mp3"
                            return jsonify(pokemon)
            except Exception as e:
                print(f"Error loading from cache: {e}")
        
        # If not in cache, fetch from API
        url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": f"Pokémon #{pokemon_id} not found"}), 404
            
        data = response.json()
        
        # Get species data for description
        species_url = data['species']['url']
        species_response = requests.get(species_url)
        species_data = species_response.json()
        
        # Find English description
        description = ""
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                description = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                break
        
        # Determine generation
        generation = species_data['generation']['url'].split('/')[-2].replace('generation-', '')
        
        # Get types
        types = [t['type']['name'].capitalize() for t in data['types']]
        
        # Get the Pokémon name for the cry URL
        pokemon_name = data['name'].lower()
        
        pokemon = {
            'id': pokemon_id,
            'name': data['name'],
            'sprite': data['sprites']['front_default'],
            'types': types,
            'generation': generation,
            'description': description,
            'cry': f"https://play.pokemonshowdown.com/audio/cries/{pokemon_name}.mp3"
        }
        
        return jsonify(pokemon)
        
    except Exception as e:
        print(f"Error fetching Pokémon #{pokemon_id}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
