"""
Pokemon API client module.
Handles interactions with the PokeAPI service.
"""
import requests
from typing import Dict, Any, Optional, List
from functools import lru_cache

class PokemonAPIClient:
    """Client for interacting with the Pokemon API."""
    
    def __init__(self, config):
        """Initialize Pokemon API client with configuration."""
        self.base_url = config.POKEAPI_BASE
        self.session = requests.Session()

    @lru_cache(maxsize=100)
    def get_pokemon(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Pokemon details by ID.
        Uses caching to improve performance.
        """
        try:
            response = self.session.get(f"{self.base_url}/pokemon/{pokemon_id}")
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            return {
                "id": data["id"],
                "name": data["name"].capitalize(),
                "sprites": {
                    "front_default": data["sprites"]["front_default"],
                    "front_shiny": data["sprites"]["front_shiny"]
                },
                "types": [t["type"]["name"] for t in data["types"]]
            }
        except requests.exceptions.RequestException:
            return None

    def get_pokemon_details(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Alias for get_pokemon to match test expectations."""
        return self.get_pokemon(pokemon_id)

    @lru_cache(maxsize=1)
    def get_pokemon_count(self) -> int:
        """
        Get total number of Pokemon available.
        Uses caching as this rarely changes.
        """
        try:
            response = self.session.get(f"{self.base_url}/pokemon")
            response.raise_for_status()
            return response.json()["count"]
        except requests.exceptions.RequestException:
            return 0

    def get_pokemon_list(self, offset: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get a paginated list of Pokemon."""
        try:
            response = self.session.get(
                f"{self.base_url}/pokemon",
                params={"offset": offset, "limit": limit}
            )
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException:
            return []

    def close(self):
        """Close the session."""
        self.session.close() 