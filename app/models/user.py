"""
User model module.
Handles user-related operations and data management.
"""
from typing import Dict, Any, Optional, List
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for managing user data and operations."""
    
    def __init__(self, username: str, password: str = None, caught_pokemon: List[int] = None):
        """Initialize a user with basic information."""
        self.username = username
        self.password_hash = generate_password_hash(password) if password else None
        self.caught_pokemon = caught_pokemon or []

    @classmethod
    def from_db_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from database dictionary."""
        user = cls(username=data['username'])
        user.password_hash = data['password_hash']
        user.caught_pokemon = data.get('caught_pokemon', [])
        return user

    def to_db_dict(self) -> Dict[str, Any]:
        """Convert user to database dictionary."""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'caught_pokemon': self.caught_pokemon
        }

    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def catch_pokemon(self, pokemon_id: int) -> None:
        """Add a Pokemon to user's caught list."""
        if pokemon_id not in self.caught_pokemon:
            self.caught_pokemon.append(pokemon_id)

    def get_caught_pokemon(self) -> List[int]:
        """Get list of caught Pokemon IDs."""
        return self.caught_pokemon

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API responses."""
        return {
            'username': self.username,
            'caught_pokemon': self.caught_pokemon
        }

class UserRepository:
    """Repository for user-related database operations."""
    
    def __init__(self, collection):
        """Initialize repository with database collection."""
        self.collection = collection

    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        user_data = self.collection.find_one({'username': username})
        return User.from_db_dict(user_data) if user_data else None

    def create_user(self, user: User) -> bool:
        """Create a new user."""
        if self.find_by_username(user.username):
            return False
        
        self.collection.insert_one(user.to_db_dict())
        return True

    def update_user(self, user: User) -> bool:
        """Update existing user."""
        result = self.collection.update_one(
            {'username': user.username},
            {'$set': user.to_db_dict()}
        )
        return result.modified_count > 0

    def delete_user(self, username: str) -> bool:
        """Delete user by username."""
        result = self.collection.delete_one({'username': username})
        return result.deleted_count > 0

    def get_all_users(self) -> list:
        """Get all users from the database."""
        users = []
        for user_data in self.collection.find():
            user = User.from_db_dict(user_data)
            if user:
                users.append(user)
        return users 