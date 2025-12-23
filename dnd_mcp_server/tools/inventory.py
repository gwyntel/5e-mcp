from typing import Dict, Any, List, Literal
from dnd_mcp_server.storage.game_state import get_game_state

async def get_inventory(campaign_id: str = "default") -> Dict[str, Any]:
    """
    Get character's complete inventory including items, equipment, and gold.
    Example: get_inventory() returns {"items": ["sword", "potion"], "gold": 50, "equipped": {...}}
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char:
        return {"error": "No character loaded."}
    return char.inventory.model_dump()

async def add_item(item_id: str, equip_to_slot: Literal["main_hand", "off_hand", "armor", None] = None, campaign_id: str = "default") -> str:
    """
    Add item to inventory and optionally equip it to a slot.
    Example: add_item("longsword", "main_hand") adds and equips longsword.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    char.inventory.items.append(item_id)
    msg = f"Added {item_id} to inventory."
    
    # Auto-equip if slot specified
    if equip_to_slot:
        if equip_to_slot == "main_hand":
            char.inventory.equipped.main_hand = item_id
        elif equip_to_slot == "off_hand":
            char.inventory.equipped.off_hand = item_id
        elif equip_to_slot == "armor":
            char.inventory.equipped.armor = item_id
        msg += f" Equipped to {equip_to_slot}."
    
    # TODO: Add logic to look up item weight and update total weight
    await state.save_all()
    return msg

async def remove_item(item_id: str, campaign_id: str = "default") -> str:
    """
    Remove item from inventory and unequip if currently equipped.
    Example: remove_item("potion") removes potion from inventory.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    if item_id in char.inventory.items:
        char.inventory.items.remove(item_id)
        # Check if equipped and unequip if so
        if char.inventory.equipped.main_hand == item_id:
            char.inventory.equipped.main_hand = None
        if char.inventory.equipped.off_hand == item_id:
            char.inventory.equipped.off_hand = None
        if char.inventory.equipped.armor == item_id:
            char.inventory.equipped.armor = None
            
        await state.save_all()
        return f"Removed {item_id} from inventory."
    else:
        return f"Item {item_id} not found in inventory."

async def equip_item(item_id: str, slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """
    Equip inventory item to specific equipment slot.
    Example: equip_item("shield", "off_hand") equips shield to off hand.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    if item_id not in char.inventory.items:
        return f"Cannot equip {item_id}: Not in inventory."
    
    # Simple Equip logic
    if slot == "main_hand":
        char.inventory.equipped.main_hand = item_id
    elif slot == "off_hand":
        char.inventory.equipped.off_hand = item_id
    elif slot == "armor":
        char.inventory.equipped.armor = item_id
    
    await state.save_all()
    return f"Equipped {item_id} to {slot}."

async def unequip_item(slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """
    Unequip item from specified equipment slot.
    Example: unequip_item("main_hand") unequips main hand weapon.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    if slot == "main_hand":
        char.inventory.equipped.main_hand = None
    elif slot == "off_hand":
        char.inventory.equipped.off_hand = None
    elif slot == "armor":
        char.inventory.equipped.armor = None
        
    await state.save_all()
    return f"Unequipped {slot}."

async def add_gold(amount: int, campaign_id: str = "default") -> str:
    """
    Add gold pieces to character's inventory.
    Example: add_gold(100) adds 100 gold to character's total.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char: return "Error: No character."
    
    char.inventory.gold += amount
    await state.save_all()
    return f"Added {amount} gold. Total: {char.inventory.gold} gp."

async def remove_gold(amount: int, campaign_id: str = "default") -> str:
    """
    Remove gold from character's inventory if sufficient funds available.
    Example: remove_gold(25) spends 25 gold if character has enough.
    """
    state = get_game_state(campaign_id)
    char = await state.character
    if not char: return "Error: No character."
    
    if char.inventory.gold < amount:
        return f"Not enough gold! Current: {char.inventory.gold} gp."
    
    char.inventory.gold -= amount
    await state.save_all()
    return f"Spent {amount} gold. Remaining: {char.inventory.gold} gp."
