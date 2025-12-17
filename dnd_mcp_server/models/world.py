from typing import List, Optional, Dict
from pydantic import BaseModel

class Connection(BaseModel):
    to: str
    direction: str
    description: str
    locked: bool = False
    hidden: bool = False

class LocationIdentity(BaseModel):
    name: str
    type: str

class Location(BaseModel):
    id: str
    identity: LocationIdentity
    description: str
    connections: List[Connection] = []
    entities_present: List[str] = [] # IDs of NPCs/Monsters
    items_present: List[str] = [] # IDs of Items
    points_of_interest: List[str] = []
    metadata: Dict[str, object] = {}

class WorldState(BaseModel):
    locations: Dict[str, Location] = {}
    current_location_id: Optional[str] = None
    time_of_day: str = "Morning"
    # Basic quest tracking could live here or separate
    active_quests: List[str] = []
