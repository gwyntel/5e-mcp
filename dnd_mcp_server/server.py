from fastmcp import FastMCP
from typing import Literal, List, Dict, Any, Optional

# Import Tools with absolute imports
from dnd_mcp_server.tools.dice import roll_dice, roll_initiative
from dnd_mcp_server.tools.character import (
    get_character_sheet, update_hp, update_stat, add_experience,
    use_hit_dice, manage_conditions,
    calculate_ac, calculate_modifier, get_proficiency_bonus, create_character
)
from dnd_mcp_server.tools.inventory import get_inventory, items_add, remove_item, equip_item, unequip_item, add_gold, remove_gold
from dnd_mcp_server.tools.combat import start_combat, roll_initiative_for_all, get_initiative_order, next_turn, make_attack, end_combat
from dnd_mcp_server.generators.monster import generate_monster
from dnd_mcp_server.generators.item import generate_magic_item
from dnd_mcp_server.generators.world import generate_location

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
mcp.tool()(items_add)
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
from dnd_mcp_server.tools.spells import get_spell_slots, cast_spell
# prepare_spell removed - functionality integrated into cast_spell
# use_spell_slot is removed from exposed tools per request (avail internally)
mcp.tool()(get_spell_slots)
mcp.tool()(cast_spell)

# --- Rest Tools ---
from dnd_mcp_server.tools.rest import rest
mcp.tool()(rest) # Consolidated

# --- Check & Save Tools ---
from dnd_mcp_server.tools.checks import make_check, make_death_save, stabilize_character
# make_skill_check and make_ability_check removed - consolidated into make_check
mcp.tool()(make_check)
mcp.tool()(make_death_save)
mcp.tool()(stabilize_character)

# --- Lookup Tools ---
from dnd_mcp_server.tools.lookup import lookup_monster, lookup_spell, lookup_item, get_random_monster, lookup_feat, get_spell_list
mcp.tool()(lookup_monster)
mcp.tool()(lookup_spell)
mcp.tool()(lookup_item)
mcp.tool()(get_random_monster)
mcp.tool()(lookup_feat)
mcp.tool()(get_spell_list)

# --- Generator Tools ---
# Wrappers to ensure simple JSON return
@mcp.tool()
def generator_monster_tool(
    name: str,
    type: str,  # Beast, Undead, Monstrosity, etc.
    size: str,  # Tiny, Small, Medium, Large, Huge, Gargantuan
    cr: float,
    hp: int,
    ac: int,
    speed: int,
    str: int,
    dex: int, 
    con: int,
    intelligence: int,
    wis: int,
    cha: int,
    attack_bonus: int,
    damage_dice: str,  # e.g. "1d8+2"
    damage_type: str,  # slashing, bludgeoning, piercing, poison, etc.
    alignment: str = "Unaligned",
    multiattack: Optional[int] = None,
    traits: Optional[List[Dict[str, str]]] = None,  # [{"name": "...", "description": "..."}]
    description: Optional[str] = None
) -> str:
    """
    Generates a monster with DM-specified stats. The DM must provide all mechanical details including HP, AC, ability scores, attack bonus, and damage. Use this when you need a custom creature and have designed its complete stat block. For standard monsters, use lookup_monster instead.

    Example: generator_monster_tool(
      name="Blighted Jaguar",
      type="Monstrosity", 
      size="Medium",
      cr=1.0,
      hp=25,
      ac=13,
      speed=40,
      str=14, dex=15, con=12, intelligence=3, wis=12, cha=6,
      attack_bonus=4,
      damage_dice="1d6+2",
      damage_type="slashing",
      traits=[{"name": "Blight Spores", "description": "When hit by melee attack, attacker makes DC 11 CON save or takes 1d4 poison damage"}]
    )
    """
    from dnd_mcp_server.generators.monster import assemble_monster
    m = assemble_monster(
        name=name, type=type, size=size, cr=cr, hp=hp, ac=ac, speed=speed,
        str_val=str, dex_val=dex, con_val=con, intelligence_val=intelligence, wis_val=wis, cha_val=cha,
        attack_bonus=attack_bonus, damage_dice=damage_dice, damage_type=damage_type,
        alignment=alignment, multiattack=multiattack, traits=traits, description=description
    )
    return m.model_dump_json(indent=2)

@mcp.tool()
def generator_item_tool(
    name: str,
    type: str,  # Weapon, Armor, Wondrous Item, Potion, Scroll, Ring, etc.
    rarity: str,  # Common, Uncommon, Rare, Very Rare, Legendary, Artifact
    requires_attunement: bool = False,
    
    # If weapon:
    weapon_damage: Optional[str] = None,  # "1d8"
    weapon_damage_type: Optional[str] = None,  # slashing, piercing, bludgeoning
    weapon_properties: Optional[List[str]] = None,  # ["finesse", "light", "versatile"]
    
    # If armor:
    armor_ac: Optional[int] = None,
    armor_type: Optional[str] = None,  # light, medium, heavy, shield
    
    # Magical properties:
    bonus: Optional[int] = None,  # +1, +2, +3 for weapons/armor
    magical_effect: Optional[str] = None,  # Description of special ability
    charges: Optional[int] = None,  # If it has limited uses
    
    description: Optional[str] = None
) -> str:
    """
    Creates a magic item with DM-specified properties. The DM must define all mechanical effects including bonuses, damage, charges, and special abilities. Follow rarity guidelines for balance.

    Example: generator_item_tool(
      name="Serpent's Fang Dagger",
      type="Weapon",
      rarity="Uncommon",
      requires_attunement=False,
      weapon_damage="1d4",
      weapon_damage_type="piercing",
      weapon_properties=["finesse", "light"],
      bonus=1,
      magical_effect="On hit, target must make DC 11 CON save or take 1d4 poison damage",
      description="A curved dagger with a green-tinted blade"
    )
    """
    from dnd_mcp_server.generators.item import assemble_item
    i = assemble_item(
        name=name,
        type=type,
        rarity=rarity,
        requires_attunement=requires_attunement,
        weapon_damage=weapon_damage,
        weapon_damage_type=weapon_damage_type,
        weapon_properties=weapon_properties,
        armor_ac=armor_ac,
        armor_type=armor_type,
        bonus=bonus,
        magical_effect=magical_effect,
        charges=charges,
        description=description
    )
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
from dnd_mcp_server.tools.session import load_session_history, save_session_summary
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
