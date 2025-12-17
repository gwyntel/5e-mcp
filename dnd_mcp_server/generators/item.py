import uuid
from ..models.item import Item, ItemIdentity

def generate_magic_item(rarity: str, concept: str) -> Item:
    """Generates a random item."""
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    return Item(
        id=item_id,
        identity=ItemIdentity(
            name=f"{rarity} {concept}",
            type="Wonderous",
            rarity=rarity
        ),
        description=f"A {rarity.lower()} item that embodies {concept}.",
        value_gp=500,
        weight=1.0,
        magic_properties=None
    )
