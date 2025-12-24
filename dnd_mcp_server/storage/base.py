"""
Base storage manager interface for 5e-mcp.
"""

import json
from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod

from dnd_mcp_server.models.character import Character
from dnd_mcp_server.models.world import WorldState
from dnd_mcp_server.models.combat import CombatState
from dnd_mcp_server.models.campaign import CampaignState


class StorageInterface(ABC):
    """Abstract interface for storage backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value by key with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value by key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        pass


class StorageManager:
    """High-level storage manager for 5e-mcp data."""
    
    def __init__(self, storage: StorageInterface, namespace: str = "5e_mcp"):
        self.storage = storage
        self.namespace = namespace
    
    def _key(self, user_id: str, campaign_id: str, data_type: str) -> str:
        """Generate namespaced key for storage."""
        return f"{self.namespace}:user:{user_id}:campaign:{campaign_id}:{data_type}"
    
    async def get_character(self, user_id: str, campaign_id: str) -> Optional[Character]:
        """Get character data for user and campaign."""
        key = self._key(user_id, campaign_id, "character")
        data = await self.storage.get(key)
        if data:
            try:
                return Character(**json.loads(data))
            except Exception as e:
                print(f"Error parsing character data: {e}")
        return None
    
    async def save_character(self, user_id: str, campaign_id: str, character: Character) -> None:
        """Save character data for user and campaign."""
        key = self._key(user_id, campaign_id, "character")
        await self.storage.set(key, character.model_dump_json())
    
    async def get_world(self, user_id: str, campaign_id: str) -> WorldState:
        """Get world state for user and campaign."""
        key = self._key(user_id, campaign_id, "world")
        data = await self.storage.get(key)
        if data:
            try:
                return WorldState(**json.loads(data))
            except Exception as e:
                print(f"Error parsing world data: {e}")
        return WorldState()
    
    async def save_world(self, user_id: str, campaign_id: str, world: WorldState) -> None:
        """Save world state for user and campaign."""
        key = self._key(user_id, campaign_id, "world")
        await self.storage.set(key, world.model_dump_json())
    
    async def get_combat(self, user_id: str, campaign_id: str) -> CombatState:
        """Get combat state for user and campaign."""
        key = self._key(user_id, campaign_id, "combat")
        data = await self.storage.get(key)
        if data:
            try:
                return CombatState(**json.loads(data))
            except Exception as e:
                print(f"Error parsing combat data: {e}")
        return CombatState()
    
    async def save_combat(self, user_id: str, campaign_id: str, combat: CombatState) -> None:
        """Save combat state for user and campaign."""
        key = self._key(user_id, campaign_id, "combat")
        await self.storage.set(key, combat.model_dump_json())
    
    async def get_campaign(self, user_id: str, campaign_id: str) -> Optional[CampaignState]:
        """Get campaign state for user and campaign."""
        key = self._key(user_id, campaign_id, "campaign")
        data = await self.storage.get(key)
        if data:
            try:
                return CampaignState(**json.loads(data))
            except Exception as e:
                print(f"Error parsing campaign data: {e}")
        return None
    
    async def save_campaign(self, user_id: str, campaign_id: str, campaign: CampaignState) -> None:
        """Save campaign state for user and campaign."""
        key = self._key(user_id, campaign_id, "campaign")
        await self.storage.set(key, campaign.model_dump_json())
    
    async def delete_campaign_data(self, user_id: str, campaign_id: str) -> None:
        """Delete all data for a specific campaign."""
        data_types = ["character", "world", "combat", "campaign"]
        for data_type in data_types:
            key = self._key(user_id, campaign_id, data_type)
            await self.storage.delete(key)
    
    async def list_user_campaigns(self, user_id: str) -> list[str]:
        """List all campaigns for a user (implementation depends on backend)."""
        # This would need backend-specific implementation for key listing
        # For now, return empty list - can be implemented per backend
        return []
