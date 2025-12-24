"""
Enhanced validation layer with helpful error messages for small LLMs.

This module provides user-friendly error messages and validation helpers
to improve reliability when using local 7B-13B models.
"""

from typing import Dict, Any, List, Optional
from dnd_mcp_server.schemas import validate_params, get_validation_tips

class ValidationError(Exception):
    """Custom exception for validation errors with helpful messages."""
    pass

def validate_tool_call(tool_name: str, params: Dict[str, Any]) -> None:
    """
    Validate tool parameters and raise ValidationError with helpful message if invalid.
    """
    from dnd_mcp_server.schemas import ALL_SCHEMAS
    
    if tool_name not in ALL_SCHEMAS:
        raise ValidationError(f"Unknown tool '{tool_name}'. Available tools: {', '.join(ALL_SCHEMAS.keys())}")
    
    schema = ALL_SCHEMAS[tool_name]
    errors = validate_params(params, schema)
    
    if errors:
        # Group errors by type for better readability
        missing_params = [e for e in errors if "Missing" in e]
        invalid_params = [e for e in errors if "must be" in e or "must be one of" in e]
        range_errors = [e for e in errors if "must be >=" in e or "must be <=" in e]
        
        message_parts = []
        
        if missing_params:
            message_parts.append(f"Missing required parameters: {', '.join(missing_params)}")
        
        if invalid_params:
            message_parts.append(f"Invalid parameters: {', '.join(invalid_params)}")
        
        if range_errors:
            message_parts.append(f"Parameter range errors: {', '.join(range_errors)}")
        
        # Add helpful context
        message_parts.append(f"\n💡 Tip: Use get_character_sheet() to check current state first")
        
        raise ValidationError(f"Validation failed for {tool_name}:\n" + "\n".join(message_parts))

def suggest_fix(error_type: str, context: str = "") -> str:
    """
    Suggest fixes for common error patterns.
    """
    suggestions = {
        "no_character": "Create a character first using create_character() with name, race, class, background, and stats",
        "no_combat": "Start combat using start_combat(['MonsterName']) with monster names",
        "no_spell_slots": "Take a long rest using rest('long') to restore spell slots",
        "item_not_found": "Check inventory with get_inventory() or add items using items_add(['item_id'])",
        "invalid_target": "Use get_initiative_order() to see valid target IDs",
        "invalid_spell": "Use get_spell_list('ClassName') to see available spells",
        "stat_out_of_range": "Ability scores must be between 1-20. Use get_character_sheet() to check current values"
    }
    
    base_suggestion = suggestions.get(error_type, "Check current state with get_character_sheet()")
    if context:
        base_suggestion += f"\nContext: {context}"
    
    return base_suggestion

def validate_combat_state(campaign_id: str = "default") -> None:
    """
    Validate that combat state is consistent and provide helpful errors.
    """
    from dnd_mcp_server.persistence.state import get_game_state
    
    state = get_game_state(campaign_id)
    if not state.character:
        raise ValidationError("No character found. Use create_character() to create one first.")
    
    if state.combat.active:
        combat = state.combat
        if not combat.combatants:
            raise ValidationError("Combat is active but has no combatants. Use end_combat() to reset.")
        
        # Check for orphaned combatants (should have at least player)
        player_in_combat = any(c.type == "player" for c in combat.combatants)
        if not player_in_combat:
            raise ValidationError("Combat active but player not found. Use end_combat() and restart.")

def validate_character_state(campaign_id: str = "default") -> None:
    """
    Validate character state and provide context-aware error messages.
    """
    from dnd_mcp_server.persistence.state import get_game_state
    
    state = get_game_state(campaign_id)
    if not state.character:
        raise ValidationError("No character loaded. Use create_character() to create one.")
    
    char = state.character
    
    # Check for common issues
    issues = []
    
    if char.health.current_hp <= 0:
        issues.append("Character has 0 HP - use make_death_save() or stabilize_character()")
    
    if char.spellcasting:
        # Check if all spell slots are empty
        empty_slots = [level for level, slot in char.spellcasting.slots.items() if slot.current == 0 and slot.max > 0]
        if empty_slots and all(slot.current == 0 for slot in char.spellcasting.slots.values() if slot.max > 0):
            issues.append("All spell slots empty - consider rest('long') to restore")
    
    if issues:
        context = "\n".join([f"• {issue}" for issue in issues])
        raise ValidationError(f"Character state issues detected:\n{context}\n\n💡 Fix these issues before continuing.")

def get_parameter_examples(tool_name: str) -> str:
    """
    Return parameter examples for common tools to help small LLMs.
    """
    examples = {
        "create_character": 'create_character("Aria", "Elf", "Wizard", "Sage", {"str": 8, "dex": 14, "con": 12, "int": 16, "wis": 13, "cha": 10})',
        "start_combat": 'start_combat(["Goblin", "2 Wolves"])',
        "make_attack": 'make_attack("pc_abc123", "goblin_1", "Longsword", True)',
        "cast_spell": 'cast_spell("Fireball", 3, True, True)',
        "update_hp": 'update_hp(8, "damage", "goblin_1")',
        "items_add": 'items_add(["potion"], None)',
        "make_check": 'make_check("skill", "athletics", 15, True)',
        "rest": 'rest("long")',
        "roll_dice": 'roll_dice("1d20+3", True)'
    }
    
    return examples.get(tool_name, f"Example for {tool_name} not available")

def format_validation_error(tool_name: str, error: str) -> str:
    """
    Format validation errors with helpful context and examples.
    """
    examples = get_parameter_examples(tool_name)
    tips = get_validation_tips()
    
    return f"""
❌ Error in {tool_name}: {error}

💡 Example usage:
{examples}

📋 Common tips:
{tips}

🔄 Recovery steps:
1. Check current state: get_character_sheet()
2. Review error message above
3. Try again with corrected parameters
4. Use workflows.md for step-by-step guides
"""

def validate_and_suggest(tool_name: str, params: Dict[str, Any]) -> str:
    """
    Validate parameters and return helpful error message with suggestions.
    """
    try:
        validate_tool_call(tool_name, params)
        return "Validation passed"
    except ValidationError as e:
        return format_validation_error(tool_name, str(e))

# Context-aware validation helpers
def validate_combat_action(action: str, params: Dict[str, Any]) -> None:
    """
    Validate combat-specific actions with context awareness.
    """
    from dnd_mcp_server.persistence.state import get_game_state
    
    state = get_game_state(params.get("campaign_id", "default"))
    
    if not state.combat.active:
        raise ValidationError(f"Cannot {action}: No active combat. Use start_combat() first.")
    
    if action == "attack":
        attacker_id = params.get("attacker_id")
        target_id = params.get("target_id")
        
        if not attacker_id or not target_id:
            raise ValidationError("Attack requires both attacker_id and target_id")
        
        # Validate IDs exist in combat
        combatant_ids = [c.id for c in state.combat.combatants]
        if attacker_id not in combatant_ids:
            raise ValidationError(f"Attacker ID '{attacker_id}' not in combat. Use get_initiative_order() to see valid IDs.")
        if target_id not in combatant_ids:
            raise ValidationError(f"Target ID '{target_id}' not in combat. Use get_initiative_order() to see valid IDs.")
    
    elif action == "damage":
        target_id = params.get("target_id")
        amount = params.get("amount")
        
        if not target_id or not amount:
            raise ValidationError("Damage requires target_id and amount")
        
        if target_id not in [c.id for c in state.combat.combatants]:
            raise ValidationError(f"Target '{target_id}' not in active combat")

def validate_spell_casting(params: Dict[str, Any]) -> None:
    """
    Validate spell casting with resource management awareness.
    """
    from dnd_mcp_server.persistence.state import get_game_state
    
    state = get_game_state(params.get("campaign_id", "default"))
    
    if not state.character or not state.character.spellcasting:
        raise ValidationError("Character cannot cast spells. Check character class or create spellcasting character.")
    
    spell_name = params.get("spell_name")
    level = params.get("level")
    
    if not spell_name or level is None:
        raise ValidationError("Casting requires spell_name and level")
    
    # Check spell slots
    level_str = str(level)
    if level_str in state.character.spellcasting.slots:
        slot = state.character.spellcasting.slots[level_str]
        if slot.current <= 0:
            available_slots = [f"{lvl} ({slot.current}/{slot.max})" for lvl, slot in state.character.spellcasting.slots.items()]
            raise ValidationError(f"No level {level} spell slots remaining. Available: {', '.join(available_slots)}")
    
    # Check prepared spells if character requires preparation
    if state.character.spellcasting.prepared:
        prepared_spells = [s.lower() for s in state.character.spellcasting.prepared]
        if spell_name.lower() not in prepared_spells:
            raise ValidationError(f"Spell '{spell_name}' not prepared. Use prepare_spell('{spell_name}') or cast with prepare=True")
