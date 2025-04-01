"""
Configuration module for the Pokemon Smile application.
Handles different environment configurations (development, testing, production).
"""
import os
import secrets
from datetime import timedelta
from pymongo import MongoClient

class Config:
    """Base configuration class."""
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(16))
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # MongoDB settings
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://mongo:27017/")
    MONGODB_DB_NAME = "pokemon_smile"
    MONGODB_TIMEOUT_MS = 20000
    
    @property
    def MONGODB_COLLECTION(self):
        """Get MongoDB collection for users."""
        client = MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=self.MONGODB_TIMEOUT_MS)
        db = client[self.MONGODB_DB_NAME]
        return db['users']
    
    # Pokemon API settings
    POKEAPI_BASE = os.environ.get("POKEAPI_BASE", "https://pokeapi.co/api/v2")
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = 10  # seconds
    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_COOLDOWN = 300  # seconds (5 minutes)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    # Use a separate database for testing
    MONGODB_DB_NAME = "pokemon_smile_test"
    # Shorter timeouts for faster tests
    MONGODB_TIMEOUT_MS = 5000
    HEALTH_CHECK_INTERVAL = 1

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Longer session lifetime for production
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])() 