from typing import List, Optional, Dict, Literal
from pydantic import BaseModel

class MonsterIdentity(BaseModel):
    name: str
    type: str
    size: str
    alignment: str
    cr: float

class MonsterStats(BaseModel):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int

class MonsterHitDice(BaseModel):
    d4: Optional[int] = None
    d6: Optional[int] = None
    d8: Optional[int] = None
    d10: Optional[int] = None
    d12: Optional[int] = None
    d20: Optional[int] = None

class MonsterHealth(BaseModel):
    current_hp: int
    max_hp: int
    hit_dice: MonsterHitDice

class MonsterDefense(BaseModel):
    ac: int
    speed: int

class MonsterAction(BaseModel):
    name: str
    type: Literal["melee_weapon", "ranged_weapon", "ability", "spell"]
    attack_bonus: Optional[int] = None
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    range: Optional[str] = None
    description: Optional[str] = None # For abilities that format differently

class MonsterOffense(BaseModel):
    actions: List[MonsterAction] = []
    multiattack: Optional[str] = None

class MonsterTrait(BaseModel):
    name: str
    description: str

class Monster(BaseModel):
    id: str
    identity: MonsterIdentity
    stats: MonsterStats
    health: MonsterHealth
    defense: MonsterDefense
    offense: MonsterOffense
    traits: List[MonsterTrait] = []
    loot: List[str] = []
