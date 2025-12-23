"""
Compatibility layer for migrating from sync to async storage.
"""

from typing import Optional
from dnd_mcp_server.storage.game_state import get_game_state as get_async_game_state
from dnd_mcp_server.models.character import Character
from dnd_mcp_server.models.world import WorldState
from dnd_mcp_server.models.combat import CombatState


class SyncGameState:
    """Synchronous wrapper around async game state for backward compatibility."""
    
    def __init__(self, user_id: str = "default", campaign_id: str = "default"):
        self.user_id = user_id
        self.campaign_id = campaign_id
        self._async_state = get_async_game_state(user_id, campaign_id)
        self._character: Optional[Character] = None
        self._world: Optional[WorldState] = None
        self._combat: Optional[CombatState] = None
        self._loaded = False
    
    def _ensure_loaded(self):
        """Ensure data is loaded from storage."""
        if not self._loaded:
            import asyncio
            # Create event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Load data synchronously
            self._character = loop.run_until_complete(self._async_state.character)
            self._world = loop.run_until_complete(self._async_state.world)
            self._combat = loop.run_until_complete(self._async_state.combat)
            self._loaded = True
    
    @property
    def character(self) -> Optional[Character]:
        """Get character data."""
        self._ensure_loaded()
        return self._character
    
    @property
    def world(self) -> WorldState:
        """Get world state."""
        self._ensure_loaded()
        return self._world or WorldState()
    
    @property
    def combat(self) -> CombatState:
        """Get combat state."""
        self._ensure_loaded()
        return self._combat or CombatState()
    
    def save_character(self, character: Character) -> None:
        """Save character data."""
        self._character = character
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_state.save_character(character))
    
    def set_character(self, character: Character) -> None:
        """Set character data without saving."""
        self._character = character
    
    def save_world(self, world: WorldState) -> None:
        """Save world state."""
        self._world = world
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_state.save_world(world))
    
    def save_combat(self, combat: CombatState) -> None:
        """Save combat state."""
        self._combat = combat
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_state.save_combat(combat))
    
    def save_all(self) -> None:
        """Save all cached data."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_state.save_all())


def get_game_state(user_id: str = "default", campaign_id: str = "default") -> SyncGameState:
    """Get synchronous game state for backward compatibility."""
    return SyncGameState(user_id, campaign_id)
