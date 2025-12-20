from ..persistence.state import get_game_state
from typing import Literal

def rest(type: Literal["short", "long"], campaign_id: str = "default") -> str:
    """
    Perform short (1 hour) or long (8 hours) rest to recover resources.
    Example: rest("long") performs long rest, restoring HP and spell slots.
    """
    state = get_game_state(campaign_id)
    char = state.character
    if not char: return "No character."
    
    if type == "short":
        restored = []
        # 1. Restore Class Features
        for name, usage in char.features.items():
            if usage.resets_on == "short_rest":
                usage.uses = usage.max
                restored.append(name)
        
        state.save_all()
        msg = "Short rest complete."
        if restored:
            msg += f" Restored features: {', '.join(restored)}."
        return msg

    elif type == "long":
        # 1. HP
        char.health.current_hp = char.health.max_hp
        
        # 2. Hit Dice (recover half max)
        recovered_hd = []
        for hd_type in ["d6", "d8", "d10", "d12"]:
            hd_store = getattr(char.health.hit_dice, hd_type)
            if hd_store and hd_store.max > 0:
                recover_amt = max(1, hd_store.max // 2)
                old_curr = hd_store.current
                hd_store.current = min(hd_store.current + recover_amt, hd_store.max)
                if hd_store.current > old_curr:
                    recovered_hd.append(f"{hd_store.current - old_curr}{hd_type}")

        # 3. Spell Slots
        if char.spellcasting:
            for level, slot in char.spellcasting.slots.items():
                slot.current = slot.max
                
        # 4. Features
        for usage in char.features.values():
            usage.uses = usage.max
            
        # 5. Exhaustion
        exh = next((c for c in char.conditions if c.name.lower() == "exhaustion"), None)
        exh_msg = ""
        if exh:
            if exh.level and exh.level > 1:
                exh.level -= 1
                exh_msg = f" Exhaustion reduced to level {exh.level}."
            else:
                char.conditions.remove(exh)
                exh_msg = " Exhaustion removed."
                
        state.save_all()
        
        return (
            f"Long rest complete. HP fully restored. Spell slots reset. "
            f"Recovered Hit Dice: {', '.join(recovered_hd)}.{exh_msg}"
        )
    
    else:
        return f"Invalid rest type: {type}"
