"""
Tests for the MongoDB manager module.
"""
import pytest
from unittest.mock import Mock, patch
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.database.mongodb import MongoDBManager
from app.config.config import TestingConfig

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = TestingConfig()
    config.MONGODB_URI = "mongodb://testhost:27017/"
    config.MONGODB_TIMEOUT_MS = 1000
    config.RECONNECT_COOLDOWN = 1  # Short cooldown for testing
    return config

@pytest.fixture
def mock_client():
    """Create a mock MongoDB client."""
    client = Mock()
    client.admin.command.return_value = True  # Successful ping
    return client

@patch('app.database.mongodb.MongoClient')
def test_successful_connection(mock_mongo_client, mock_config, mock_client):
    """Test successful MongoDB connection."""
    mock_mongo_client.return_value = mock_client
    
    manager = MongoDBManager(mock_config)
    assert manager.connection_status == "healthy"
    assert manager.client == mock_client
    assert manager.reconnect_attempts == 0

@patch('app.database.mongodb.MongoClient')
def test_connection_failure(mock_mongo_client, mock_config):
    """Test MongoDB connection failure."""
    mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
    
    with pytest.raises(ConnectionError) as exc_info:
        manager = MongoDBManager(mock_config)
    
    assert "Connection failed" in str(exc_info.value)

@patch('app.database.mongodb.MongoClient')
def test_connection_timeout(mock_mongo_client, mock_config):
    """Test MongoDB connection timeout."""
    mock_mongo_client.side_effect = ServerSelectionTimeoutError("Timeout")
    
    with pytest.raises(ConnectionError) as exc_info:
        manager = MongoDBManager(mock_config)
    
    assert "Timeout" in str(exc_info.value)

@patch('app.database.mongodb.MongoClient')
def test_health_check_healthy(mock_mongo_client, mock_config, mock_client):
    """Test health check with healthy connection."""
    mock_mongo_client.return_value = mock_client
    
    manager = MongoDBManager(mock_config)
    health = manager.check_connection()
    
    assert health["status"] == "healthy"
    assert "healthy" in health["message"].lower()

@patch('app.database.mongodb.MongoClient')
def test_health_check_error(mock_mongo_client, mock_config, mock_client):
    """Test health check with connection error."""
    mock_mongo_client.return_value = mock_client
    mock_client.admin.command.side_effect = ConnectionFailure("Connection lost")
    
    manager = MongoDBManager(mock_config)
    health = manager.check_connection()
    
    assert health["status"] == "error"
    assert "error" in health["message"].lower()

@patch('app.database.mongodb.MongoClient')
def test_reconnection_success(mock_mongo_client, mock_config, mock_client):
    """Test successful reconnection after failure."""
    # First connection fails
    mock_mongo_client.side_effect = [
        ConnectionFailure("First connection failed"),
        mock_client  # Second connection succeeds
    ]
    
    # Initial connection attempt
    with pytest.raises(ConnectionError):
        manager = MongoDBManager(mock_config)
    
    # Reset mock for reconnection
    mock_mongo_client.side_effect = None
    mock_mongo_client.return_value = mock_client
    
    # Attempt reconnection
    status = manager.attempt_reconnection()
    assert status["status"] == "healthy"
    assert "successfully" in status["message"].lower()

@patch('app.database.mongodb.MongoClient')
def test_max_reconnection_attempts(mock_mongo_client, mock_config):
    """Test maximum reconnection attempts limit."""
    mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
    
    with pytest.raises(ConnectionError):
        manager = MongoDBManager(mock_config)
    
    # Attempt reconnection multiple times
    for _ in range(mock_config.MAX_RECONNECT_ATTEMPTS + 1):
        status = manager.attempt_reconnection()
    
    assert status["status"] == "error"
    assert "maximum" in status["message"].lower()
    assert manager.reconnect_attempts >= mock_config.MAX_RECONNECT_ATTEMPTS

@patch('app.database.mongodb.MongoClient')
def test_reconnection_cooldown(mock_mongo_client, mock_config):
    """Test reconnection cooldown period."""
    mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
    
    with pytest.raises(ConnectionError):
        manager = MongoDBManager(mock_config)
    
    # First reconnection attempt
    status1 = manager.attempt_reconnection()
    assert status1["status"] == "error"
    
    # Immediate second attempt should be in cooldown
    status2 = manager.attempt_reconnection()
    assert status2["status"] == "degraded"
    assert "cooldown" in status2["message"].lower()

@patch('app.database.mongodb.MongoClient')
def test_close_connection(mock_mongo_client, mock_config, mock_client):
    """Test closing MongoDB connection."""
    mock_mongo_client.return_value = mock_client
    
    manager = MongoDBManager(mock_config)
    manager.close()
    
    assert manager.client is None
    assert manager.db is None
    assert manager.connection_status == "unknown"
    mock_client.close.assert_called_once() 