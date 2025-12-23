import uuid
from dnd_mcp_server.models.world import Location, LocationIdentity

def generate_location(type: str, difficulty: str) -> Location:
    """Generates a location."""
    loc_id = f"loc_{uuid.uuid4().hex[:8]}"
    return Location(
        id=loc_id,
        identity=LocationIdentity(name=f"Random {type}", type=type),
        description=f"A {difficulty.lower()} difficulty {type}.",
        connections=[]
    )
    
def generate_npc(role: str) -> str:
    """Generates an NPC (returns ID or Description)."""
    # For now just string description
    return f"Generated NPC: {role} (Commoner stats)"
