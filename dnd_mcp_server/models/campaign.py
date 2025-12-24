from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Session(BaseModel):
    session_number: int
    date: datetime
    dramatic_moments: List[str]
    character_feelings: str
    cliffhanger: Optional[str] = None
    narrative_summary: str
    world_changes: List[str]

class LocationState(BaseModel):
    name: str
    type: str
    description: str
    status: Dict[str, bool] = Field(default_factory=lambda: {"discovered": False, "visited": False, "cleared": False})
    npcs_present: List[str] = []
    threats: List[str] = []
    features: List[str] = []

class NPCState(BaseModel):
    name: str
    race: str
    descriptor: str
    relationship: str
    location: str
    role: str
    first_met: int
    last_seen: int
    memorable_moments: List[str] = []
    personality: str
    wants: Optional[str] = None
    owes: Optional[str] = None

class FactionState(BaseModel):
    name: str
    description: str
    relationship: str
    notable_members: List[str] = []

class WorldState(BaseModel):
    locations: Dict[str, LocationState] = {}
    npcs: Dict[str, NPCState] = {}
    factions: Dict[str, FactionState] = {}

class QuestState(BaseModel):
    name: str
    type: str
    giver: str
    why_pc_cares: str
    objective: str
    next_step: str
    status: Literal['active', 'completed', 'failed', 'abandoned']
    progress_notes: List[str] = []
    locations_involved: List[str] = []
    npcs_involved: List[str] = []
    started_session: int
    completed_session: Optional[int] = None

class MysteryState(BaseModel):
    question: str
    clues_found: List[str] = []
    solved: bool = False
    solution: Optional[str] = None

class StoryState(BaseModel):
    quests: Dict[str, QuestState] = {}
    mysteries: Dict[str, MysteryState] = {}
    active_hooks: List[str] = []
    unresolved_questions: List[str] = []
    promises_made: List[str] = []

class CampaignState(BaseModel):
    campaign_id: str
    campaign_name: str
    current_session: int = 1
    last_updated: datetime = Field(default_factory=datetime.now)
    character_id: str
    sessions: List[Session] = []
    world: WorldState = Field(default_factory=WorldState)
    story: StoryState = Field(default_factory=StoryState)
