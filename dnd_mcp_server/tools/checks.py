from ..persistence.state import get_game_state
from .dice import roll_dice
import random

def make_skill_check(skill: str, dc: int = 10, advantage: bool = False, campaign_id: str = "default") -> str:
    """
    Rolls a Skill Check (d20 + Ability Mod + Proficiency). 
    Use this when the player attempts an action like 'climbing', 'persuading', or 'hiding'.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    # 1. Get Modifier
    # Map skill to ability
    skill_ability_map = {
        "athletics": "str",
        "acrobatics": "dex", "sleight_of_hand": "dex", "stealth": "dex",
        "arcana": "int", "history": "int", "investigation": "int", "nature": "int", "religion": "int",
        "animal_handling": "wis", "insight": "wis", "medicine": "wis", "perception": "wis", "survival": "wis",
        "deception": "cha", "intimidation": "cha", "performance": "cha", "persuasion": "cha"
    }
    
    ability = skill_ability_map.get(skill.lower())
    if not ability:
        return f"Unknown skill '{skill}'. Use make_ability_check for raw stats."
        
    base_mod = getattr(char.stats, ability, 10)
    mod = (base_mod - 10) // 2
    
    # Add proficiency if proficient
    prof_bonus = getattr(char.skills, skill.lower(), None)
    # The models/character.py schema says skills are Optional[int]. 
    # If set, it's the *total bonus*? Or just the proficiency flag?
    # "athletics": 5 implies total bonus. 
    # If the user model stores the TOTAL bonus in skills, we just use that.
    # If it stores *proficiency* (like a boolean), we calculate.
    # The prompt says: "athletics: 5 ... # Proficient only". This implies the value IS the bonus.
    
    total_bonus = prof_bonus if prof_bonus is not None else mod
    
    # 2. Roll
    expression = f"1d20+{total_bonus}"
    result = roll_dice(expression, advantage=advantage)
    
    # We can append "vs DC {dc}" if we want, but roll_dice returns a string.
    # We assume the user reads the result.
    return f"Skill Check ({skill.title()}): {result} (DC {dc})"

def make_ability_check(ability: str, dc: int = 10, advantage: bool = False, campaign_id: str = "default") -> str:
    """
    Rolls a raw Ability Check (d20 + Ability Mod). 
    Use this for attributes without specific skills (e.g. Strength check to break a door).
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    score = getattr(char.stats, ability.lower(), 10)
    mod = (score - 10) // 2
    
    expression = f"1d20+{mod}"
    result = roll_dice(expression, advantage=advantage)
    return f"Ability Check ({ability.upper()}): {result} (DC {dc})"

def make_death_save(campaign_id: str = "default") -> str:
    """
    Rolls a Death Saving Throw. Automatically tracks successes (3 = stable) and failures (3 = dead). 
    Handles critical successes (revive to 1 HP) and critical failures (2 fails).
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    if char.health.current_hp > 0:
        return "Character is not unconscious (HP > 0)."
        
    roll = random.randint(1, 20)
    msg = f"Death Save Roll: {roll}. "
    
    if roll == 1:
        char.health.death_saves.failures += 2
        msg += "CRITICAL FAILURE! (2 failures added)."
    elif roll == 20:
        char.health.current_hp = 1
        char.health.death_saves.failures = 0
        char.health.death_saves.successes = 0
        msg += "CRITICAL SUCCESS! You regain 1 HP and consciousness!"
        state.save_all()
        return msg
    elif roll >= 10:
        char.health.death_saves.successes += 1
        msg += "Success."
    else:
        char.health.death_saves.failures += 1
        msg += "Failure."
        
    # Check status
    if char.health.death_saves.successes >= 3:
        char.health.death_saves.successes = 0
        char.health.death_saves.failures = 0
        msg += " STABILIZED! (Set failures/successes to 0)"
    elif char.health.death_saves.failures >= 3:
        msg += " DEAD! Character has died."
        
    state.save_all()
    return msg

def stabilize_character(campaign_id: str = "default") -> str:
    """
    Immediately stabilizes the dying character (0 HP), resetting death save failures to 0. 
    Use when a Medicine check succeeds or Spare the Dying is cast.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    char.health.death_saves.successes = 0
    char.health.death_saves.failures = 0
    state.save_all()
    return "Character stabilized. Death saves reset."
