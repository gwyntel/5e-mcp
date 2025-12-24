import httpx
from typing import Optional, List, Dict, Any
import random

BASE_URL = "https://api.open5e.com"

def _fetch(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}


def get_monster_data(name: str) -> Optional[Dict[str, Any]]:
    """
    Internal helper to fetch raw monster dictionary data. 
    Not intended for direct AI use; use lookup_monster instead.
    """
    # 1. Try exact match first
    data = _fetch("/v1/monsters/", {"name__iexact": name, "limit": 1})
    if data.get("results"):
        return data["results"][0]

    # 2. Try singularized exact match if name ends in 's'
    if name.lower().endswith('s') and len(name) > 3:
        singular = name[:-1]
        data = _fetch("/v1/monsters/", {"name__iexact": singular, "limit": 1})
        if data.get("results"):
            return data["results"][0]

    # 3. Fallback to search
    params = {"search": name, "limit": 20}
    data = _fetch("/v1/monsters/", params)
    results = data.get("results", [])
    
    if not results: return None
    
    # 4. Prioritize exact-ish matches in results
    name_low = name.lower()
    # Exact name match in results
    exact = next((m for m in results if m['name'].lower() == name_low), None)
    if exact: return exact
    
    # Singularized name match in results
    if name_low.endswith('s'):
        singular = name_low[:-1]
        match = next((m for m in results if m['name'].lower() == singular), None)
        if match: return match
        
    # Substring match (either way)
    sub = next((m for m in results if name_low in m['name'].lower() or m['name'].lower() in name_low), None)
    return sub if sub else results[0]

def lookup_monster(name: str, cr_range: Optional[str] = None) -> str:
    """
    Search Open5e database for monster stats, HP, AC, actions, and challenge rating.
    Example: lookup_monster("Goblin", "0-1") returns goblin stats filtered by CR 0-1.
    """
    # Try exact match first
    data = _fetch("/v1/monsters/", {"name__iexact": name, "limit": 1})
    if not data.get("results"):
        # Fallback to search
        data = _fetch("/v1/monsters/", {"search": name, "limit": 10})
    
    results = data.get("results", [])
    if not results:
        return f"No monster found matching '{name}'."
        
    filtered = results
    if cr_range:
        # Simple client-side filtering for CR
        try:
            if "-" in cr_range:
                min_cr, max_cr = map(float, cr_range.split("-"))
                filtered = [m for m in results if min_cr <= m.get("cr", 0) <= max_cr]
            else:
                target = float(cr_range)
                filtered = [m for m in results if m.get("cr", 0) == target]
        except:
            pass # Ignore invalid CR format

    if not filtered:
        return f"Found monsters matching '{name}' but none in CR range {cr_range}."

    # Return the first best match
    # Prioritize exact name match if available (if we fell back to search)
    best = next((m for m in filtered if m['name'].lower() == name.lower()), None)
    if not best:
        best = filtered[0]

    # Format a specialized summary for the AI
    return (
        f"Name: {best.get('name', 'Unknown')}\n"
        f"CR: {best.get('challenge_rating', '?')} ({best.get('xp', '?')} XP)\n"
        f"Type: {best.get('size', '')} {best.get('type', '')} ({best.get('alignment', '')})\n"
        f"AC: {best.get('armor_class', '?')} ({best.get('armor_desc', '')})\n"
        f"HP: {best.get('hit_points', '?')} ({best.get('hit_dice', '')})\n"
        f"Stats: Str {best.get('strength', 10)}, Dex {best.get('dexterity', 10)}, Con {best.get('constitution', 10)}, "
        f"Int {best.get('intelligence', 10)}, Wis {best.get('wisdom', 10)}, Cha {best.get('charisma', 10)}\n"
        f"Actions: {', '.join([a.get('name', 'Action') for a in best.get('actions', []) if a.get('name')])}"
    )

def lookup_spell(name: str, level: Optional[int] = None, class_name: Optional[str] = None) -> str:
    """
    Search for spell details including level, school, casting time, components, description.
    Example: lookup_spell("Fireball", 3, "Wizard") returns Fireball spell details.
    """
    # Try exact match first
    params = {"name__iexact": name}
    if level is not None: params["level_int"] = level
    data = _fetch("/v1/spells/", params)
    
    if not data.get("results"):
        # Fallback
        params = {"search": name}
        if level is not None: params["level_int"] = level
        data = _fetch("/v1/spells/", params)
        
    results = data.get("results", [])
    
    if not results:
        return f"No spell found matching '{name}'."
        
    # Client side filter for class if API doesn't support it strictly in search or if ambiguous
    if class_name:
        results = [s for s in results if class_name.lower() in s.get("dnd_class", "").lower()]
        
    if not results:
        return f"Found spells matching '{name}' but none for class {class_name}."
    
    # Prioritize exact
    spell = next((s for s in results if s['name'].lower() == name.lower()), results[0])

    return (
        f"Name: {spell['name']}\n"
        f"Level: {spell['level']} {spell['school']}\n"
        f"Casting Time: {spell['casting_time']}\n"
        f"Range: {spell['range']}\n"
        f"Components: {spell['components']} ({spell.get('material', '')})\n"
        f"Duration: {spell['duration']}\n"
        f"Description: {spell['desc'][:500]}..."
    )

def lookup_item(name: str, type: Optional[str] = None, rarity: Optional[str] = None) -> str:
    """
    Search for magic items, weapons, or armor with stats, rarity, cost, properties.
    Example: lookup_item("Longsword +1") returns magic longsword details.
    """
    # Magic items
    # Try exact match
    data = _fetch("/v1/magicitems/", {"name__iexact": name})
    if not data.get("results"):
        data = _fetch("/v1/magicitems/", {"search": name})
        
    results = data.get("results", [])
    
    # Also check weapons/armor if magic item not found? 
    # Open5e splits them. For simplicity, just check magic items first.
    
    if not results:
        # Check standard weapons/armor if magic item failed
        # Weapons
        data = _fetch("/v1/weapons/", {"name__iexact": name})
        if not data.get("results"): data = _fetch("/v1/weapons/", {"search": name})
        
        if data.get("results"):
            item = data["results"][0]
            return (
                f"Name: {item['name']}\n"
                f"Category: {item['category']}\n"
                f"Damage: {item['damage_dice']} {item['damage_type']}\n"
                f"Properties: {', '.join(item.get('properties', []))}\n"
                f"Cost: {item['cost']}, Weight: {item.get('weight', '?')}"
            )
            
        # Armor
        data = _fetch("/v1/armor/", {"name__iexact": name})
        if not data.get("results"): data = _fetch("/v1/armor/", {"search": name})
        
        if data.get("results"):
            item = data["results"][0]
            return (
                f"Name: {item['name']}\n"
                f"Category: {item['category']}\n"
                f"AC: {item['ac_string']}\n"
                f"Stealth Disadvantage: {item['stealth_check']}\n"
                f"Cost: {item['cost']}, Weight: {item.get('weight', '?')}"
            )

        return f"No item (magic, weapon, or armor) found matching '{name}'."
        
    item = results[0]
    return (
        f"Name: {item['name']}\n"
        f"Type: {item['type']}, Rarity: {item['rarity']}\n"
        f"Attunement: {item.get('requires_attunement', 'No')}\n"
        f"Desc: {item['desc'][:500]}..."
    )

def lookup_feat(name: str) -> str:
    """
    Search for feat with prerequisites and mechanical description.
    Example: lookup_feat("Sharpshooter") returns Sharpshooter feat details.
    """
    params = {"search": name}
    data = _fetch("/v1/feats/", params)
    results = data.get("results", [])
    
    if not results:
        return f"No feat found matching '{name}'."
        
    feat = results[0]
    return (
        f"Name: {feat['name']}\n"
        f"Prerequisite: {feat.get('prerequisite', 'None')}\n"
        f"Desc: {feat['desc'][:800]}..."
    )

def get_spell_list(class_name: str, level: Optional[int] = None) -> str:
    """
    Get list of all spell names for specific class and optional level filter.
    Example: get_spell_list("Wizard", 1) returns all level 1 Wizard spells.
    """
    # Open5e allows filtering by class: /v1/spells/?dnd_class=Wizard
    params = {"dnd_class__icontains": class_name, "limit": 50}
    if level is not None:
        params["level_int"] = level
        
    data = _fetch("/v1/spells/", params)
    results = data.get("results", [])
    
    if not results:
        return f"No spells found for {class_name} (Level {level if level is not None else 'All'})."
        
    # Summarize
    names = [f"{s['name']} (Lvl {s['level']})" for s in results]
    return f"Spells for {class_name}:\n" + ", ".join(names)

def get_random_monster(cr: float, type: Optional[str] = None, environment: Optional[str] = None) -> str:
    """
    Get random monster by CR with optional type and environment filters.
    Example: get_random_monster(2.0, "Beast") returns random CR 2 beast.
    """
    # Open5e allows filtering by CR exact: ?cr=1.0
    params = {"cr": cr, "limit": 50}
    if type:
        params["type"] = type
        
    data = _fetch("/v1/monsters/", params)
    results = data.get("results", [])
    
    if not results:
        return "No monsters found matching criteria."
        
    # Filter environment client side as it's often a list or text field
    if environment:
        # This is fuzzy, 'environments' might be a list in json
        results = [m for m in results if environment.lower() in str(m.get("environments", "")).lower()]
        
    if not results:
        return "No monsters match environment."
        
    best = random.choice(results)
    return lookup_monster(best["name"]) # Reuse formatter
