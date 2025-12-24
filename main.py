#!/usr/bin/env python3
"""
Solo D&D 5e MCP Server - Single Entrypoint
==========================================

This is the main entrypoint for the Solo D&D 5e MCP Server.
Run this file to start the MCP server.

Usage:
    python main.py
    python -m main
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up environment and configuration
def setup_environment():
    """Configure environment variables and paths"""
    # Load from .env file if present
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env file")
    
    # Configure storage backend
    backend = os.getenv("STORAGE_BACKEND", "memory")
    logger.info(f"Storage backend: {backend}")
    
    # Configure data directory for disk storage
    if backend == "disk":
        data_dir = Path(os.getenv("STORAGE_DISK_DIRECTORY", PROJECT_ROOT / "save_data"))
        os.environ.setdefault("STORAGE_DISK_DIRECTORY", str(data_dir))
        data_dir.mkdir(exist_ok=True)
        logger.info(f"Disk storage directory: {data_dir}")
    
    logger.info(f"Project root: {PROJECT_ROOT}")

# Import the MCP server at module level so FastMCP can find it
setup_environment()
from dnd_mcp_server.server import mcp

def main():
    """Main entry point for the application"""
    print("Starting Solo D&D 5e MCP Server...")
    print("=" * 50)
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
