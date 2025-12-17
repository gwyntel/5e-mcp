import json
import os
from typing import Optional, Dict

from ..models.character import Character
from ..models.world import WorldState
from ..models.item import Item
from ..models.monster import Monster
from ..models.combat import CombatState

# Constants for file paths
# Use absolute path to ensure write access and persistence location
DATA_BASE_DIR = "/Users/gwyn/projects/5e-mcp/gemini/save_data"

def get_campaign_dir(campaign_id: str) -> str:
    return os.path.join(DATA_BASE_DIR, campaign_id)

def get_file_paths(campaign_id: str):
    base = get_campaign_dir(campaign_id)
    return {
        "char": os.path.join(base, "character.json"),
        "world": os.path.join(base, "world.json"),
        "combat": os.path.join(base, "combat.json"),
        "monsters": os.path.join(base, "encounters.json"),
        "items": os.path.join(base, "items.json")
    }

def ensure_campaign_dir(campaign_id: str):
    path = get_campaign_dir(campaign_id)
    if not os.path.exists(path):
        os.makedirs(path)

# --- Character Persistence ---

# --- Character Persistence ---

def load_character(campaign_id: str) -> Optional[Character]:
    paths = get_file_paths(campaign_id)
    if not os.path.exists(paths["char"]):
        return None
    try:
        with open(paths["char"], 'r') as f:
            data = json.load(f)
        return Character(**data)
    except Exception as e:
        print(f"Error loading character for {campaign_id}: {e}")
        return None

def save_character(character: Character, campaign_id: str):
    ensure_campaign_dir(campaign_id)
    paths = get_file_paths(campaign_id)
    with open(paths["char"], 'w') as f:
        f.write(character.model_dump_json(indent=2))

# --- World Persistence ---

def load_world(campaign_id: str) -> WorldState:
    paths = get_file_paths(campaign_id)
    if not os.path.exists(paths["world"]):
        return WorldState()
    try:
        with open(paths["world"], 'r') as f:
            data = json.load(f)
        return WorldState(**data)
    except Exception as e:
        print(f"Error loading world for {campaign_id}: {e}")
        return WorldState()

def save_world(world: WorldState, campaign_id: str):
    ensure_campaign_dir(campaign_id)
    paths = get_file_paths(campaign_id)
    with open(paths["world"], 'w') as f:
        f.write(world.model_dump_json(indent=2))

# --- Combat Persistence ---

def load_combat(campaign_id: str) -> CombatState:
    paths = get_file_paths(campaign_id)
    if not os.path.exists(paths["combat"]):
        return CombatState()
    try:
        with open(paths["combat"], 'r') as f:
            data = json.load(f)
        return CombatState(**data)
    except Exception as e:
        print(f"Error loading combat for {campaign_id}: {e}")
        return CombatState()

def save_combat(combat: CombatState, campaign_id: str):
    ensure_campaign_dir(campaign_id)
    paths = get_file_paths(campaign_id)
    with open(paths["combat"], 'w') as f:
        f.write(combat.model_dump_json(indent=2))

# --- Global Game State Helper ---
# For the MVP, we can keep simple caches or re-load. 
# Robustness: Reload on every tool call to ensure consistency if manual edits happen? 
# Or keep in memory. Design says "Every session resumes", implies disk is truth.
# But for tool performance, we might want to keep in memory and write on change.

class GameState:
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.character: Optional[Character] = load_character(campaign_id)
        self.world: WorldState = load_world(campaign_id)
        self.combat: CombatState = load_combat(campaign_id)
        
    def save_all(self):
        if self.character:
            save_character(self.character, self.campaign_id)
        save_world(self.world, self.campaign_id)
        save_combat(self.combat, self.campaign_id)

# Cache of GameStates by campaign_id
_game_state_cache: Dict[str, GameState] = {}

def get_game_state(campaign_id: str = "default") -> GameState:
    global _game_state_cache
    if campaign_id not in _game_state_cache:
        # Load logic specific to this campaign
        _game_state_cache[campaign_id] = GameState(campaign_id)
        
    return _game_state_cache[campaign_id]
