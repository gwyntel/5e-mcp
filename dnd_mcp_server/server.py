from fastmcp import FastMCP
from typing import Literal, List, Dict, Any

# Import Tools
from .tools.dice import roll_dice, roll_initiative
from .tools.character import (
    get_character_sheet, update_hp, update_stat, add_experience,
    use_hit_dice, manage_conditions,
    calculate_ac, calculate_modifier, get_proficiency_bonus, create_character
)
from .tools.inventory import get_inventory, add_item, remove_item, equip_item, unequip_item, add_gold, remove_gold
from .tools.combat import start_combat, roll_initiative_for_all, get_initiative_order, next_turn, make_attack, end_combat
from .generators.monster import generate_monster
from .generators.item import generate_magic_item
from .generators.world import generate_location

# Initialize FastMCP server
mcp = FastMCP("Solo D&D 5e Server")

# --- Dice Tools ---
mcp.tool()(roll_dice)
mcp.tool()(roll_initiative)

# --- Character Tools ---
mcp.tool()(get_character_sheet)
mcp.tool()(create_character)
mcp.tool()(update_hp) # Consolidated with deal_damage
mcp.tool()(use_hit_dice)
mcp.tool()(manage_conditions) # Consolidated
mcp.tool()(update_stat)
mcp.tool()(add_experience) # Level-up detection integrated
mcp.tool()(calculate_ac)
mcp.tool()(calculate_modifier)
mcp.tool()(get_proficiency_bonus)

# --- Inventory Tools ---
mcp.tool()(get_inventory)
mcp.tool()(add_item)
mcp.tool()(remove_item)
mcp.tool()(equip_item)
mcp.tool()(unequip_item)
mcp.tool()(add_gold)
mcp.tool()(remove_gold)

# --- Combat Tools ---
mcp.tool()(start_combat)
mcp.tool()(roll_initiative_for_all)
mcp.tool()(get_initiative_order)
mcp.tool()(next_turn)
mcp.tool()(make_attack)
# deal_damage removed - consolidated into update_hp
mcp.tool()(end_combat)

# --- Spellcasting Tools ---
from .tools.spells import get_spell_slots, cast_spell
# prepare_spell removed - functionality integrated into cast_spell
# use_spell_slot is removed from exposed tools per request (avail internally)
mcp.tool()(get_spell_slots)
mcp.tool()(cast_spell)

# --- Rest Tools ---
from .tools.rest import rest
mcp.tool()(rest) # Consolidated

# --- Check & Save Tools ---
from .tools.checks import make_check, make_death_save, stabilize_character
# make_skill_check and make_ability_check removed - consolidated into make_check
mcp.tool()(make_check)
mcp.tool()(make_death_save)
mcp.tool()(stabilize_character)

# --- Lookup Tools ---
from .tools.lookup import lookup_monster, lookup_spell, lookup_item, get_random_monster, lookup_feat, get_spell_list
mcp.tool()(lookup_monster)
mcp.tool()(lookup_spell)
mcp.tool()(lookup_item)
mcp.tool()(get_random_monster)
mcp.tool()(lookup_feat)
mcp.tool()(get_spell_list)

# --- Generator Tools ---
# Wrappers to ensure simple JSON return
@mcp.tool()
def generator_monster_tool(concept: str, target_cr: float) -> str:
    """
    Generates a unique monster stat block based on a concept and Target CR. 
    Returns the full JSON model. Use this when you need a custom foe not found in the standard list.
    """
    m = generate_monster(concept, target_cr)
    return m.model_dump_json(indent=2)

@mcp.tool()
def generator_item_tool(rarity: str, concept: str) -> str:
    """
    Generates a unique magic item with mechanics based on a rarity and concept. 
    Returns the full JSON model.
    """
    i = generate_magic_item(rarity, concept)
    return i.model_dump_json(indent=2)

@mcp.tool()
def generator_location_tool(type: str, difficulty: str) -> str:
    """
    Generates a detailed location with description, sensory details, and potential encounters. 
    Returns the full JSON model.
    """
    l = generate_location(type, difficulty)
    return l.model_dump_json(indent=2)


# --- Session Tools ---
from .tools.session import load_session_history, save_session_summary
mcp.tool()(load_session_history)
mcp.tool()(save_session_summary)

# --- Prompts ---
@mcp.prompt()
def dnd_dm() -> str:
    """System prompt for running a D&D 5e solo campaign"""
    # Load from system_prompt.md usually, or inline it. 
    # Since we have the file, let's read it.
    import os
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            return f.read()
    return "Error: system_prompt.md not found."


if __name__ == "__main__":
    mcp.run()
