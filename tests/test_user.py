"""
Tests for the User model and UserRepository.
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.models.user import User, UserRepository

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    return MagicMock()

@pytest.fixture
def user_repository(mock_collection):
    """Create a UserRepository with a mock collection."""
    return UserRepository(mock_collection)

@pytest.fixture
def sample_user():
    """Create a sample user instance."""
    return User('testuser', 'password123')

def test_user_creation():
    """Test user creation with username and password."""
    user = User('testuser', 'password123')
    assert user.username == 'testuser'
    assert user.password_hash is not None
    assert user.caught_pokemon == []

def test_user_creation_no_password():
    """Test user creation without password."""
    user = User('testuser')
    assert user.username == 'testuser'
    assert user.password_hash is None
    assert user.caught_pokemon == []

def test_user_from_db_dict():
    """Test creating a user from a database dictionary."""
    db_dict = {
        'username': 'testuser',
        'password_hash': 'hashedpassword',
        'caught_pokemon': [1, 2, 3]
    }
    user = User.from_db_dict(db_dict)
    assert user.username == 'testuser'
    assert user.password_hash == 'hashedpassword'
    assert user.caught_pokemon == [1, 2, 3]

def test_user_to_db_dict():
    """Test converting a user to a database dictionary."""
    user = User('testuser', 'password123')
    user.caught_pokemon = [1, 2, 3]
    db_dict = user.to_db_dict()
    assert db_dict['username'] == 'testuser'
    assert db_dict['password_hash'] == user.password_hash
    assert db_dict['caught_pokemon'] == [1, 2, 3]

def test_check_password():
    """Test password checking."""
    user = User('testuser', 'password123')
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_check_password_no_hash():
    """Test password checking when no password is set."""
    user = User('testuser')
    assert not user.check_password('anypassword')

def test_catch_pokemon():
    """Test catching a Pokemon."""
    user = User('testuser', 'password123')
    user.catch_pokemon(1)
    assert 1 in user.caught_pokemon
    user.catch_pokemon(2)
    assert 2 in user.caught_pokemon

def test_get_caught_pokemon():
    """Test getting caught Pokemon."""
    user = User('testuser', 'password123')
    user.caught_pokemon = [1, 2, 3]
    assert user.get_caught_pokemon() == [1, 2, 3]

def test_user_to_dict():
    """Test converting a user to a dictionary."""
    user = User('testuser', 'password123')
    user.caught_pokemon = [1, 2, 3]
    user_dict = user.to_dict()
    assert user_dict['username'] == 'testuser'
    assert 'password_hash' not in user_dict
    assert user_dict['caught_pokemon'] == [1, 2, 3]

def test_repository_find_by_username(user_repository, mock_collection, sample_user):
    """Test finding a user by username."""
    mock_collection.find_one.return_value = sample_user.to_db_dict()
    
    user = user_repository.find_by_username('testuser')
    
    assert user is not None
    assert user.username == 'testuser'
    mock_collection.find_one.assert_called_once_with({'username': 'testuser'})

def test_repository_find_by_username_not_found(user_repository, mock_collection):
    """Test finding a non-existent user."""
    mock_collection.find_one.return_value = None
    
    user = user_repository.find_by_username('nonexistent')
    
    assert user is None
    mock_collection.find_one.assert_called_once_with({'username': 'nonexistent'})

def test_repository_create_user(user_repository, mock_collection, sample_user):
    """Test creating a new user."""
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value = Mock()
    
    result = user_repository.create_user(sample_user)
    
    assert result is True
    mock_collection.find_one.assert_called_once_with({'username': 'testuser'})
    mock_collection.insert_one.assert_called_once_with(sample_user.to_db_dict())

def test_repository_create_existing_user(user_repository, mock_collection, sample_user):
    """Test creating a user that already exists."""
    mock_collection.find_one.return_value = sample_user.to_db_dict()
    
    result = user_repository.create_user(sample_user)
    
    assert result is False
    mock_collection.find_one.assert_called_once_with({'username': 'testuser'})
    mock_collection.insert_one.assert_not_called()

def test_repository_update_user(user_repository, mock_collection, sample_user):
    """Test updating a user."""
    mock_collection.update_one.return_value = Mock(modified_count=1)
    
    result = user_repository.update_user(sample_user)
    
    assert result is True
    mock_collection.update_one.assert_called_once_with(
        {'username': 'testuser'},
        {'$set': sample_user.to_db_dict()}
    )

def test_repository_update_nonexistent_user(user_repository, mock_collection, sample_user):
    """Test updating a non-existent user."""
    mock_collection.update_one.return_value = Mock(modified_count=0)
    
    result = user_repository.update_user(sample_user)
    
    assert result is False
    mock_collection.update_one.assert_called_once_with(
        {'username': 'testuser'},
        {'$set': sample_user.to_db_dict()}
    )

def test_repository_delete_user(user_repository, mock_collection):
    """Test deleting a user."""
    mock_collection.delete_one.return_value = Mock(deleted_count=1)
    
    result = user_repository.delete_user('testuser')
    
    assert result is True
    mock_collection.delete_one.assert_called_once_with({'username': 'testuser'})

def test_repository_delete_nonexistent_user(user_repository, mock_collection):
    """Test deleting a non-existent user."""
    mock_collection.delete_one.return_value = Mock(deleted_count=0)
    
    result = user_repository.delete_user('nonexistent')
    
    assert result is False
    mock_collection.delete_one.assert_called_once_with({'username': 'nonexistent'})

def test_repository_get_all_users(user_repository, mock_collection, sample_user):
    """Test getting all users."""
    mock_collection.find.return_value = [
        sample_user.to_db_dict(),
        {**sample_user.to_db_dict(), 'username': 'testuser2'},
        {**sample_user.to_db_dict(), 'username': 'testuser3'}
    ]
    
    users = user_repository.get_all_users()
    
    assert len(users) == 3
    assert all(isinstance(user, User) for user in users)
    assert users[0].username == 'testuser'
    assert users[1].username == 'testuser2'
    assert users[2].username == 'testuser3'
    mock_collection.find.assert_called_once_with()

def test_repository_get_all_users_empty(user_repository, mock_collection):
    """Test getting all users when database is empty."""
    mock_collection.find.return_value = []
    
    users = user_repository.get_all_users()
    
    assert len(users) == 0
    mock_collection.find.assert_called_once_with() 