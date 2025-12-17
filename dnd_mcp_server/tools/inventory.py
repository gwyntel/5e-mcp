from typing import Dict, Any, List, Literal
from ..persistence.state import get_game_state

def get_inventory(campaign_id: str = "default") -> Dict[str, Any]:
    """Returns the character's full inventory state."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char:
        return {"error": "No character loaded."}
    return char.inventory.model_dump()

def add_item(item_id: str, campaign_id: str = "default") -> str:
    """Adds an item to the inventory."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char:
        return "Error: No character."
    
    char.inventory.items.append(item_id)
    # TODO: Add logic to look up item weight and update total weight
    state.save_all()
    return f"Added {item_id} to inventory."

def remove_item(item_id: str, campaign_id: str = "default") -> str:
    """Removes an item from the inventory."""
    state = get_game_state(campaign_id)
    char = state.character
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
            
        state.save_all()
        return f"Removed {item_id} from inventory."
    else:
        return f"Item {item_id} not found in inventory."

def equip_item(item_id: str, slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """Equips an item to a specific slot."""
    state = get_game_state(campaign_id)
    char = state.character
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
    
    state.save_all()
    return f"Equipped {item_id} to {slot}."

def unequip_item(slot: Literal["main_hand", "off_hand", "armor"], campaign_id: str = "default") -> str:
    """Unequips an item from a specific slot."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char:
        return "Error: No character."
    
    if slot == "main_hand":
        char.inventory.equipped.main_hand = None
    elif slot == "off_hand":
        char.inventory.equipped.off_hand = None
    elif slot == "armor":
        char.inventory.equipped.armor = None
        
    state.save_all()
    return f"Unequipped {slot}."

def add_gold(amount: int, campaign_id: str = "default") -> str:
    """Adds gold to the character's inventory."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "Error: No character."
    
    char.inventory.gold += amount
    state.save_all()
    return f"Added {amount} gold. Total: {char.inventory.gold} gp."

def remove_gold(amount: int, campaign_id: str = "default") -> str:
    """Removes gold from the character's inventory."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "Error: No character."
    
    if char.inventory.gold < amount:
        return f"Not enough gold! Current: {char.inventory.gold} gp."
    
    char.inventory.gold -= amount
    state.save_all()
    return f"Spent {amount} gold. Remaining: {char.inventory.gold} gp."
