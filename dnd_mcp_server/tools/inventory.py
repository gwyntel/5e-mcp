from typing import Dict, Any, List, Literal
from dnd_mcp_server.storage.game_state import get_game_state
from .character import calculate_ac

async def get_inventory(campaign_id: str = "default") -> Dict[str, Any]:
    """
    Get character's complete inventory including items, equipment, and gold.
    Example: get_inventory(campaign_id="campaign1") returns inventory JSON.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
    char = await state.character
    if not char:
        return {"error": "No character loaded."}
    return char.inventory.model_dump()

async def items_add(item_ids: List[str], equip_to_slot: Literal["main_hand", "off_hand", "armor", None] = None, campaign_id: str = "default") -> str:
    """
    Add multiple items to inventory and optionally equip the first one to a slot.
    Example: items_add(["longsword", "shield"], "main_hand", campaign_id="campaign1") 
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    char.inventory.items.extend(item_ids)
    msg = f"Added {', '.join(item_ids)} to inventory."
    
    # Auto-equip first item if slot specified
    if equip_to_slot and item_ids:
        item_id = item_ids[0]
        if equip_to_slot == "main_hand":
            char.inventory.equipped.main_hand = item_id
        elif equip_to_slot == "off_hand":
            char.inventory.equipped.off_hand = item_id
        elif equip_to_slot == "armor":
            char.inventory.equipped.armor = item_id
        msg += f" Equipped {item_id} to {equip_to_slot}."
    
    # TODO: Add logic to look up item weight and update total weight
    # Recalculate AC in case armor was equipped
    if equip_to_slot == "armor" or (equip_to_slot == "off_hand" and item_ids and "shield" in item_ids[0].lower()):
        await calculate_ac(campaign_id)
        
    await state.save_all()
    return msg

async def remove_item(item_id: str, campaign_id: str = "default") -> str:
    """
    Remove item from inventory and unequip if currently equipped.
    Example: remove_item("potion", campaign_id="campaign1") removes potion.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
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
            
        await calculate_ac(campaign_id)
        await state.save_all()
        return f"Removed {item_id} from inventory."
    else:
        return f"Item {item_id} not found in inventory."

async def equip_item(item_id: str, slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """
    Equip inventory item to specific equipment slot.
    Example: equip_item("shield", "off_hand", campaign_id="campaign1") equips shield.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
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
    
    await calculate_ac(campaign_id)
    await state.save_all()
    return f"Equipped {item_id} to {slot}."

async def unequip_item(slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """
    Unequip item from specified equipment slot.
    Example: unequip_item("main_hand", campaign_id="campaign1") unequips weapon.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
    char = await state.character
    if not char:
        return "Error: No character."
    
    if slot == "main_hand":
        char.inventory.equipped.main_hand = None
    elif slot == "off_hand":
        char.inventory.equipped.off_hand = None
    elif slot == "armor":
        char.inventory.equipped.armor = None
        
    await calculate_ac(campaign_id)
    await state.save_all()
    return f"Unequipped {slot}."

async def add_gold(amount: int, campaign_id: str = "default") -> str:
    """
    Add gold pieces to character's inventory.
    Example: add_gold(100, campaign_id="campaign1") adds 100 gold.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
    char = await state.character
    if not char: return "Error: No character."
    
    char.inventory.gold += amount
    await state.save_all()
    return f"Added {amount} gold. Total: {char.inventory.gold} gp."

async def remove_gold(amount: int, campaign_id: str = "default") -> str:
    """
    Remove gold from character's inventory if sufficient funds available.
    Example: remove_gold(25, campaign_id="campaign1") spends 25 gold.
    REQUIRED for persistent storage (e.g. Redis). 'default' is restricted on Redis.
    """
    state = get_game_state(campaign_id=campaign_id)
    char = await state.character
    if not char: return "Error: No character."
    
    if char.inventory.gold < amount:
        return f"Not enough gold! Current: {char.inventory.gold} gp."
    
    char.inventory.gold -= amount
    await state.save_all()
    return f"Spent {amount} gold. Remaining: {char.inventory.gold} gp."
