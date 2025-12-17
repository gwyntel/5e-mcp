import random
import re
from typing import Dict, Any, Union

def roll_dice(expression: str, advantage: bool = False, disadvantage: bool = False) -> str:
    """
    Rolls any standard D&D dice expression (e.g., '2d6+4', '1d20-1'). 
    Supports 'advantage' (roll 2 take higher) and 'disadvantage' (roll 2 take lower) flags.
    """
    # Simple parser for XdY+Z
    pattern = r"(\d+)d(\d+)([\+\-]\d+)?"
    match = re.match(pattern, expression.strip())
    
    if not match:
        return f"Error: Invalid dice expression '{expression}'. Use format like '2d6+4'."
    
    count = int(match.group(1))
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    def roll_one():
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        return total, rolls
    
    if advantage and not disadvantage:
        # Roll twice, take higher
        total1, rolls1 = roll_one()
        total2, rolls2 = roll_one()
        final_total = max(total1, total2)
        used_rolls = rolls1 if total1 >= total2 else rolls2
        dropped_rolls = rolls2 if total1 >= total2 else rolls1
        
        detail = f"Rolling {expression} with Advantage:\n"
        detail += f"Roll 1: {rolls1} + {modifier} = {total1}\n"
        detail += f"Roll 2: {rolls2} + {modifier} = {total2}\n"
        detail += f"Result: **{final_total}**"
        return detail
        
    elif disadvantage and not advantage:
        # Roll twice, take lower
        total1, rolls1 = roll_one()
        total2, rolls2 = roll_one()
        final_total = min(total1, total2)
        used_rolls = rolls1 if total1 <= total2 else rolls2
        
        detail = f"Rolling {expression} with Disadvantage:\n"
        detail += f"Roll 1: {rolls1} + {modifier} = {total1}\n"
        detail += f"Roll 2: {rolls2} + {modifier} = {total2}\n"
        detail += f"Result: **{final_total}**"
        return detail
        
    else:
        # Straight roll (or adv+dis cancel)
        total, rolls = roll_one()
        return f"Rolling {expression}: {rolls} + {modifier} = **{total}**"

def roll_initiative(dex_mod: int, advantage: bool = False) -> int:
    """
    Rolls a d20 + Dex modifier for initiative tracking. Returns the raw value for sorting purposes.
    """
    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)
    
    final_roll = roll1
    if advantage:
        final_roll = max(roll1, roll2)
    
    return final_roll + dex_mod
