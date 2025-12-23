# Storage Migration Guide

This document explains the migration from the old file-based storage to the new py-key-value-aio based storage system.

## Overview

The 5e-mcp server has been upgraded to use pluggable storage backends supporting:
- **Memory Storage** (default) - In-memory for development
- **Disk Storage** - Persistent file-based storage for single-server deployments
- **Redis Storage** - Distributed storage for multi-server/cloud deployments

## Configuration

Storage is configured via environment variables. Copy `.env.example` to `.env` and modify:

```bash
# Storage backend: memory, disk, or redis
STORAGE_BACKEND=memory

# Disk storage (when STORAGE_BACKEND=disk)
STORAGE_DISK_DIRECTORY=./save_data

# Redis storage (when STORAGE_BACKEND=redis)
STORAGE_REDIS_HOST=localhost
STORAGE_REDIS_PORT=6379
STORAGE_REDIS_PASSWORD=
STORAGE_REDIS_DB=0

# Optional encryption for sensitive data
STORAGE_ENCRYPTION_KEY=
STORAGE_NAMESPACE_PREFIX=5e_mcp
```

## Multi-User Support

The new system supports multiple users with isolated data:
- **Old**: `campaign_id` only
- **New**: `user_id` + `campaign_id`

Data is stored with keys like: `5e_mcp:user:{user_id}:campaign:{campaign_id}:character`

## Backward Compatibility

Existing tools continue to work with `campaign_id` parameter only:
- `user_id` defaults to "default" for backward compatibility
- All existing function signatures preserved

## Installation

```bash
# Install new dependencies
pip install -r requirements.txt

# For Redis support (optional)
pip install 'py-key-value-aio[redis]'
```

## Migration

Data from the old `/save_data/` directory needs to be migrated to the new format. The system will automatically create new storage locations when first accessed.

## Deployment Options

### Development
```bash
export STORAGE_BACKEND=memory
python -m dnd_mcp_server.server
```

### Single Server (Production)
```bash
export STORAGE_BACKEND=disk
export STORAGE_DISK_DIRECTORY=/var/lib/5e-mcp
python -m dnd_mcp_server.server
```

### Cloud/Distributed
```bash
export STORAGE_BACKEND=redis
export STORAGE_REDIS_HOST=redis.example.com
export STORAGE_REDIS_PORT=6379
export STORAGE_REDIS_PASSWORD=your-password
python -m dnd_mcp_server.server
```

## Benefits

1. **Scalability**: Redis/DynamoDB support for horizontal scaling
2. **Multi-tenancy**: User isolation with encryption support
3. **Flexibility**: Easy backend swapping via configuration
4. **Production-ready**: Built-in caching, monitoring, and FastMCP integration
5. **Cloud Native**: Designed for containerized deployments

## FastMCP Integration

The new storage layer is designed to work with FastMCP middleware:
- Response caching with persistent storage
- OAuth token storage with encryption
- Proper key management for production

## Security

- Optional encryption for sensitive character data
- User isolation via namespacing
- Configurable TTL for cache entries
- Production-ready key management
