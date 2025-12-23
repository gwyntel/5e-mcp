from typing import Literal
from dnd_mcp_server.persistence.state import get_game_state
from dnd_mcp_server.tools.dice import roll_dice
import random

def make_check(check_type: Literal["skill", "ability"], skill_or_ability: str, dc: int = 10, advantage: bool = False, campaign_id: str = "default") -> str:
    """
    Roll d20 + modifiers for skill or ability check vs Difficulty Class.
    Example: make_check("skill", "athletics", 15) rolls Athletics check DC 15.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."

    # Map 'int' to 'intelligence' due to Pydantic alias
    stat_mapping = {"int": "intelligence"}

    if check_type == "skill":
        # 1. Get Modifier for skill
        # Map skill to ability
        skill_ability_map = {
            "athletics": "str",
            "acrobatics": "dex", "sleight_of_hand": "dex", "stealth": "dex",
            "arcana": "int", "history": "int", "investigation": "int", "nature": "int", "religion": "int",
            "animal_handling": "wis", "insight": "wis", "medicine": "wis", "perception": "wis", "survival": "wis",
            "deception": "cha", "intimidation": "cha", "performance": "cha", "persuasion": "cha"
        }

        ability = skill_ability_map.get(skill_or_ability.lower())
        if not ability:
            return f"Unknown skill '{skill_or_ability}'. Use check_type='ability' for raw stats."

        actual_ability = stat_mapping.get(ability, ability)
        base_mod = getattr(char.stats, actual_ability, 10)
        mod = (base_mod - 10) // 2

        # Add proficiency if proficient
        prof_bonus = getattr(char.skills, skill_or_ability.lower(), None)
        # The models/character.py schema says skills are Optional[int].
        # If set, it's *total bonus*? Or just proficiency flag?
        # "athletics": 5 implies total bonus.
        # If user model stores TOTAL bonus in skills, we just use that.
        # If it stores *proficiency* (like a boolean), we calculate.
        # The prompt says: "athletics": 5 ... # Proficient only". This implies value IS the bonus.

        total_bonus = prof_bonus if prof_bonus is not None else mod

        # 2. Roll
        expression = f"1d20+{total_bonus}"
        result = roll_dice(expression, advantage=advantage)

        return f"Skill Check ({skill_or_ability.title()}): {result} (DC {dc})"

    elif check_type == "ability":
        # Raw ability check
        actual_stat = stat_mapping.get(skill_or_ability.lower(), skill_or_ability.lower())
        score = getattr(char.stats, actual_stat, 10)
        mod = (score - 10) // 2

        expression = f"1d20+{mod}"
        result = roll_dice(expression, advantage=advantage)
        return f"Ability Check ({skill_or_ability.upper()}): {result} (DC {dc})"

    else:
        return f"Invalid check_type '{check_type}'. Use 'skill' or 'ability'."

def make_death_save(campaign_id: str = "default") -> str:
    """
    Roll death saving throw when at 0 HP. Tracks successes (3=stable) and failures (3=dead).
    Example: make_death_save() returns "Death Save Roll: 18. Success."
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
    Stabilize dying character (0 HP), resetting death save failures to 0.
    Example: stabilize_character() returns "Character stabilized. Death saves reset."
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    char.health.death_saves.successes = 0
    char.health.death_saves.failures = 0
    state.save_all()
    return "Character stabilized. Death saves reset."
