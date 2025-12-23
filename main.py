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
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up environment and configuration
def setup_environment():
    """Configure environment variables and paths"""
    # Configure data directory to use relative path
    data_dir = PROJECT_ROOT / "save_data"
    os.environ.setdefault("DND_DATA_DIR", str(data_dir))
    
    # Create save_data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    print(f"Data directory: {data_dir}")
    print(f"Project root: {PROJECT_ROOT}")

def main():
    """Main entry point for the application"""
    setup_environment()
    
    # Import and run the MCP server
    from dnd_mcp_server.server import mcp
    
    print("Starting Solo D&D 5e MCP Server...")
    print("=" * 50)
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
