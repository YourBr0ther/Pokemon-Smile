import pytest
import sys
from app.app import app, client, mongodb_status, check_mongodb_connection, attempt_mongodb_reconnection, MongoClient
import json
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure
import requests

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = None  # Prevent URL generation issues in tests
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_mongo():
    """Mock MongoDB with better control over connection behavior"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.admin.command.return_value = True  # Default to successful connection
    mock_client.pokemon_smile = mock_db  # Set up database access
    
    with patch('app.app.get_mongodb_client', return_value=mock_client), \
         patch('app.app.client', mock_client), \
         patch('app.app.profiles_collection', mock_db.profiles):  # Mock the profiles collection
        yield mock_client

def test_health_check_healthy(test_client, mock_mongo, monkeypatch):
    """Test health check endpoint when MongoDB is healthy"""
    # Mock environment variable and PokeAPI request
    monkeypatch.setenv('POKEAPI_BASE', 'https://pokeapi.co/api/v2')
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Ensure MongoDB is seen as healthy
        mongodb_status['status'] = 'healthy'
        mock_mongo.admin.command.return_value = True
        
        response = test_client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

def test_health_check_error(test_client, mock_mongo, monkeypatch):
    """Test health check endpoint when MongoDB has an error"""
    # Mock environment variable and PokeAPI request
    monkeypatch.setenv('POKEAPI_BASE', 'https://pokeapi.co/api/v2')
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        
        # Simulate MongoDB error
        mongodb_status['status'] = 'error'
        mock_mongo.admin.command.side_effect = ConnectionFailure("Connection failed")
        
        response = test_client.get('/api/health')
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['status'] == 'degraded'
        assert data['services']['mongodb']['status'] == 'error'
        assert data['services']['pokemon_api']['status'] == 'error'

def test_index_route(test_client, mock_mongo):
    """Test the main index route"""
    # Ensure MongoDB is healthy for this test
    mongodb_status['status'] = 'healthy'
    mock_mongo.admin.command.return_value = True
    
    response = test_client.get('/')
    assert response.status_code == 200

def test_pokedex_route_authenticated(test_client, mock_mongo):
    """Test pokedex route when authenticated"""
    # Ensure MongoDB is healthy for this test
    mongodb_status['status'] = 'healthy'
    mock_mongo.admin.command.return_value = True
    
    with test_client.session_transaction() as session:
        session['logged_in'] = True
        session['user_id'] = '123'
    response = test_client.get('/pokedex')
    assert response.status_code == 200

def test_pokedex_route_unauthenticated(test_client, mock_mongo):
    """Test pokedex route redirects when not authenticated"""
    # Ensure MongoDB is healthy for this test
    mongodb_status['status'] = 'healthy'
    mock_mongo.admin.command.return_value = True
    
    response = test_client.get('/pokedex')
    assert response.status_code == 302  # Redirect

def test_login_valid(test_client, mock_mongo):
    """Test valid login attempt"""
    # Ensure MongoDB is healthy for this test
    mongodb_status['status'] = 'healthy'
    mock_mongo.admin.command.return_value = True
    
    # Setup mock user in database
    mock_user = {
        '_id': '123',
        'name': 'Test User',
        'password': 'test_password',
        'buddy_pokemon': 'pikachu'
    }
    mock_mongo.pokemon_smile.profiles.find_one.return_value = mock_user
    
    response = test_client.post('/api/login', json={
        'name': 'Test User',
        'password': 'test_password'
    })
    assert response.status_code == 200

def test_login_invalid(test_client, mock_mongo):
    """Test invalid login attempt"""
    # Ensure MongoDB is healthy for this test
    mongodb_status['status'] = 'healthy'
    mock_mongo.admin.command.return_value = True
    
    # No user found in database
    mock_mongo.pokemon_smile.profiles.find_one.return_value = None
    
    response = test_client.post('/api/login', json={
        'name': 'Wrong User',
        'password': 'wrong_password'
    })
    assert response.status_code == 401

def test_mongodb_connection_check(mock_mongo):
    """Test MongoDB connection check function"""
    # Test successful connection
    mock_mongo.admin.command.return_value = True
    assert check_mongodb_connection() == True
    assert mongodb_status['status'] == 'healthy'
    
    # Test failed connection
    mock_mongo.admin.command.side_effect = ConnectionFailure("Connection failed")
    assert check_mongodb_connection() == False
    assert mongodb_status['status'] == 'error'

def test_attempt_mongodb_reconnection(mock_mongo, monkeypatch):
    """Test MongoDB reconnection attempt function"""
    # Mock environment variable and MongoClient
    monkeypatch.setenv('MONGODB_URI', 'mongodb://mongo:27017/')
    
    # Create a mock client for reconnection
    mock_new_client = MagicMock()
    mock_new_client.admin.command.return_value = True
    mock_new_client.pokemon_smile = MagicMock()
    
    with patch('app.app.MongoClient', return_value=mock_new_client):
        # Setup initial error state
        mongodb_status.update({
            'status': 'error',
            'reconnect_attempts': 1,
            'last_reconnect_attempt': None
        })
        
        # Test successful reconnection
        attempt_mongodb_reconnection()
        assert mongodb_status['status'] == 'healthy'
        assert mongodb_status['reconnect_attempts'] == 0
        
        # Test failed reconnection
        mock_new_client.admin.command.side_effect = ConnectionFailure("Connection failed")
        attempt_mongodb_reconnection()
        assert mongodb_status['status'] == 'error'
        assert mongodb_status['reconnect_attempts'] > 0 