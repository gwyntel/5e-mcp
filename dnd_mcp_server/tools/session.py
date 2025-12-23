from typing import Dict, List
import json
import os
from pathlib import Path

def get_campaign_dir(campaign_id: str) -> Path:
    """Get campaign directory path."""
    # Use save_data directory from environment or default to temp directory
    disk_dir = os.getenv("STORAGE_DISK_DIRECTORY")
    if disk_dir:
        base_dir = Path(disk_dir)
    else:
        # For memory backend, use a temp directory
        import tempfile
        base_dir = Path(tempfile.gettempdir()) / "5e-mcp-sessions"
    
    campaign_dir = base_dir / campaign_id
    try:
        campaign_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # If we can't create the directory, use temp
        import tempfile
        campaign_dir = Path(tempfile.gettempdir()) / "5e-mcp-sessions" / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
    
    return campaign_dir

def get_session_file_path(campaign_id: str) -> str:
    return str(get_campaign_dir(campaign_id) / "session_log.json")

async def load_session_history(campaign_id: str = "default") -> str:
    """
    Load all previous session summaries for campaign continuity.
    Example: load_session_history() returns formatted session logs with dates and summaries.
    """
    path = get_session_file_path(campaign_id)
    if not os.path.exists(path):
        return "No session history found."
        
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            
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
    path = get_session_file_path(campaign_id)
    
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except:
            pass # Start fresh if error
            
    # generate session key
    import datetime
    session_num = len(data) + 1
    session_key = f"session_{session_num}"
    today = datetime.date.today().isoformat()
    
    data[session_key] = {
        "date": today,
        "summary": summary
    }
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
    return f"Session summary saved as {session_key}."
