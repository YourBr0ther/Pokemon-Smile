from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import random
import os

load_dotenv()

app = Flask(__name__)

POKEAPI_BASE = "https://pokeapi.co/api/v2"
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/")
client = MongoClient(MONGO_URI)
db = client["pokemon_smile"]
profiles_collection = db["profiles"]

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
    random_pokemon = get_random_pokemon_sprite()
    return render_template('index.html', sprite_url=random_pokemon['sprite'], pokemon_name=random_pokemon['name'])

# -------------------
# NEW SINGLE-PAGE POKEDEX ROUTE
# -------------------
@app.route('/pokedex')
def pokedex():
    return render_template('pokedex.html')

# -------------------
# BRUSHING SCREEN ROUTE
# -------------------
@app.route('/brushing')
def brushing():
    return render_template('brushing.html')

# -------------------
# API ROUTES FOR MONGODB
# -------------------
@app.route('/api/save_profile', methods=['POST'])
def save_profile():
    data = request.json
    profiles_collection.replace_one({"name": data["name"]}, data, upsert=True)
    return jsonify({"status": "saved"})

@app.route('/api/load_profile/<name>')
def load_profile(name):
    profile = profiles_collection.find_one({"name": name}, {"_id": 0})
    return jsonify(profile or {})

@app.route('/api/save_pokemon/<profile_name>', methods=['POST'])
def save_pokemon(profile_name):
    data = request.json
    profiles_collection.update_one(
        {"name": profile_name},
        {"$push": {"caught_pokemon": data}},
        upsert=True
    )
    return jsonify({"status": "pokemon added"})

@app.route('/api/get_pokedex/<profile_name>')
def get_pokedex(profile_name):
    profile = profiles_collection.find_one({"name": profile_name}, {"_id": 0, "caught_pokemon": 1})
    return jsonify(profile.get("caught_pokemon", []) if profile else [])

@app.route('/api/get_profiles')
def get_profiles():
    profiles = list(profiles_collection.find({}, {"_id": 0}))
    return jsonify(profiles)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
