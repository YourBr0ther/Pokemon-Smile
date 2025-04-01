"""
MongoDB connection management module.
Handles connection, health checks, and reconnection logic.
"""
import time
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class MongoDBManager:
    """Manages MongoDB connection and health checks."""
    
    def __init__(self, config):
        """Initialize MongoDB manager with configuration."""
        self.config = config
        self.client: Optional[MongoClient] = None
        self.db = None
        self.last_reconnect_attempt = 0
        self.reconnect_attempts = 0
        self.connection_status = "disconnected"
        self.connect()

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            if self.client:
                try:
                    self.client.close()
                except Exception:
                    pass
            
            self.client = MongoClient(
                self.config.MONGODB_URI,
                serverSelectionTimeoutMS=self.config.MONGODB_TIMEOUT_MS
            )
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.config.MONGODB_DB_NAME]
            self.connection_status = "connected"
            self.reconnect_attempts = 0
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.connection_status = "disconnected"
            self.client = None
            self.db = None
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def is_connected(self):
        """Check if MongoDB is connected."""
        try:
            if self.client is None:
                return False
            if self.db is None:
                return False
            # Ping the database to verify the connection
            self.db.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False

    def reconnect(self) -> bool:
        """Attempt to reconnect to MongoDB."""
        current_time = time.time()
        
        # Check if we're in cooldown period
        if (current_time - self.last_reconnect_attempt) < self.config.RECONNECT_COOLDOWN:
            return False

        # Check if we've exceeded max attempts
        if self.reconnect_attempts >= self.config.MAX_RECONNECT_ATTEMPTS:
            return False

        try:
            self.connect()
            return True
        except ConnectionError:
            self.reconnect_attempts += 1
            self.last_reconnect_attempt = current_time
            return False

    def get_db(self):
        """Get the database instance."""
        if self.db is None or not self.is_connected():
            self.connect()
        return self.db

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            finally:
                self.client = None
                self.db = None
                self.connection_status = "disconnected" 