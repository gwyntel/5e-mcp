"""
JSON Schema definitions for D&D 5e MCP Server tool validation.

These schemas help small LLMs validate parameters before making tool calls,
reducing errors and improving reliability for local models.
"""

from typing import Dict, Any, List
import json

# Character Tool Schemas
CHARACTER_SHEET_SCHEMA = {
    "type": "object",
    "properties": {
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier (default: 'default')",
            "default": "default"
        }
    },
    "required": []
}

UPDATE_HP_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {
            "type": "integer",
            "description": "Positive amount of damage/healing/temp HP",
            "minimum": 1
        },
        "type": {
            "type": "string",
            "enum": ["damage", "healing", "temp"],
            "description": "Type of HP modification",
            "default": "damage"
        },
        "target_id": {
            "type": "string",
            "description": "Combat target ID (optional)"
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["amount"]
}

UPDATE_STAT_SCHEMA = {
    "type": "object",
    "properties": {
        "stat": {
            "type": "string",
            "enum": ["str", "dex", "con", "intelligence", "wis", "cha"],
            "description": "Ability score to update"
        },
        "value": {
            "type": "integer",
            "description": "New stat value (1-20)",
            "minimum": 1,
            "maximum": 20
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["stat", "value"]
}

CREATE_CHARACTER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Character name",
            "minLength": 1
        },
        "race": {
            "type": "string",
            "description": "Character race",
            "enum": ["Human", "Elf", "Dwarf", "Halfling", "Gnome", "Dragonborn", "Half-Elf", "Half-Orc", "Tiefling"]
        },
        "class_name": {
            "type": "string",
            "description": "Character class",
            "enum": ["Fighter", "Wizard", "Cleric", "Rogue", "Ranger", "Paladin", "Barbarian", "Bard", "Druid", "Monk", "Sorcerer", "Warlock"]
        },
        "background": {
            "type": "string",
            "description": "Character background"
        },
        "stats": {
            "type": "object",
            "properties": {
                "str": {"type": "integer", "minimum": 1, "maximum": 20},
                "dex": {"type": "integer", "minimum": 1, "maximum": 20},
                "con": {"type": "integer", "minimum": 1, "maximum": 20},
                "intelligence": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Intelligence attribute (using 'intelligence' because 'int' is a reserved keyword in Python)"},
                "wis": {"type": "integer", "minimum": 1, "maximum": 20},
                "cha": {"type": "integer", "minimum": 1, "maximum": 20}
            },
            "required": ["str", "dex", "con", "intelligence", "wis", "cha"]
        },
        "level": {
            "type": "integer",
            "description": "Starting level (1-20)",
            "minimum": 1,
            "maximum": 20,
            "default": 1
        },
        "hit_die": {
            "type": "string",
            "enum": ["d6", "d8", "d10", "d12"],
            "description": "Hit die type",
            "default": "d8"
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["name", "race", "class_name", "background", "stats"]
}

# Combat Tool Schemas
START_COMBAT_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of monster names to fight",
            "minItems": 1
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["entities"]
}

MAKE_ATTACK_SCHEMA = {
    "type": "object",
    "properties": {
        "attacker_id": {
            "type": "string",
            "description": "ID of attacker from initiative order"
        },
        "target_id": {
            "type": "string",
            "description": "ID of target from initiative order"
        },
        "weapon": {
            "type": "string",
            "description": "Weapon or attack name"
        },
        "advantage": {
            "type": "boolean",
            "description": "Roll with advantage",
            "default": False
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["attacker_id", "target_id", "weapon"]
}

# Inventory Tool Schemas
ITEMS_ADD_SCHEMA = {
    "type": "object",
    "properties": {
        "item_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of item identifiers to add"
        },
        "equip_to_slot": {
            "type": "string",
            "enum": ["main_hand", "off_hand", "armor", None],
            "description": "Equipment slot to auto-equip the first item to",
            "default": None
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["item_ids"]
}

GOLD_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {
            "type": "integer",
            "description": "Gold amount (positive for add, negative for remove)",
            "minimum": 1
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["amount"]
}

# Spell Tool Schemas
CAST_SPELL_SCHEMA = {
    "type": "object",
    "properties": {
        "spell_name": {
            "type": "string",
            "description": "Name of spell to cast"
        },
        "level": {
            "type": "integer",
            "description": "Spell level (0-9)",
            "minimum": 0,
            "maximum": 9
        },
        "concentration": {
            "type": "boolean",
            "description": "Spell requires concentration",
            "default": False
        },
        "prepare": {
            "type": "boolean",
            "description": "Prepare spell before casting",
            "default": False
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["spell_name", "level"]
}

# Check Tool Schemas
MAKE_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "check_type": {
            "type": "string",
            "enum": ["skill", "ability"],
            "description": "Type of check to make"
        },
        "skill_or_ability": {
            "type": "string",
            "description": "Skill name or ability (str, dex, etc.)"
        },
        "dc": {
            "type": "integer",
            "description": "Difficulty Class (1-30)",
            "minimum": 1,
            "maximum": 30,
            "default": 10
        },
        "advantage": {
            "type": "boolean",
            "description": "Roll with advantage",
            "default": False
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["check_type", "skill_or_ability"]
}

# Rest Tool Schemas
REST_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": ["short", "long"],
            "description": "Type of rest",
            "default": "long"
        },
        "campaign_id": {
            "type": "string",
            "description": "Campaign identifier",
            "default": "default"
        }
    },
    "required": ["type"]
}

# Dice Tool Schemas
ROLL_DICE_SCHEMA = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "Dice expression (e.g., '2d6+4', '1d20')",
            "pattern": "^\\d+d\\d+([+-]\\d+)?$"
        },
        "advantage": {
            "type": "boolean",
            "description": "Roll with advantage",
            "default": False
        },
        "disadvantage": {
            "type": "boolean",
            "description": "Roll with disadvantage",
            "default": False
        }
    },
    "required": ["expression"]
}

# Validation Helper Functions
def validate_params(params: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate parameters against JSON schema and return list of errors.
    """
    errors = []
    
    for required_field in schema.get("required", []):
        if required_field not in params:
            errors.append(f"Missing required parameter: {required_field}")
    
    for field_name, field_schema in schema.get("properties", {}).items():
        if field_name in params:
            value = params[field_name]
            field_type = field_schema.get("type")
            
            # Type validation
            if field_type == "integer":
                if not isinstance(value, int):
                    errors.append(f"{field_name} must be an integer, got {type(value).__name__}")
                else:
                    minimum = field_schema.get("minimum")
                    maximum = field_schema.get("maximum")
                    if minimum is not None and value < minimum:
                        errors.append(f"{field_name} must be >= {minimum}, got {value}")
                    if maximum is not None and value > maximum:
                        errors.append(f"{field_name} must be <= {maximum}, got {value}")
            
            elif field_type == "string":
                if not isinstance(value, str):
                    errors.append(f"{field_name} must be a string, got {type(value).__name__}")
                else:
                    enum_values = field_schema.get("enum")
                    if enum_values and value not in enum_values:
                        errors.append(f"{field_name} must be one of {enum_values}, got '{value}'")
                    min_length = field_schema.get("minLength")
                    if min_length and len(value) < min_length:
                        errors.append(f"{field_name} must be at least {min_length} characters")
            
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{field_name} must be boolean, got {type(value).__name__}")
            
            elif field_type == "array":
                if not isinstance(value, list):
                    errors.append(f"{field_name} must be an array, got {type(value).__name__}")
                else:
                    min_items = field_schema.get("minItems")
                    if min_items and len(value) < min_items:
                        errors.append(f"{field_name} must have at least {min_items} items")
    
    return errors

# Common validation patterns for small LLMs
COMMON_VALIDATION_TIPS = {
    "character_creation": "Always include all 6 ability scores (str, dex, con, intelligence, wis, cha)",
    "combat": "Use get_initiative_order() to get correct target IDs before attacking",
    "spells": "Check spell slots with get_spell_slots() before casting",
    "inventory": "Use get_inventory() to verify item exists before equipping",
    "general": "Call get_character_sheet() to verify state before major actions"
}

def get_validation_tips() -> str:
    """Return validation tips for small LLMs."""
    return "\n".join([f"• {key}: {tip}" for key, tip in COMMON_VALIDATION_TIPS.items()])

# Export all schemas for easy access
ALL_SCHEMAS = {
    "get_character_sheet": CHARACTER_SHEET_SCHEMA,
    "update_hp": UPDATE_HP_SCHEMA,
    "update_stat": UPDATE_STAT_SCHEMA,
    "create_character": CREATE_CHARACTER_SCHEMA,
    "start_combat": START_COMBAT_SCHEMA,
    "make_attack": MAKE_ATTACK_SCHEMA,
    "items_add": ITEMS_ADD_SCHEMA,
    "remove_gold": GOLD_SCHEMA,
    "add_gold": GOLD_SCHEMA,
    "cast_spell": CAST_SPELL_SCHEMA,
    "make_check": MAKE_CHECK_SCHEMA,
    "rest": REST_SCHEMA,
    "roll_dice": ROLL_DICE_SCHEMA
}
