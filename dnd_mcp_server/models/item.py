from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel

class ItemIdentity(BaseModel):
    name: str
    type: str
    rarity: str
    requires_attunement: bool = False

class WeaponData(BaseModel):
    damage: str
    damage_type: str
    properties: List[str] = []
    bonus: int = 0
    range: Optional[str] = None

class ArmorData(BaseModel):
    ac_base: int
    dex_bonus_max: Optional[int] = None # None means unlimited (Light armor), 0 means none (Heavy), 2 means Medium
    stealth_disadvantage: bool = False
    strength_requirement: Optional[int] = None

class MagicProperties(BaseModel):
    activation: Optional[str] = None
    effect: str
    duration: Optional[str] = None
    charges: Optional[int] = None
    recharge: Optional[str] = None

class Item(BaseModel):
    id: str
    identity: ItemIdentity
    description: str
    value_gp: float
    weight: float
    # Optional specific data depending on type
    weapon_data: Optional[WeaponData] = None
    armor_data: Optional[ArmorData] = None
    magic_properties: Optional[MagicProperties] = None
