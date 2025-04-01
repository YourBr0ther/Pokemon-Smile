"""
Health check routes module.
Handles system health monitoring endpoints.
"""
from flask import Blueprint, jsonify
from app.database.mongodb import MongoDBManager

health_bp = Blueprint('health', __name__)

def init_health_routes(mongodb_manager: MongoDBManager):
    """Initialize health check routes with dependencies."""
    
    @health_bp.route('/health', methods=['GET'])
    def health_check():
        """Check system health status."""
        # Check MongoDB connection
        if mongodb_manager.is_connected():
            return jsonify({
                'status': 'healthy',
                'message': 'Service is healthy',
                'details': {
                    'database': 'connected'
                }
            })
        
        # Attempt reconnection
        if mongodb_manager.reconnect():
            return jsonify({
                'status': 'healthy',
                'message': 'Service recovered after reconnection',
                'details': {
                    'database': 'reconnected'
                }
            })
        
        # If in cooldown or max attempts exceeded
        if mongodb_manager.reconnect_attempts < mongodb_manager.config.MAX_RECONNECT_ATTEMPTS:
            return jsonify({
                'status': 'degraded',
                'message': 'Service is degraded',
                'details': {
                    'database': 'degraded'
                }
            }), 503
        
        # If reconnection failed
        return jsonify({
            'status': 'error',
            'message': 'Service is unavailable',
            'details': {
                'database': 'disconnected'
            }
        }), 503

    return health_bp 