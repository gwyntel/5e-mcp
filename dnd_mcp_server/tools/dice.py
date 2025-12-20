import random
import re
from typing import Dict, Any, Union

def roll_dice(expression: str, advantage: bool = False, disadvantage: bool = False) -> str:
    """
    Roll D&D dice expressions like '2d6+4' with optional advantage/disadvantage.
    Example: roll_dice("1d20+3", True) rolls d20+3 with advantage.
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
    Roll d20 + Dexterity modifier for combat initiative order.
    Example: roll_initiative(2, True) rolls initiative with +2 Dex mod and advantage.
    """
    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)
    
    final_roll = roll1
    if advantage:
        final_roll = max(roll1, roll2)
    
    return final_roll + dex_mod
