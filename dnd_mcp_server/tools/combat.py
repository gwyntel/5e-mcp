from typing import List, Dict, Any, Optional
import random
from dnd_mcp_server.storage.game_state import get_game_state
from dnd_mcp_server.models.combat import Combatant, CombatState
from dnd_mcp_server.tools.dice import roll_initiative, roll_dice

from dnd_mcp_server.tools.lookup import get_monster_data

async def start_combat(entities: List[str], campaign_id: str = "default") -> str:
    """
    Start combat with specified monsters. Initializes combat state and adds combatants.
    Example: start_combat(["Goblin", "2 Wolves"]) begins combat with 1 goblin and 2 wolves.
    """
    state = get_game_state(campaign_id)
    combat = await state.combat
    if combat.active:
        return "Combat already active. End current combat first."
    
    combat.active = True
    combat.round = 1
    combat.combatants = []
    
    # Add Player
    if await state.character:
        char = await state.character
        pc = Combatant(
            id=char.id,
            name=char.identity.name,
            type="player",
            hp=char.health.current_hp,
            max_hp=char.health.max_hp,
            ac=char.defense.ac
        )
        combat.combatants.append(pc)
    
    existing_ids = {c.id for c in combat.combatants}
    
    for entity_ref in entities:
        # Check if it's the player ID (skip)
        if await state.character and entity_ref == state.character.id: 
            continue
            
        # Unique ID handling
        mob_id = entity_ref
        while mob_id in existing_ids:
             mob_id += "_1"
        existing_ids.add(mob_id)

        # Lookup data
        data = get_monster_data(entity_ref) # Try using name
        
        if data:
            # Parse HP/AC
            hp = data.get("hit_points", 10)
            ac = data.get("armor_class", 10)
            name = data.get("name", entity_ref)
            # We could store attacks here if Combatant supported it
        else:
            # Fallback
            hp, ac, name = 10, 12, entity_ref
            
        mob = Combatant(
            id=mob_id,
            name=name,
            type="monster",
            hp=hp,
            max_hp=hp,
            ac=ac
        )
        combat.combatants.append(mob)

    await state.save_all()
    return f"Combat started with {len(combat.combatants)} combatants. Round 1."

async def roll_initiative_for_all(campaign_id: str = "default") -> str:
    """
    Roll initiative for all combatants and sort turn order. Call after starting combat.
    Example: roll_initiative_for_all() returns "Initiative Rolled:\nAria: 18\nGoblin: 12"
    """
    state = get_game_state(campaign_id)
    combat = await state.combat
    if not combat.active:
        return "No active combat."
        
    results = []
    for c in combat.combatants:
        # Puts dex mod logic here? Or just assumes 0 for now?
        # Ideally fetch dex mod from character/monster model.
        # Simplified:
        mod = 0
        if c.type == "player" and await state.character:
            mod = state.character.defense.initiative_mod
        
        init = roll_initiative(mod)
        c.initiative = init
        results.append(f"{c.name}: {init}")
        
    # Sort by initiative desc
    combat.combatants.sort(key=lambda x: x.initiative, reverse=True)
    combat.turn_index = 0
    
    await state.save_all()
    return "Initiative Rolled:\n" + "\n".join(results)

async def get_initiative_order(campaign_id: str = "default") -> str:
    """
    Get current turn order with HP status and whose turn it is. Use each round.
    Example: get_initiative_order() shows "-> Aria (pc_abc123) - Init: 18, HP: 15/15"
    """
    state = get_game_state(campaign_id)
    combat = await state.combat
    if not combat.active:
        return "No active combat."
        
    order = []
    for i, c in enumerate(combat.combatants):
        marker = "-> " if i == combat.turn_index else "   "
        order.append(f"{marker}{c.name} ({c.id}) - Init: {c.initiative}, HP: {c.hp}/{c.max_hp}, Status: {c.status}")
        
    return "Turn Order:\n" + "\n".join(order)

async def next_turn(campaign_id: str = "default") -> str:
    """
    Advance to next combatant's turn. Automatically increments rounds when order loops.
    Example: next_turn() returns "It is Goblin's turn." or "Round 2 begins!"
    """
    state = get_game_state(campaign_id)
    combat = await state.combat
    if not combat.active:
        return "No active combat."
    
    if not combat.combatants:
        return "No combatants in combat."
        
    combat.turn_index += 1
    if combat.turn_index >= len(combat.combatants):
        combat.turn_index = 0
        combat.round += 1
        current = combat.current_actor
        if current:
            return f"Round {combat.round} begins! It is {current.name}'s turn."
        else:
            return f"Round {combat.round} begins!"
    
    current = combat.current_actor
    if not current:
        return "No current actor found."
        
    # Skip dead/fled
    while current.status != "active":
        combat.turn_index += 1
        if combat.turn_index >= len(combat.combatants):
            combat.turn_index = 0
            combat.round += 1
            current = combat.current_actor
            if current:
                return f"Round {combat.round} begins! It is {current.name}'s turn."
            else:
                return f"Round {combat.round} begins!"
        
        current = combat.current_actor
        if not current:
            return "No current actor found."
        
    await state.save_all()
    return f"It is {current.name}'s turn."

async def make_attack(attacker_id: str, target_id: str, weapon: str, advantage: bool = False, campaign_id: str = "default") -> str:
    """
    Resolve attack roll vs target AC. Returns hit/miss and damage but doesn't apply HP.
    Example: make_attack("pc_abc123", "goblin_1", "Longsword") rolls attack vs goblin.
    """
    state = get_game_state(campaign_id)
    combat = await state.combat
    
    # Validation
    attacker = next((c for c in combat.combatants if c.id == attacker_id), None)
    target = next((c for c in combat.combatants if c.id == target_id), None)
    
    if not attacker: return f"Attacker {attacker_id} not found."
    if not target: return f"Target {target_id} not found."
    
    # Determine bonuses (Simplified: Need to fetch from Char/Monster models)
    # For prototype: Assume player uses Char model, Monsters use fixed +4
    attack_bonus = 4
    damage_dice = "1d6+2"
    
    if attacker.type == "player" and await state.character:
        # Find weapon in attacks
        atk_meta = next((a for a in state.character.combat.attacks if a.name.lower() == weapon.lower()), None)
        if atk_meta:
            attack_bonus = atk_meta.bonus
            damage_dice = atk_meta.damage
            # Fallback for "Sword", "Bow" etc if exact match fails, or assume improvised
            pass
            
    elif attacker.type == "monster":
        # Fetch monster data to check specific actions
        from dnd_mcp_server.tools.lookup import get_monster_data
        data = get_monster_data(attacker.name)
        if data and "actions" in data:
            # Look for action name
            # Fuzzy match action name
            action = next((a for a in data["actions"] if weapon.lower() in a.get("name", "").lower()), None)
            if not action:
                 # Try first action if no match (default attack)
                 action = data["actions"][0] if data["actions"] else None
                 
            if action:
                attack_bonus = action.get("attack_bonus", 4)
                # Damage dice often in desc: "Hit: 7 (1d6 + 4) damage"
                # Need regex to parse if 'damage_dice' key not present (Open5e often doesn't have structured damage)
                # But 'damage_dice' might occur in some records. 
                # fallback parse description:
                desc = action.get("desc", "")
                import re
                # Pattern: (1d6 + 4) or 1d6
                dmg_match = re.search(r'\(?(\d+d\d+(?:\s?[\+\-]\s?\d+)?)\)?', desc)
                if dmg_match:
                    damage_dice = dmg_match.group(1).replace(" ", "")
            
    # Roll Attack
    d20_roll = random.randint(1, 20) 
    # Use dice.py logic if advantage? Re-implementing simplified here for speed/context
    if advantage:
        d20_roll = max(d20_roll, random.randint(1, 20))
        
    total_to_hit = d20_roll + attack_bonus
    
    # Roll Damage (Simulation)
    # Parse damage dice string "1d8+3"
    # Basic parse:
    dmg_parts = damage_dice.split('+')
    dmg_roll_str = dmg_parts[0]
    dmg_mod = int(dmg_parts[1]) if len(dmg_parts) > 1 else 0
    
    # Hacky extraction of XdY
    try:
        d_split = dmg_roll_str.lower().split('d')
        num = int(d_split[0])
        sides = int(d_split[1])
        dmg_val = sum(random.randint(1, sides) for _ in range(num)) + dmg_mod
    except:
        dmg_val = 0 # Error fallback
        
    result_str = (
        f"Attack Result:\n"
        f"Attacker: {attacker.name}\n"
        f"Target: {target.name} (AC {target.ac})\n"
        f"Roll: {d20_roll} + {attack_bonus} = **{total_to_hit}**\n"
    )
    
    if total_to_hit >= target.ac:
        result_str += f"HIT! Damage: {damage_dice} = **{dmg_val}**"
    elif d20_roll == 20:
         result_str += f"CRITICAL HIT! Damage: **{dmg_val * 2}** (Simplified Crit)" # Ideally roll twice
    else:
        result_str += "MISS!"
        
    return result_str

async def end_combat(campaign_id: str = "default") -> str:
    """
    End current combat encounter and clear temporary combat state.
    Example: end_combat() returns "Combat ended." and resets combat flags.
    """
    state = get_game_state(campaign_id)
    state.combat.active = False
    await state.save_all()
    return "Combat ended."
