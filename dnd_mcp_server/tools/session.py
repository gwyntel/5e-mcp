from typing import Dict, List
import json
import datetime
from dnd_mcp_server.storage.game_state import get_game_state

async def load_session_history(campaign_id: str = "default") -> str:
    """
    Load all previous session summaries for campaign continuity.
    Example: load_session_history() returns formatted session logs with dates and summaries.
    """
    state = get_game_state(campaign_id=campaign_id)
    
    # Session data is stored as a JSON string in storage
    session_key = f"sessions:{campaign_id}"
    data_json = await state.storage.storage.get(session_key)
    
    if not data_json:
        return "No session history found."
    
    try:
        data = json.loads(data_json)
        
        # Format for readability
        output = []
        for session_id, info in data.items():
            date = info.get("date", "Unknown Date")
            summary = info.get("summary", "")
            output.append(f"--- Session: {session_id} ({date}) ---\n{summary}\n")
            
        return "\n".join(output) if output else "Session history is empty."
    except Exception as e:
        return f"Error loading history: {str(e)}"

async def save_session_summary(summary: str, campaign_id: str = "default") -> str:
    """
    Save narrative session summary to campaign log for story continuity.
    Example: save_session_summary("Defeated goblins, found treasure") saves session summary.
    """
    state = get_game_state(campaign_id=campaign_id)
    
    # Load existing session data
    session_key = f"sessions:{campaign_id}"
    data_json = await state.storage.storage.get(session_key)
    
    data = {}
    if data_json:
        try:
            data = json.loads(data_json)
        except:
            pass  # Start fresh if error
    
    # Generate session key
    session_num = len(data) + 1
    session_id = f"session_{session_num}"
    today = datetime.date.today().isoformat()
    
    data[session_id] = {
        "date": today,
        "summary": summary
    }
    
    # Save back to storage
    await state.storage.storage.set(session_key, json.dumps(data))
    
    return f"Session summary saved as {session_id}."
