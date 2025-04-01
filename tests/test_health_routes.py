"""
Tests for the health check routes.
"""
import json
import pytest
from unittest.mock import Mock
from flask import Flask
from app.routes.health import init_health_routes

@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def mock_mongodb_manager():
    """Create a mock MongoDB manager."""
    return Mock()

@pytest.fixture
def client(app, mock_mongodb_manager):
    """Create a test client with mocked dependencies."""
    health_bp = init_health_routes(mock_mongodb_manager)
    app.register_blueprint(health_bp)
    return app.test_client()

def test_health_check_healthy(client, mock_mongodb_manager):
    """Test health check with healthy status."""
    mock_mongodb_manager.is_connected.return_value = True
    mock_mongodb_manager.reconnect.return_value = True
    
    response = client.get('/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['message'] == 'Service is healthy'
    assert data['details']['database'] == 'connected'

def test_health_check_error_with_successful_reconnect(client, mock_mongodb_manager):
    """Test health check with error status but successful reconnection."""
    mock_mongodb_manager.is_connected.return_value = False
    mock_mongodb_manager.reconnect.return_value = True
    
    response = client.get('/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['message'] == 'Service recovered after reconnection'
    assert data['details']['database'] == 'reconnected'

def test_health_check_error_with_degraded_reconnect(client, mock_mongodb_manager):
    """Test health check with error status and degraded reconnection."""
    mock_mongodb_manager.is_connected.return_value = False
    mock_mongodb_manager.reconnect.side_effect = [False, True]
    
    response = client.get('/health')
    
    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['status'] == 'degraded'
    assert data['message'] == 'Service is degraded'
    assert data['details']['database'] == 'degraded'

def test_health_check_error_with_failed_reconnect(client, mock_mongodb_manager):
    """Test health check with error status and failed reconnection."""
    mock_mongodb_manager.is_connected.return_value = False
    mock_mongodb_manager.reconnect.return_value = False
    
    response = client.get('/health')
    
    assert response.status_code == 503
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert data['message'] == 'Service is unavailable'
    assert data['details']['database'] == 'disconnected' 