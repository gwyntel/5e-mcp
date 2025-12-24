"""
Storage backend implementations using py-key-value-aio.
"""

import os
import asyncio
from typing import Optional

from dnd_mcp_server.storage.base import StorageInterface
from dnd_mcp_server.storage.config import StorageConfig, StorageBackend


class MemoryStorage(StorageInterface):
    """In-memory storage implementation."""
    
    def __init__(self):
        self._data: dict[str, str] = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value by key with optional TTL (ignored for memory)."""
        self._data[key] = value
    
    async def delete(self, key: str) -> None:
        """Delete a value by key."""
        self._data.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return key in self._data


class DiskStorage(StorageInterface):
    """Disk storage implementation using JSON files."""
    
    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for a key."""
        # Replace colons with underscores for valid filenames
        safe_key = key.replace(":", "_")
        return os.path.join(self.directory, f"{safe_key}.json")
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    return data.get("value")
            except Exception as e:
                print(f"Error reading from disk storage: {e}")
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value by key with optional TTL."""
        file_path = self._get_file_path(key)
        try:
            import json
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            data: dict[str, str | float] = {"value": value}
            if ttl:
                import time
                data["expires_at"] = time.time() + ttl
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing to disk storage: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete a value by key."""
        file_path = self._get_file_path(key)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting from disk storage: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return False
        
        # Check TTL if present
        try:
            import json
            import time
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "expires_at" in data and time.time() > data["expires_at"]:
                    os.remove(file_path)
                    return False
            return True
        except Exception:
            return False


class RedisStorage(StorageInterface):
    """Redis storage implementation using py-key-value-aio."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 password: Optional[str] = None, db: int = 0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self._client = None
        self._ready = False
        self._lock = asyncio.Lock()
    
    async def _ensure_ready(self):
        """Ensure client is initialized and setup() has been called."""
        if self._ready:
            return
            
        async with self._lock:
            if self._ready:
                return
                
            client = self._get_client()
            try:
                # setup() is necessary for RedisStore to initialize connections/pools
                await client.setup()
                self._ready = True
            except Exception as e:
                print(f"Error during Redis setup: {e}")
                raise
    
    def _get_client(self):
        """Get Redis client (lazy initialization)."""
        if self._client is None:
            try:
                from key_value.aio.stores.redis import RedisStore
                import redis.asyncio as redis
                
                # Construct URL for consistency and SSL support
                # Heuristic: upstash usually implies SSL (rediss)
                protocol = "rediss" if self.password and "upstash" in self.host else "redis"
                
                if self.password:
                    url = f"{protocol}://default:{self.password}@{self.host}:{self.port}/{self.db}"
                else:
                    url = f"{protocol}://{self.host}:{self.port}/{self.db}"

                # Create explicit client with decode_responses=True (CRITICAL)
                raw_client = redis.from_url(url, decode_responses=True)
                
                self._client = RedisStore(client=raw_client)
                
            except ImportError:
                raise ImportError(
                    "Redis support requires 'py-key-value-aio[redis]'. "
                    "Install with: pip install 'py-key-value-aio[redis]'"
                )
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        try:
            await self._ensure_ready()
            client = self._get_client()
            result = await client.get(key)
            # Handle different return types from py-key-value-aio
            if result is None:
                return None
            elif isinstance(result, str):
                return result
            elif isinstance(result, dict) and 'value' in result:
                return str(result['value'])
            else:
                # Try to get value attribute as fallback
                value = getattr(result, 'value', result)
                return str(value)
        except Exception as e:
            print(f"Error getting from Redis: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value by key with optional TTL."""
        try:
            await self._ensure_ready()
            client = self._get_client()
            # py-key-value-aio expects dict-like for put method
            await client.put(key, {"value": value}, ttl=ttl)
        except Exception as e:
            print(f"Error setting to Redis: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete a value by key."""
        try:
            await self._ensure_ready()
            client = self._get_client()
            await client.delete(key)
        except Exception as e:
            print(f"Error deleting from Redis: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        try:
            await self._ensure_ready()
            client = self._get_client()
            result = await client.get(key)
            return result is not None
        except Exception as e:
            print(f"Error checking key existence in Redis: {e}")
            return False


def create_storage_backend(config: StorageConfig) -> StorageInterface:
    """Create storage backend based on configuration."""
    
    if config.backend == StorageBackend.MEMORY:
        return MemoryStorage()
    
    elif config.backend == StorageBackend.DISK:
        return DiskStorage(config.disk_directory)
    
    elif config.backend == StorageBackend.REDIS:
        return RedisStorage(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password,
            db=config.redis_db
        )
    
    else:
        raise ValueError(f"Unsupported storage backend: {config.backend}")
