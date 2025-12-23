from typing import Dict, Any, Optional
from dnd_mcp_server.persistence.state import get_game_state
from dnd_mcp_server.models.character import Condition

def get_spell_slots(campaign_id: str = "default") -> Dict[str, Any]:
    """
    Get available spell slots by level with current/max usage.
    Example: get_spell_slots() returns {"1": {"current": 2, "max": 4}, "2": {...}}
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char or not char.spellcasting:
        return {"error": "No spellcasting ability."}
    return {k: v.model_dump() for k, v in char.spellcasting.slots.items()}

def use_spell_slot(level: int, campaign_id: str = "default") -> str:
    """
    Consume one spell slot of specified level for casting.
    Example: use_spell_slot(2) consumes one level 2 spell slot.
    """
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
    Add spell to prepared spells list for classes that require preparation.
    Example: prepare_spell("Fireball") adds Fireball to prepared spells.
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

def cast_spell(spell_name: str, level: int, concentration: bool = False, prepare: bool = False, campaign_id: str = "default") -> str:
    """
    Cast spell consuming slot, handling concentration and optional preparation.
    Example: cast_spell("Fireball", 3, True) casts Fireball with concentration.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char or not char.spellcasting:
        return "Error: No spellcasting ability."
    
    # 1. Prepare spell if requested
    if prepare:
        if spell_name not in char.spellcasting.prepared:
            char.spellcasting.prepared.append(spell_name)
    
    # 2. Consume slot
    # (Cantrips level 0 don't consume)
    msg = ""
    if level > 0:
        res = use_spell_slot(level, campaign_id=campaign_id)
        if "Error" in res:
            return res
        msg += res + "\n"
        
    # 3. Check prep (optional rule enforcement)
    # Simple check: If prepared list is not empty, assume we are tracking prep.
    # If empty, maybe they are a known caster (Bard) or haven't set it up.
    # We'll enforce only if they have > 0 prepared spells, implying usage.
    if char.spellcasting.prepared:
        # fuzzy match
        known = any(s.lower() == spell_name.lower() for s in char.spellcasting.prepared)
        if not known:
            return f"Error: Spell '{spell_name}' is not prepared. Use prepare=True to prepare it first."
    
    # 4. Handle Concentration
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
