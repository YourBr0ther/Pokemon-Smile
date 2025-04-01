"""
Tests for the Pokemon routes.
"""
import json
import pytest
from unittest.mock import Mock
from flask import Flask, session
from app.routes.pokemon import init_pokemon_routes
from app.models.user import User

@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def mock_pokemon_api():
    """Create a mock Pokemon API client."""
    return Mock()

@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    return Mock()

@pytest.fixture
def client(app, mock_pokemon_api, mock_user_repository):
    """Create a test client with mocked dependencies."""
    pokemon_bp = init_pokemon_routes(mock_pokemon_api, mock_user_repository)
    app.register_blueprint(pokemon_bp)
    return app.test_client()

@pytest.fixture
def sample_user():
    """Create a sample user."""
    user = User('testuser', 'password123')
    user.caught_pokemon = [1, 2, 3]
    return user

@pytest.fixture
def sample_pokemon():
    """Create a sample Pokemon data."""
    return {
        'id': 1,
        'name': 'bulbasaur',
        'sprites': {
            'front_default': 'https://example.com/bulbasaur.png',
            'front_shiny': 'https://example.com/bulbasaur-shiny.png'
        },
        'types': ['grass', 'poison']
    }

def test_get_pokedex_authenticated(client, mock_user_repository, sample_user):
    """Test getting the Pokedex when authenticated."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = sample_user
    
    response = client.get('/pokedex')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['caught_pokemon'] == [1, 2, 3]

def test_get_pokedex_unauthenticated(client):
    """Test getting the Pokedex when not authenticated."""
    response = client.get('/pokedex')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Not authenticated' in data['message']

def test_get_pokedex_user_not_found(client, mock_user_repository):
    """Test getting the Pokedex with non-existent user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = None
    
    response = client.get('/pokedex')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'User not found' in data['message']

def test_get_pokemon_list(client, mock_pokemon_api, mock_pokemon_list_response):
    """Test getting a paginated list of Pokemon."""
    mock_pokemon_api.get_pokemon_list.return_value = mock_pokemon_list_response
    
    response = client.get('/pokemon?page=1&per_page=20')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['pokemon']) == 20
    assert data['total'] == 100
    assert data['page'] == 1
    assert data['per_page'] == 20

def test_get_pokemon_list_invalid_params(client):
    """Test getting a Pokemon list with invalid parameters."""
    response = client.get('/pokemon?page=invalid&per_page=invalid')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid parameters' in data['message']

def test_get_pokemon_details(client, mock_pokemon_api, sample_pokemon):
    """Test getting details of a specific Pokemon."""
    mock_pokemon_api.get_pokemon_details.return_value = sample_pokemon
    
    response = client.get('/pokemon/1')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['pokemon']['id'] == 1
    assert data['pokemon']['name'] == 'Bulbasaur'

def test_get_pokemon_details_not_found(client, mock_pokemon_api):
    """Test getting details of a non-existent Pokemon."""
    mock_pokemon_api.get_pokemon_details.return_value = None
    
    response = client.get('/pokemon/9999')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Pokemon not found' in data['message']

def test_catch_pokemon_success(client, mock_pokemon_api, mock_user_repository, sample_user, sample_pokemon):
    """Test successfully catching a Pokemon."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = sample_user
    mock_pokemon_api.get_pokemon_details.return_value = sample_pokemon
    mock_user_repository.update_user.return_value = True
    
    response = client.post('/pokemon/1/catch')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'Pokemon caught successfully'
    assert data['pokemon']['id'] == 1
    assert data['pokemon']['name'] == 'Bulbasaur'

def test_catch_pokemon_unauthenticated(client):
    """Test catching a Pokemon when not authenticated."""
    response = client.post('/pokemon/1/catch')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Not authenticated' in data['message']

def test_catch_pokemon_user_not_found(client, mock_user_repository):
    """Test catching a Pokemon with non-existent user."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = None
    
    response = client.post('/pokemon/1/catch')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'User not found' in data['message']

def test_catch_pokemon_not_found(client, mock_pokemon_api, mock_user_repository, sample_user):
    """Test catching a non-existent Pokemon."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = sample_user
    mock_pokemon_api.get_pokemon_details.return_value = None
    
    response = client.post('/pokemon/9999/catch')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Pokemon not found' in data['message']

def test_catch_pokemon_update_failure(client, mock_pokemon_api, mock_user_repository, sample_user, sample_pokemon):
    """Test catching a Pokemon with database update failure."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = sample_user
    mock_pokemon_api.get_pokemon_details.return_value = sample_pokemon
    mock_user_repository.update_user.return_value = False
    
    response = client.post('/pokemon/1/catch')
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Failed to update user data' in data['message']

@pytest.fixture
def mock_pokemon_list_response():
    """Create a mock Pokemon list response."""
    return {
        'count': 1118,
        'results': [
            {'name': 'bulbasaur', 'url': 'https://pokeapi.co/api/v2/pokemon/1/'},
            {'name': 'ivysaur', 'url': 'https://pokeapi.co/api/v2/pokemon/2/'}
        ]
    } 