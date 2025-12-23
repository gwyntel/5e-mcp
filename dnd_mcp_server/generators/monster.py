import random
import uuid
from dnd_mcp_server.models.monster import Monster, MonsterIdentity, MonsterStats, MonsterHealth, MonsterDefense, MonsterOffense, MonsterAction
# from dnd_mcp_server.models.monster import MonsterHitDice 

# Simplified CR Table (AC, HP, Attack, Damage)
CR_TABLE = {
    0.25: {"ac": 13, "hp": 15, "to_hit": 3, "dmg": 5},
    0.5:  {"ac": 13, "hp": 25, "to_hit": 4, "dmg": 8},
    1:    {"ac": 13, "hp": 40, "to_hit": 5, "dmg": 12},
    2:    {"ac": 13, "hp": 60, "to_hit": 5, "dmg": 18},
    3:    {"ac": 14, "hp": 80, "to_hit": 5, "dmg": 24},
    4:    {"ac": 14, "hp": 100, "to_hit": 6, "dmg": 30},
    5:    {"ac": 15, "hp": 120, "to_hit": 7, "dmg": 36},
}

def generate_monster(concept: str, target_cr: float) -> Monster:
    """
    Generates a monster stat block based on CR table.
    """
    # Find closest CR
    cached_stats = CR_TABLE.get(target_cr)
    if not cached_stats:
        # Fallback to closest
        cached_stats = CR_TABLE[1] # Default
        
    mob_id = f"mob_{uuid.uuid4().hex[:8]}"
    
    # Construct Monster
    m = Monster(
        id=mob_id,
        identity=MonsterIdentity(
            name=f"{concept} (CR {target_cr})",
            type="Unknown",
            size="Medium",
            alignment="Unaligned",
            cr=target_cr
        ),
        stats=MonsterStats(str=10, dex=10, con=10, int=10, wis=10, cha=10),
        health=MonsterHealth(
            current_hp=cached_stats["hp"],
            max_hp=cached_stats["hp"],
            hit_dice={"d8": int(cached_stats["hp"]/4)} # rough approx
        ),
        defense=MonsterDefense(
            ac=cached_stats["ac"],
            speed=30
        ),
        offense=MonsterOffense(
            actions=[
                MonsterAction(
                    name="Attack",
                    type="melee_weapon",
                    attack_bonus=cached_stats["to_hit"],
                    damage=f"1d8+{cached_stats['dmg']-4}", # rough math
                    damage_type="physical"
                )
            ]
        )
    )
    return m
