"""
Game state manager using new storage layer with multi-user support.
"""

from typing import Optional
import asyncio

from dnd_mcp_server.storage.base import StorageManager
from dnd_mcp_server.storage.config import get_storage_config
from dnd_mcp_server.storage.backends import create_storage_backend
from dnd_mcp_server.models.character import Character
from dnd_mcp_server.models.world import WorldState
from dnd_mcp_server.models.combat import CombatState


class GameState:
    """Game state for a specific user and campaign."""
    
    def __init__(self, user_id: str, campaign_id: str, storage_manager: StorageManager):
        self.user_id = user_id
        self.campaign_id = campaign_id
        self.storage = storage_manager
        
        # Cache for current session
        self._character: Optional[Character] = None
        self._world: Optional[WorldState] = None
        self._combat: Optional[CombatState] = None
        self._loaded = False
    
    async def _ensure_loaded(self):
        """Ensure data is loaded from storage."""
        if not self._loaded:
            self._character = await self.storage.get_character(self.user_id, self.campaign_id)
            self._world = await self.storage.get_world(self.user_id, self.campaign_id)
            self._combat = await self.storage.get_combat(self.user_id, self.campaign_id)
            self._loaded = True
    
    @property
    async def character(self) -> Optional[Character]:
        """Get character data."""
        await self._ensure_loaded()
        return self._character
    
    @property
    async def world(self) -> WorldState:
        """Get world state."""
        await self._ensure_loaded()
        return self._world or WorldState()
    
    @property
    async def combat(self) -> CombatState:
        """Get combat state."""
        await self._ensure_loaded()
        return self._combat or CombatState()
    
    async def save_character(self, character: Character) -> None:
        """Save character data."""
        self._character = character
        await self.storage.save_character(self.user_id, self.campaign_id, character)
    
    async def save_world(self, world: WorldState) -> None:
        """Save world state."""
        self._world = world
        await self.storage.save_world(self.user_id, self.campaign_id, world)
    
    async def save_combat(self, combat: CombatState) -> None:
        """Save combat state."""
        self._combat = combat
        await self.storage.save_combat(self.user_id, self.campaign_id, combat)
    
    async def save_all(self) -> None:
        """Save all cached data."""
        if self._character:
            await self.storage.save_character(self.user_id, self.campaign_id, self._character)
        if self._world:
            await self.storage.save_world(self.user_id, self.campaign_id, self._world)
        if self._combat:
            await self.storage.save_combat(self.user_id, self.campaign_id, self._combat)


class GameStateManager:
    """Global game state manager with caching."""
    
    def __init__(self):
        self.config = get_storage_config()
        self.storage_backend = create_storage_backend(self.config)
        self.storage_manager = StorageManager(
            self.storage_backend, 
            self.config.namespace_prefix
        )
        self._cache: dict[str, GameState] = {}
    
    def _cache_key(self, user_id: str, campaign_id: str) -> str:
        """Generate cache key for user and campaign."""
        return f"{user_id}:{campaign_id}"
    
    def get_game_state(self, user_id: str = "default", campaign_id: str = "default") -> GameState:
        """Get game state for user and campaign."""
        cache_key = self._cache_key(user_id, campaign_id)
        if cache_key not in self._cache:
            self._cache[cache_key] = GameState(user_id, campaign_id, self.storage_manager)
        return self._cache[cache_key]
    
    async def clear_cache(self, user_id: Optional[str] = None, campaign_id: Optional[str] = None) -> None:
        """Clear cached game states."""
        if user_id and campaign_id:
            cache_key = self._cache_key(user_id, campaign_id)
            self._cache.pop(cache_key, None)
        elif user_id:
            # Clear all campaigns for user
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                self._cache.pop(key, None)
        else:
            # Clear all cache
            self._cache.clear()


# Global instance
_game_state_manager = GameStateManager()


def get_game_state(user_id: str = "default", campaign_id: str = "default") -> GameState:
    """Get game state for user and campaign (backward compatibility)."""
    return _game_state_manager.get_game_state(user_id, campaign_id)


async def get_user_campaigns(user_id: str) -> list[str]:
    """Get list of campaigns for a user."""
    return await _game_state_manager.storage_manager.list_user_campaigns(user_id)


async def delete_campaign_data(user_id: str, campaign_id: str) -> None:
    """Delete all data for a campaign."""
    await _game_state_manager.storage_manager.delete_campaign_data(user_id, campaign_id)
    await _game_state_manager.clear_cache(user_id, campaign_id)
