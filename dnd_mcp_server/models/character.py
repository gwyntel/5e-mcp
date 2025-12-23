from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class CharacterIdentity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    race: str
    class_: str
    background: str
    level: int = 1
    xp: int = 0

class AbilityScores(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    str: int
    dex: int
    con: int
    intelligence: int = Field(alias="int")
    wis: int
    cha: int
    proficiency_bonus: int = 2

class HitDice(BaseModel):
    max: int
    current: int

class DeathSaves(BaseModel):
    successes: int = 0
    failures: int = 0

class HitDiceStore(BaseModel):
    d6: Optional[HitDice] = None
    d8: Optional[HitDice] = None
    d10: Optional[HitDice] = None
    d12: Optional[HitDice] = None

class Health(BaseModel):
    current_hp: int
    max_hp: int
    temp_hp: int = 0
    hit_dice: HitDiceStore
    death_saves: DeathSaves = Field(default_factory=DeathSaves)

class Saves(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    str: Optional[int] = None
    dex: Optional[int] = None
    con: Optional[int] = None
    intelligence: Optional[int] = Field(alias="int", default=None)
    wis: Optional[int] = None
    cha: Optional[int] = None

class Defense(BaseModel):
    ac: int
    initiative_mod: int
    speed: int
    saves: Saves

class Attack(BaseModel):
    name: str
    bonus: int
    damage: str
    type: str

class Combat(BaseModel):
    weapon_proficiencies: List[str] = []
    attacks: List[Attack] = []

class Skills(BaseModel):
    # Mapping skill name to bonus. Only proficient skills need be listed usually, 
    # but we can store all if we want. Design says "Proficient only" usually.
    athletics: Optional[int] = None
    acrobatics: Optional[int] = None
    sleight_of_hand: Optional[int] = None
    stealth: Optional[int] = None
    arcana: Optional[int] = None
    history: Optional[int] = None
    investigation: Optional[int] = None
    nature: Optional[int] = None
    religion: Optional[int] = None
    animal_handling: Optional[int] = None
    insight: Optional[int] = None
    medicine: Optional[int] = None
    perception: Optional[int] = None
    survival: Optional[int] = None
    deception: Optional[int] = None
    intimidation: Optional[int] = None
    performance: Optional[int] = None
    persuasion: Optional[int] = None

class SpellSlot(BaseModel):
    max: int
    current: int

class Spellcasting(BaseModel):
    ability: Optional[Literal["str", "dex", "con", "int", "wis", "cha"]] = None
    spell_dc: Optional[int] = None
    spell_attack: Optional[int] = None
    slots: Dict[str, SpellSlot] = {}
    prepared: List[str] = []

class EquippedItems(BaseModel):
    main_hand: Optional[str] = None
    off_hand: Optional[str] = None
    armor: Optional[str] = None

class Inventory(BaseModel):
    items: List[str] = []
    equipped: EquippedItems
    gold: float = 0
    weight: float = 0
    max_capacity: float

class Condition(BaseModel):
    name: str
    duration: int
    unit: str = "rounds"
    level: Optional[int] = None

class FeatureUsage(BaseModel):
    uses: int
    max: int
    resets_on: Literal["short_rest", "long_rest"]

class Character(BaseModel):
    id: str
    identity: CharacterIdentity
    stats: AbilityScores
    health: Health
    defense: Defense
    combat: Combat
    skills: Skills
    spellcasting: Optional[Spellcasting] = None
    inventory: Inventory
    conditions: List[Condition] = []
    features: Dict[str, FeatureUsage] = {}
