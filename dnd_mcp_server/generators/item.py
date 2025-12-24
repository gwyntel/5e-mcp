import uuid
from typing import Optional, List, Dict, Any
from dnd_mcp_server.models.item import Item, ItemIdentity, WeaponData, ArmorData, MagicProperties

def generate_magic_item(rarity: str, concept: str) -> Item:
    """Generates a random magic item based on rarity and concept."""
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    return Item(
        id=item_id,
        identity=ItemIdentity(
            name=f"{rarity} {concept}",
            type="Wondrous Item",
            rarity=rarity
        ),
        description=f"A {rarity.lower()} item that embodies {concept}.",
        value_gp=500.0,
        weight=1.0,
        magic_properties=MagicProperties(effect=f"This item embodies the concept of {concept}.")
    )

def assemble_item(
    name: str,
    type: str,
    rarity: str,
    requires_attunement: bool = False,
    weapon_damage: Optional[str] = None,
    weapon_damage_type: Optional[str] = None,
    weapon_properties: Optional[List[str]] = None,
    armor_ac: Optional[int] = None,
    armor_type: Optional[str] = None,
    bonus: Optional[int] = None,
    magical_effect: Optional[str] = None,
    charges: Optional[int] = None,
    description: Optional[str] = None
) -> Item:
    """Assembles an Item object from specified parameters."""
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    
    identity = ItemIdentity(
        name=name,
        type=type,
        rarity=rarity,
        requires_attunement=requires_attunement
    )
    
    weapon_data = None
    if type.lower() == "weapon" and weapon_damage and weapon_damage_type:
        weapon_data = WeaponData(
            damage=weapon_damage,
            damage_type=weapon_damage_type,
            properties=weapon_properties or [],
            bonus=bonus or 0
        )
    
    armor_data = None
    if type.lower() == "armor" and armor_ac is not None:
        # Determine dex bonus max based on armor type
        dex_max = None
        if armor_type:
            at = armor_type.lower()
            if "medium" in at:
                dex_max = 2
            elif "heavy" in at:
                dex_max = 0
            elif "shield" in at:
                dex_max = 0
        
        armor_data = ArmorData(
            ac_base=armor_ac,
            dex_bonus_max=dex_max
        )
    
    magic_props = None
    if magical_effect or charges is not None or (bonus and type.lower() not in ["weapon", "armor"]):
        magic_props = MagicProperties(
            effect=magical_effect or (f"+{bonus} bonus" if bonus else "Magical"),
            charges=charges
        )
    
    return Item(
        id=item_id,
        identity=identity,
        description=description or f"A {rarity.lower()} {type.lower()}.",
        value_gp=0.0, # Defaulting for now as it's not in the tool signature
        weight=1.0,  # Defaulting for now
        weapon_data=weapon_data,
        armor_data=armor_data,
        magic_properties=magic_props
    )
