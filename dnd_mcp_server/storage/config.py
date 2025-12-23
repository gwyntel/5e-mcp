"""
Storage configuration for 5e-mcp using environment variables.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StorageBackend(str, Enum):
    """Supported storage backends."""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"


class StorageConfig(BaseModel):
    """Configuration for storage backends."""
    
    backend: StorageBackend = Field(
        default=StorageBackend.MEMORY,
        description="Storage backend to use"
    )
    
    # Disk storage configuration
    disk_directory: str = Field(
        default="./save_data",
        description="Directory for disk storage"
    )
    
    # Redis configuration
    redis_host: str = Field(
        default="localhost",
        description="Redis host"
    )
    
    redis_port: int = Field(
        default=6379,
        description="Redis port"
    )
    
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password"
    )
    
    redis_db: int = Field(
        default=0,
        description="Redis database number"
    )
    
    # Encryption configuration
    encryption_key: Optional[str] = Field(
        default=None,
        description="Encryption key for sensitive data (base64 encoded)"
    )
    
    # Namespace configuration
    namespace_prefix: str = Field(
        default="5e_mcp",
        description="Prefix for all storage keys"
    )


def get_storage_config() -> StorageConfig:
    """Load storage configuration from environment variables."""
    return StorageConfig(
        backend=StorageBackend(os.getenv("STORAGE_BACKEND", "memory")),
        disk_directory=os.getenv("STORAGE_DISK_DIRECTORY", "./save_data"),
        redis_host=os.getenv("STORAGE_REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("STORAGE_REDIS_PORT", "6379")),
        redis_password=os.getenv("STORAGE_REDIS_PASSWORD"),
        redis_db=int(os.getenv("STORAGE_REDIS_DB", "0")),
        encryption_key=os.getenv("STORAGE_ENCRYPTION_KEY"),
        namespace_prefix=os.getenv("STORAGE_NAMESPACE_PREFIX", "5e_mcp")
    )
