from typing import Dict, Any, Optional
from ..persistence.state import get_game_state
from ..models.character import Condition

def get_spell_slots(campaign_id: str = "default") -> Dict[str, Any]:
    """Returns available spell slots."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char or not char.spellcasting:
        return {"error": "No spellcasting ability."}
    return {k: v.model_dump() for k, v in char.spellcasting.slots.items()}

def use_spell_slot(level: int, campaign_id: str = "default") -> str:
    """Consumes a spell slot of the given level."""
    state = get_game_state(campaign_id)
    char = state.character
    if not char or not char.spellcasting:
        return "Error: No spellcasting ability."
        
    lvl_str = str(level)
    if lvl_str not in char.spellcasting.slots:
        return f"Error: No slots of level {level}."
        
    slot = char.spellcasting.slots[lvl_str]
    if slot.current > 0:
        slot.current -= 1
        state.save_all()
        return f"Used level {level} slot. Remaining: {slot.current}/{slot.max}."
    else:
        return f"Error: No level {level} slots remaining."

def prepare_spell(spell_name: str, campaign_id: str = "default") -> str:
    """
    Adds a spell to the list of prepared spells. 
    Functionally, this validates if the spell is known/available.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char or not char.spellcasting:
        return "Error: No spellcasting ability."

    if spell_name not in char.spellcasting.prepared:
        char.spellcasting.prepared.append(spell_name)
        state.save_all()
        return f"Prepared spell: {spell_name}."
    return f"Spell {spell_name} is already prepared."

def cast_spell(spell_name: str, level: int, concentration: bool = False, campaign_id: str = "default") -> str:
    """
    Casts a spell, consuming a slot. 
    Handles concentration tracking.
    """
    # 1. Consume slot
    # (Cantrips level 0 don't consume)
    msg = ""
    if level > 0:
        res = use_spell_slot(level, campaign_id=campaign_id)
        if "Error" in res:
            return res
        msg += res + "\n"
        
    # 2. Check prep (optional rule enforcement)
    state = get_game_state(campaign_id)
    char = state.character
    
    # Simple check: If prepared list is not empty, assume we are tracking prep.
    # If empty, maybe they are a known caster (Bard) or haven't set it up.
    # We'll enforce only if they have > 0 prepared spells, implying usage.
    if char and char.spellcasting and char.spellcasting.prepared:
        # fuzzy match
        known = any(s.lower() == spell_name.lower() for s in char.spellcasting.prepared)
        if not known:
            return f"Error: Spell '{spell_name}' is not prepared."
    
    # 3. Handle Concentration
    if concentration:
        # Check existing
        # Simplified: Check conditions for "Concentrating"
        existing = next((c for c in char.conditions if c.name.startswith("Concentrating")), None)
        if existing:
            char.conditions.remove(existing)
            msg += f"Dropped concentration on {existing.name.split(': ')[1]}.\n"
            
        new_cond = Condition(
            name=f"Concentrating: {spell_name}",
            duration=10, 
            unit="minutes"
        )
        char.conditions.append(new_cond)
        msg += f"Now concentrating on {spell_name}."
        
    state.save_all()
    return f"{msg} Cast {spell_name} at level {level}."
