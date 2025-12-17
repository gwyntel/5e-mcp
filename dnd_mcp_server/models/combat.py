from typing import List, Optional, Literal
from pydantic import BaseModel

class Combatant(BaseModel):
    id: str
    name: str
    type: Literal["player", "monster", "npc"]
    initiative: int = 0
    hp: int
    max_hp: int
    ac: int
    status: str = "active" # active, unconscious, dead, fled

class CombatState(BaseModel):
    active: bool = False
    round: int = 0
    turn_index: int = 0 # Index in the turn_order list
    combatants: List[Combatant] = []
    
    @property
    def current_actor(self) -> Optional[Combatant]:
        if not self.combatants:
            return None
        return self.combatants[self.turn_index]
