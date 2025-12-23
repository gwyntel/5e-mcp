#!/usr/bin/env python3
"""
Storage Integration Test for Solo D&D MCP Server

This script tests the fixed storage backend to ensure all previously
failing features now work correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure test environment
os.environ["STORAGE_BACKEND"] = "disk"
os.environ["STORAGE_DISK_DIRECTORY"] = str(PROJECT_ROOT / "test_save_data")

from dnd_mcp_server.storage.game_state import get_game_state


async def test_character_creation():
    """Test 1: Create a character"""
    print("\n=== TEST 1: Character Creation ===")
    from dnd_mcp_server.tools.character import create_character
    
    result = await create_character(
        name="TestHero",
        race="Human",
        class_name="Fighter",
        background="Soldier",
        stats={"str": 16, "dex": 14, "con": 15, "int": 10, "wis": 12, "cha": 8}
    )
    print(f"✓ {result}")
    return "PASS" if "created successfully" in result.lower() else "FAIL"


async def test_character_retrieval():
    """Test 2: Retrieve character sheet"""
    print("\n=== TEST 2: Character Sheet Retrieval ===")
    from dnd_mcp_server.tools.character import get_character_sheet
    import json
    
    result = await get_character_sheet()
    
    # Check if it's valid JSON and has expected fields
    try:
        data = json.loads(result)
        if "error" in data:
            print(f"✗ Error: {data['error']}")
            return "FAIL"
        
        if data.get("identity", {}).get("name") == "TestHero":
            print(f"✓ Character retrieved: {data['identity']['name']}")
            print(f"  HP: {data['health']['current_hp']}/{data['health']['max_hp']}")
            print(f"  AC: {data['defense']['ac']}")
            return "PASS"
        else:
            print(f"✗ Wrong character data")
            return "FAIL"
    except Exception as e:
        print(f"✗ Failed to parse: {e}")
        return "FAIL"


async def test_inventory():
    """Test 3: Inventory management"""
    print("\n=== TEST 3: Inventory Management ===")
    from dnd_mcp_server.tools.inventory import add_item, get_inventory
    
    # Add an item
    add_result = await add_item("longsword", "main_hand")
    print(f"  Add item: {add_result}")
    
    # Get inventory
    inv = await get_inventory()
    if "error" in inv:
        print(f"✗ Error getting inventory: {inv['error']}")
        return "FAIL"
    
    if "longsword" in inv.get("items", []):
        print(f"✓ Inventory test passed")
        print(f"  Items: {inv['items']}")
        print(f"  Gold: {inv.get('gold', 0)} gp")
        return "PASS"
    else:
        print(f"✗ Item not found in inventory")
        return "FAIL"


async def test_persistence():
    """Test 4: Data persistence across state reloads"""
    print("\n=== TEST 4: Persistence Test ===")
    from dnd_mcp_server.tools.character import get_character_sheet
    from dnd_mcp_server.storage.game_state import _game_state_manager
    import json
    
    # Clear cache to force reload from storage
    await _game_state_manager.clear_cache()
    print("  Cleared cache, reloading from storage...")
    
    # Try to get character again
    result = await get_character_sheet()
    try:
        data = json.loads(result)
        if "error" in data:
            print(f"✗ Character not persisted: {data['error']}")
            return "FAIL"
        
        if data.get("identity", {}).get("name") == "TestHero":
            print(f"✓ Character persisted correctly")
            return "PASS"
        else:
            print(f"✗ Wrong character after reload")
            return "FAIL"
    except Exception as e:
        print(f"✗ Failed: {e}")
        return "FAIL"


async def test_hp_update():
    """Test 5: HP updates and saves"""
    print("\n=== TEST 5: HP Update Test ===")
    from dnd_mcp_server.tools.character import update_hp, get_character_sheet
    import json
    
    # Deal damage
    damage_result = await update_hp(5, "damage")
    print(f"  Damage: {damage_result}")
    
    # Verify HP changed
    result = await get_character_sheet()
    data = json.loads(result)
    current_hp = data['health']['current_hp']
    max_hp = data['health']['max_hp']
    
    if current_hp < max_hp:
        print(f"✓ HP updated: {current_hp}/{max_hp}")
        return "PASS"
    else:
        print(f"✗ HP not updated")
        return "FAIL"


async def main():
    """Run all tests"""
    print("=" * 60)
    print("STORAGE BACKEND INTEGRATION TESTS")
    print("=" * 60)
    
    # Clean up any previous test data
    test_dir = PROJECT_ROOT / "test_save_data"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    tests = [
        test_character_creation,
        test_character_retrieval,
        test_inventory,
        test_persistence,
        test_hp_update
    ]
    
    results = {}
    for test in tests:
        try:
            results[test.__name__] = await test()
        except Exception as e:
            print(f"\n✗ {test.__name__} EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results[test.__name__] = "ERROR"
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    for name, result in results.items():
        symbol = "✓" if result == "PASS" else "✗"
        print(f"{symbol} {name}: {result}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
