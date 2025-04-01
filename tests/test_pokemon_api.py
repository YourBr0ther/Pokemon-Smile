"""
Tests for the Pokemon API client module.
"""
import pytest
from unittest.mock import Mock, patch
import requests
from app.services.pokemon_api.client import PokemonAPIClient
from app.config.config import TestingConfig

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = TestingConfig()
    config.POKEAPI_BASE = "https://testapi.co/api/v2"
    return config

@pytest.fixture
def mock_pokemon_response():
    """Create a mock Pokemon response."""
    return {
        "id": 1,
        "name": "bulbasaur",
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
            "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/1.png"
        },
        "types": [
            {"type": {"name": "grass"}},
            {"type": {"name": "poison"}}
        ]
    }

@pytest.fixture
def mock_pokemon_list_response():
    """Create a mock Pokemon list response."""
    return {
        "count": 1118,
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"}
        ]
    }

@patch('requests.Session')
def test_get_pokemon_success(mock_session, mock_config, mock_pokemon_response):
    """Test successful Pokemon retrieval."""
    mock_response = Mock()
    mock_response.json.return_value = mock_pokemon_response
    mock_response.raise_for_status.return_value = None
    
    session = Mock()
    session.get.return_value = mock_response
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    pokemon = client.get_pokemon(1)
    
    assert pokemon["id"] == 1
    assert pokemon["name"] == "bulbasaur"
    assert len(pokemon["types"]) == 2
    assert pokemon["types"] == ["grass", "poison"]
    session.get.assert_called_once_with(f"{mock_config.POKEAPI_BASE}/pokemon/1")

@patch('requests.Session')
def test_get_pokemon_failure(mock_session, mock_config):
    """Test Pokemon retrieval failure."""
    session = Mock()
    session.get.side_effect = requests.exceptions.RequestException()
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    pokemon = client.get_pokemon(1)
    
    assert pokemon is None
    session.get.assert_called_once_with(f"{mock_config.POKEAPI_BASE}/pokemon/1")

@patch('requests.Session')
def test_get_pokemon_count(mock_session, mock_config, mock_pokemon_list_response):
    """Test Pokemon count retrieval."""
    mock_response = Mock()
    mock_response.json.return_value = mock_pokemon_list_response
    mock_response.raise_for_status.return_value = None
    
    session = Mock()
    session.get.return_value = mock_response
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    count = client.get_pokemon_count()
    
    assert count == 1118
    session.get.assert_called_once_with(f"{mock_config.POKEAPI_BASE}/pokemon")

@patch('requests.Session')
def test_get_pokemon_count_failure(mock_session, mock_config):
    """Test Pokemon count retrieval failure."""
    session = Mock()
    session.get.side_effect = requests.exceptions.RequestException()
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    count = client.get_pokemon_count()
    
    assert count == 0
    session.get.assert_called_once_with(f"{mock_config.POKEAPI_BASE}/pokemon")

@patch('requests.Session')
def test_get_pokemon_list(mock_session, mock_config, mock_pokemon_list_response):
    """Test Pokemon list retrieval."""
    mock_response = Mock()
    mock_response.json.return_value = mock_pokemon_list_response
    mock_response.raise_for_status.return_value = None
    
    session = Mock()
    session.get.return_value = mock_response
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    pokemon_list = client.get_pokemon_list(offset=0, limit=2)
    
    assert len(pokemon_list) == 2
    assert pokemon_list[0]["name"] == "bulbasaur"
    assert pokemon_list[1]["name"] == "ivysaur"
    session.get.assert_called_once_with(
        f"{mock_config.POKEAPI_BASE}/pokemon",
        params={"offset": 0, "limit": 2}
    )

@patch('requests.Session')
def test_get_pokemon_list_failure(mock_session, mock_config):
    """Test Pokemon list retrieval failure."""
    session = Mock()
    session.get.side_effect = requests.exceptions.RequestException()
    mock_session.return_value = session
    
    client = PokemonAPIClient(mock_config)
    pokemon_list = client.get_pokemon_list()
    
    assert len(pokemon_list) == 0
    session.get.assert_called_once_with(
        f"{mock_config.POKEAPI_BASE}/pokemon",
        params={"offset": 0, "limit": 20}
    )

def test_close_session(mock_config):
    """Test closing the session."""
    with patch('requests.Session') as mock_session:
        session = Mock()
        mock_session.return_value = session
        
        client = PokemonAPIClient(mock_config)
        client.close()
        
        session.close.assert_called_once() 