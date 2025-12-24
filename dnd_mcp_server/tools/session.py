from typing import Dict, List, Any, Optional
import json
import datetime
from dnd_mcp_server.storage.game_state import get_game_state
from dnd_mcp_server.models.campaign import CampaignState

async def get_campaign_state(campaign_id: str) -> str:
    """
    Retrieves the complete campaign state including all sessions, NPCs, locations, quests, and story threads. 
    Returns the entire data structure - no filtering or summarization. 
    Use this at the start of sessions to load context for your recap and to understand the current world state.

    Example:
    state = get_campaign_state("emerald_tangle")
    # Returns full CampaignState object with all nested data
    """
    state_mgr = get_game_state(campaign_id=campaign_id)
    campaign = await state_mgr.campaign
    
    if not campaign:
        # Auto-initialize if it doesn't exist
        char = await state_mgr.character
        if not char:
            return json.dumps({"error": "No character found. Campaign must be initialized after character creation."}, indent=2)
        
        campaign = CampaignState(
            campaign_id=campaign_id,
            campaign_name=campaign_id.replace("_", " ").title(),
            character_id=char.id
        )
        await state_mgr.save_campaign(campaign)
        
    return campaign.model_dump_json(indent=2)


def _apply_deep_merge(target: Dict[str, Any], changes: Dict[str, Any]):
    """Helper to apply nested dictionary updates with list append support."""
    for key, value in changes.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                _apply_deep_merge(target[key], value)
            elif isinstance(value, list) and len(value) == 2 and value[0] == "append":
                if not isinstance(target[key], list):
                    target[key] = []
                target[key].append(value[1])
            else:
                target[key] = value
        else:
            # Key doesn't exist, auto-create it
            if isinstance(value, list) and len(value) == 2 and value[0] == "append":
                target[key] = [value[1]]
            else:
                target[key] = value


async def update_campaign_state(campaign_id: str, changes: Dict[str, Any]) -> str:
    """
    Updates any part of the campaign state using nested dictionary changes. 
    Only provide the fields you want to change - everything else remains untouched. 
    Supports deep merging and special list operations.
    Returns the FULL updated CampaignState after changes are applied.

    Special list operations:
    - Use ["append", value] to add to a list without replacing it
    - Provide a plain list to replace the entire list

    Examples:

    # Add a new NPC (auto-creates if NPC doesn't exist)
    update_campaign_state("emerald_tangle", {
      "world": {
        "npcs": {
          "Kira Swiftpaw": {
            "name": "Kira Swiftpaw",
            "race": "Tabaxi",
            "descriptor": "lithe spotted hunter",
            "relationship": "grateful ally",
            "location": "Southern hunting grounds",
            "role": "Hunter",
            "first_met": 1,
            "last_seen": 1,
            "memorable_moments": ["You saved her hunting party from the blighted jaguar"],
            "personality": "Brave but shaken, speaks quickly when nervous"
          }
        }
      }
    })

    # Update existing NPC (only changes specified fields)
    update_campaign_state("emerald_tangle", {
      "world": {
        "npcs": {
          "Kira Swiftpaw": {
            "location": "Your sacred grove",
            "relationship": "close ally",
            "last_seen": 2,
            "memorable_moments": ["append", "Asked you to investigate the Blighted Grove"]
          }
        }
      }
    })

    # Add a new location
    update_campaign_state("emerald_tangle", {
      "world": {
        "locations": {
          "Blighted Grove": {
            "name": "Blighted Grove",
            "type": "Wilderness",
            "description": "A corrupted section of jungle where black fungus grows",
            "status": {"discovered": True, "visited": False, "cleared": False},
            "threats": ["Unknown number of corrupted creatures"],
            "features": ["Black fungal growths", "Dead vegetation"]
          }
        }
      }
    })

    # Create a new quest
    update_campaign_state("emerald_tangle", {
      "story": {
        "quests": {
          "Investigate the Blighted Grove": {
            "name": "Investigate the Blighted Grove",
            "type": "main",
            "giver": "Kira Swiftpaw",
            "why_pc_cares": "Source of corruption threatening your sacred grove",
            "objective": "Find and eliminate the source of the black fungal blight",
            "next_step": "Travel northwest to the Blighted Grove",
            "status": "active",
            "progress_notes": [],
            "locations_involved": ["Blighted Grove"],
            "npcs_involved": ["Kira Swiftpaw"],
            "started_session": 1
          }
        }
      }
    })

    # Mark quest as completed
    update_campaign_state("emerald_tangle", {
      "story": {
        "quests": {
          "Defeat the Blighted Jaguar": {
            "status": "completed",
            "completed_session": 1,
            "progress_notes": ["append", "Session 1: Defeated in combat near hunting grounds"]
          }
        }
      }
    })

    # Save session summary at end of session
    update_campaign_state("emerald_tangle", {
      "current_session": 2,
      "sessions": ["append", {
        "session_number": 1,
        "date": "2025-01-15T20:00:00",
        "dramatic_moments": [
          "Failed to communicate with corrupted beast - touched void-mind",
          "Saved Kira's hunting party from blighted jaguar"
        ],
        "character_feelings": "Disturbed by psychic wrongness, protective of fellow Tabaxi",
        "cliffhanger": "Black spores drift upward from the corpse toward the canopy...",
        "narrative_summary": "Fiona awoke in her sacred grove to find the mycelial network disturbed...",
        "world_changes": ["Blighted jaguar defeated near southern hunting grounds"]
      }]
    })

    # Add mystery clues
    update_campaign_state("emerald_tangle", {
      "story": {
        "mysteries": {
          "Fungal Source": {
            "question": "What is the source of the black fungal corruption?",
            "clues_found": ["append", "Corruption emanates from the Blighted Grove northwest"]
          }
        }
      }
    })
    """
    state_mgr = get_game_state(campaign_id=campaign_id)
    campaign = await state_mgr.campaign
    
    if not campaign:
        # Auto-initialize if it doesn't exist
        char = await state_mgr.character
        if not char:
            return json.dumps({"error": "No character found. Campaign must be initialized after character creation."}, indent=2)
            
        campaign = CampaignState(
            campaign_id=campaign_id,
            campaign_name=campaign_id.replace("_", " ").title(),
            character_id=char.id
        )
    
    # Apply changes
    current_data = campaign.model_dump()
    _apply_deep_merge(current_data, changes)
    
    # Re-validate and update timestamp
    updated_campaign = CampaignState(**current_data)
    updated_campaign.last_updated = datetime.datetime.now()
    
    # Save back
    await state_mgr.save_campaign(updated_campaign)
    
    return updated_campaign.model_dump_json(indent=2)


async def load_session_history(campaign_id: str = "default") -> str:
    """
    DEPRECATED: Use get_campaign_state instead.
    Load all previous session summaries for campaign continuity.
    """
    state = get_game_state(campaign_id=campaign_id)
    campaign = await state.campaign
    if not campaign or not campaign.sessions:
        return "No session history found in CampaignState."
    
    output = []
    for s in campaign.sessions:
        output.append(f"--- Session: {s.session_number} ({s.date.isoformat()}) ---\n{s.narrative_summary}\n")
    return "\n".join(output)


async def save_session_summary(summary: str, campaign_id: str = "default") -> str:
    """
    DEPRECATED: Use update_campaign_state instead.
    Save narrative session summary to campaign log for story continuity.
    """
    state_mgr = get_game_state(campaign_id=campaign_id)
    campaign = await state_mgr.campaign
    if not campaign:
        return "Error: Campaign state not found. Use get_campaign_state first."
        
    session_num = len(campaign.sessions) + 1
    new_session = {
        "session_number": session_num,
        "date": datetime.datetime.now().isoformat(),
        "dramatic_moments": [],
        "character_feelings": "Unknown",
        "narrative_summary": summary,
        "world_changes": []
    }
    
    return await update_campaign_state(campaign_id, {"sessions": ["append", new_session]})
