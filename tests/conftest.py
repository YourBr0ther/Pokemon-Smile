"""
Shared test fixtures for the Pokemon Smile application.
"""
import pytest
from unittest.mock import Mock, MagicMock
from flask import Flask
from app.models.user import User
from app.config.config import TestingConfig
from app.app import create_app

@pytest.fixture
def app(mock_user_repository, mock_pokemon_api):
    """Create a test Flask application."""
    app = create_app(TestingConfig())
    app.user_repository = mock_user_repository
    app.pokemon_api = mock_pokemon_api
    return app

@pytest.fixture
def mock_pokemon_api():
    """Create a mock Pokemon API client."""
    return Mock()

@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    mock = MagicMock()
    mock.find_by_username = MagicMock()
    mock.create_user = MagicMock()
    mock.update_user = MagicMock()
    mock.delete_user = MagicMock()
    mock.get_all_users = MagicMock()
    return mock

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

@pytest.fixture
def sample_user_data():
    """Create sample user data."""
    return {
        'username': 'testuser',
        'password_hash': 'hashed_password',
        'caught_pokemon': [1, 2, 3]
    }

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()
 