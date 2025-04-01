"""
Tests for the authentication routes.
"""
import json
import pytest
from flask import session
from unittest.mock import Mock, MagicMock
from app.routes.auth import init_auth_routes
from app.models.user import User, UserRepository

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    return MagicMock()

@pytest.fixture
def client(app, mock_user_repository):
    """Create a test client with mocked dependencies."""
    auth_bp = init_auth_routes(mock_user_repository)
    app.register_blueprint(auth_bp)
    return app.test_client()

@pytest.fixture
def sample_user():
    """Create a sample user instance."""
    return User('testuser', 'password123')

def test_login_success(client, mock_user_repository, sample_user):
    """Test successful login."""
    mock_user_repository.find_by_username.return_value = sample_user
    
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'Login successful'
    assert data['user']['username'] == 'testuser'
    assert 'password_hash' not in data['user']

def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post('/login', json={})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Missing username or password' in data['message']

def test_login_invalid_credentials(client, mock_user_repository, sample_user):
    """Test login with invalid credentials."""
    mock_user_repository.find_by_username.return_value = sample_user
    
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid username or password' in data['message']

def test_login_nonexistent_user(client, mock_user_repository):
    """Test login with non-existent user."""
    mock_user_repository.find_by_username.return_value = None
    
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'password123'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid username or password' in data['message']

def test_register_success(client, mock_user_repository):
    """Test successful registration."""
    mock_user_repository.find_by_username.return_value = None
    mock_user_repository.create_user.return_value = True
    
    response = client.post('/register', json={
        'username': 'newuser',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'Registration successful'
    assert data['user']['username'] == 'newuser'
    assert data['user']['caught_pokemon'] == []

def test_register_missing_credentials(client):
    """Test registration with missing credentials."""
    response = client.post('/register', json={})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Missing username or password' in data['message']

def test_register_existing_user(client, mock_user_repository, sample_user):
    """Test registration with existing username."""
    mock_user_repository.find_by_username.return_value = sample_user
    
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Username already exists' in data['message']

def test_register_creation_failure(client, mock_user_repository):
    """Test registration with database creation failure."""
    mock_user_repository.find_by_username.return_value = None
    mock_user_repository.create_user.return_value = False
    
    response = client.post('/register', json={
        'username': 'newuser',
        'password': 'password123'
    })
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Failed to create user' in data['message']

def test_logout(client):
    """Test logout."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.post('/logout')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'Logout successful'
    
    with client.session_transaction() as sess:
        assert 'username' not in sess

def test_check_auth_authenticated(client, mock_user_repository, sample_user):
    """Test authentication check when user is logged in."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    mock_user_repository.find_by_username.return_value = sample_user
    
    response = client.get('/check-auth')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['authenticated'] is True
    assert data['user']['username'] == 'testuser'
    assert data['user']['caught_pokemon'] == []

def test_check_auth_not_authenticated(client):
    """Test authentication check when user is not logged in."""
    response = client.get('/check-auth')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['authenticated'] is False

def test_get_profiles_success(client, mock_user_repository, sample_user):
    """Test getting all user profiles successfully."""
    mock_user_repository.get_all_users.return_value = [sample_user]
    
    response = client.get('/get_profiles')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['username'] == 'testuser'
    assert 'password_hash' not in data[0]
    mock_user_repository.get_all_users.assert_called_once()

def test_get_profiles_empty(client, mock_user_repository):
    """Test getting profiles when no users exist."""
    mock_user_repository.get_all_users.return_value = []
    
    response = client.get('/get_profiles')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0
    mock_user_repository.get_all_users.assert_called_once()

def test_get_profiles_error(client, mock_user_repository):
    """Test getting profiles when an error occurs."""
    mock_user_repository.get_all_users.side_effect = Exception("Database error")
    
    response = client.get('/get_profiles')
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Database error' in data['message']
    mock_user_repository.get_all_users.assert_called_once()