"""
Main entry point for Pokemon Smile application
"""
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 