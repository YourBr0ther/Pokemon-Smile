"""
Tests for the configuration module.
"""
import os
import pytest
from app.config.config import get_config, Config, DevelopmentConfig, TestingConfig, ProductionConfig

def test_default_config():
    """Test default configuration."""
    config = get_config()
    assert isinstance(config, DevelopmentConfig)
    assert config.DEBUG is True
    assert config.TESTING is False

def test_development_config():
    """Test development configuration."""
    os.environ['FLASK_ENV'] = 'development'
    config = get_config()
    assert isinstance(config, DevelopmentConfig)
    assert config.DEBUG is True
    assert config.TESTING is False
    assert config.MONGODB_DB_NAME == 'pokemon_smile'

def test_testing_config():
    """Test testing configuration."""
    os.environ['FLASK_ENV'] = 'testing'
    config = get_config()
    assert isinstance(config, TestingConfig)
    assert config.DEBUG is True
    assert config.TESTING is True
    assert config.MONGODB_DB_NAME == 'pokemon_smile_test'
    assert config.MONGODB_TIMEOUT_MS == 5000
    assert config.HEALTH_CHECK_INTERVAL == 1

def test_production_config():
    """Test production configuration."""
    os.environ['FLASK_ENV'] = 'production'
    config = get_config()
    assert isinstance(config, ProductionConfig)
    assert config.DEBUG is False
    assert config.TESTING is False
    assert config.MONGODB_DB_NAME == 'pokemon_smile'

def test_invalid_env_returns_default():
    """Test that invalid environment returns default config."""
    os.environ['FLASK_ENV'] = 'invalid'
    config = get_config()
    assert isinstance(config, DevelopmentConfig)

def test_mongodb_uri_from_env():
    """Test MongoDB URI configuration from environment."""
    test_uri = 'mongodb://testhost:27017/'
    os.environ['MONGODB_URI'] = test_uri
    config = get_config()
    assert config.MONGODB_URI == test_uri

def test_pokeapi_base_from_env():
    """Test PokeAPI base URL configuration from environment."""
    test_base = 'https://testapi.co/api/v2'
    os.environ['POKEAPI_BASE'] = test_base
    config = get_config()
    assert config.POKEAPI_BASE == test_base

@pytest.fixture(autouse=True)
def cleanup_env():
    """Clean up environment variables after each test."""
    yield
    env_vars = ['FLASK_ENV', 'MONGODB_URI', 'POKEAPI_BASE']
    for var in env_vars:
        os.environ.pop(var, None) 