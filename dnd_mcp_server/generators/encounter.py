from typing import List, Dict
from ..models.monster import Monster
from .monster import generate_monster

def calculate_encounter_difficulty(player_level: int, total_monster_cr: float) -> str:
    """Evaluate difficulty for a SOLO player (buffed/heroic)."""
    # Standard 5e: CR = Level/4 is medium for 1 PC.
    # Solo Spec: CR = Level is Hard/Deadly but playable with 4x multiplier logic.
    # We'll assume the Player is capable of taking on CRs close to their level.
    
    ratio = total_monster_cr / max(1, player_level)
    
    # Example: Level 4 vs CR 3 (Ratio 0.75) -> "Hard" in example?
    # Spec says "Level 4 'hard' -> CR 3-4".
    # So Ratio 0.75 - 1.0 is Hard.
    
    if ratio < 0.25: return "Trivial"
    if ratio < 0.5: return "Easy"
    if ratio < 0.8: return "Medium"
    if ratio <= 1.2: return "Hard"
    return "Deadly"

def suggest_encounter(player_level: int, difficulty: str) -> List[Monster]:
    """
    Creates a list of monsters balanced for solo play.
    """
    # Logic based on Example: Level 4 -> Hard -> CR 3-4.
    target_cr = player_level # Default to CR = Level roughly
    
    if difficulty.lower() == "easy": target_cr = player_level * 0.3
    elif difficulty.lower() == "medium": target_cr = player_level * 0.6
    elif difficulty.lower() == "hard": target_cr = player_level * 0.9
    elif difficulty.lower() == "deadly": target_cr = player_level * 1.2
    
    target_cr = max(0.125, target_cr)
    
    # Limit to appropriate float range
    # generate_monster accepts float CR
    
    mob = generate_monster("Random Creature", target_cr)
    return [mob]
