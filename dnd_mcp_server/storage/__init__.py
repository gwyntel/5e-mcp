"""
Storage layer for 5e-mcp using py-key-value-aio backends.

Supports MemoryStore, DiskStore, and RedisStore configurable via environment variables.
"""

from dnd_mcp_server.storage.config import StorageConfig, get_storage_config
from dnd_mcp_server.storage.base import StorageManager
from dnd_mcp_server.storage.backends import create_storage_backend
from dnd_mcp_server.storage.game_state import GameState, GameStateManager
from dnd_mcp_server.storage.compat import get_game_state

__all__ = [
    "StorageConfig",
    "get_storage_config", 
    "StorageManager",
    "create_storage_backend",
    "GameState",
    "GameStateManager",
    "get_game_state"
]
