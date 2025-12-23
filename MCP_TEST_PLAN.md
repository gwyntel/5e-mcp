# Solo D&D MCP Server - Test Plan

**Version:** Post-Async Migration  
**Storage Backend:** Memory  
**Date:** 2025-12-22

## Overview

This test plan validates all MCP tools after the async migration that fixed storage backend issues. Execute these tests sequentially via MCP tool calls.

---

## Phase 1: Core Mechanics (No Character Required)

### Test 1.1: Dice Rolling
**Tool:** `roll_dice`

```
roll_dice(expression="1d20+5")
```
**Expected:** Returns roll result like `[15] + 5 = **20**`

```
roll_dice(expression="2d6+3", advantage=true)
```
**Expected:** Returns roll with advantage applied

### Test 1.2: Initiative Rolling
**Tool:** `roll_initiative`

```
roll_initiative(dex_mod=2)
```
**Expected:** Returns initiative value (1-20 + 2)

### Test 1.3: Monster Lookup
**Tool:** `lookup_monster`

```
lookup_monster(name="Goblin", cr_range="0-1")
```
**Expected:** Returns complete goblin stat block with HP, AC, actions

### Test 1.4: Spell Lookup
**Tool:** `lookup_spell`

```
lookup_spell(name="Fireball", level=3, class_name="Wizard")
```
**Expected:** Returns spell details (level, school, casting time, components, description)

### Test 1.5: Item Lookup
**Tool:** `lookup_item`

```
lookup_item(name="Longsword")
```
**Expected:** Returns item details (damage, properties, cost, weight)

---

## Phase 2: Character Creation & Retrieval

### Test 2.1: Create Character
**Tool:** `create_character`

```
create_character(
    name="Aria Stormwind",
    race="Elf",
    class_name="Wizard",
    background="Sage",
    stats={"str": 8, "dex": 14, "con": 12, "int": 16, "wis": 13, "cha": 10},
    level=1,
    hit_die="d6"
)
```
**Expected:** Success message with HP and AC calculated
**Critical:** This must succeed for all subsequent tests

### Test 2.2: Get Character Sheet
**Tool:** `get_character_sheet`

```
get_character_sheet(campaign_id="default")
```
**Expected:** Complete character JSON with:
- `identity.name` = "Aria Stormwind"
- `identity.class_` = "Wizard"
- `health.max_hp` = calculated value
- `defense.ac` = 10 + dex_mod
- `spellcasting` present (Wizard gets spellcasting)

### Test 2.3: Calculate Modifier
**Tool:** `calculate_modifier`

```
calculate_modifier(stat_name="int")
```
**Expected:** Returns +3 (INT 16 = +3 modifier)

### Test 2.4: Get Proficiency Bonus
**Tool:** `get_proficiency_bonus`

```
get_proficiency_bonus()
```
**Expected:** Returns 2 (level 1 proficiency)

### Test 2.5: Calculate AC
**Tool:** `calculate_ac`

```
calculate_ac()
```
**Expected:** Returns calculated AC (should be 12 with DEX 14)

---

## Phase 3: Inventory Management

### Test 3.1: Get Initial Inventory
**Tool:** `get_inventory`

```
get_inventory()
```
**Expected:** Returns inventory with starter items:
- `items`: ["item_rations_5", "item_torch_1"]
- `gold`: 0
- `equipped`: all slots empty

### Test 3.2: Add Item
**Tool:** `add_item`

```
add_item(item_id="longsword", equip_to_slot="main_hand")
```
**Expected:** "Added longsword to inventory. Equipped to main_hand."

### Test 3.3: Verify Item Added
**Tool:** `get_inventory`

```
get_inventory()
```
**Expected:** "longsword" in items list, equipped.main_hand = "longsword"

### Test 3.4: Add Gold
**Tool:** `add_gold`

```
add_gold(amount=100)
```
**Expected:** "Added 100 gold. Total: 100.0 gp."

### Test 3.5: Remove Gold
**Tool:** `remove_gold`

```
remove_gold(amount=25)
```
**Expected:** "Spent 25 gold. Remaining: 75.0 gp."

### Test 3.6: Add Shield
**Tool:** `add_item`

```
add_item(item_id="shield", equip_to_slot="off_hand")
```
**Expected:** Success, shield equipped to off_hand

### Test 3.7: Recalculate AC with Shield
**Tool:** `calculate_ac`

```
calculate_ac()
```
**Expected:** Returns 14 (12 base + 2 from shield)

---

## Phase 4: Combat System

### Test 4.1: Start Combat
**Tool:** `start_combat`

```
start_combat(entities=["Goblin", "Goblin"])
```
**Expected:** "Combat started with 3 combatants. Round 1." (Player + 2 goblins)

### Test 4.2: Roll Initiative for All
**Tool:** `roll_initiative_for_all`

```
roll_initiative_for_all()
```
**Expected:** "Initiative Rolled:" with results for all combatants

### Test 4.3: Get Initiative Order
**Tool:** `get_initiative_order`

```
get_initiative_order()
```
**Expected:** Turn order with current turn marked with "->"

### Test 4.4: Make Attack
**Tool:** `make_attack`

```
make_attack(
    attacker_id="<use player ID from initiative>",
    target_id="<use goblin ID from initiative>",
    weapon="Longsword"
)
```
**Expected:** Attack result with roll, total, hit/miss, damage

### Test 4.5: Apply Damage
**Tool:** `update_hp`

```
update_hp(
    amount=5,
    type="damage",
    target_id="<goblin ID>"
)
```
**Expected:** Damage applied, HP updated

### Test 4.6: Next Turn
**Tool:** `next_turn`

```
next_turn()
```
**Expected:** "It is [next combatant]'s turn."

### Test 4.7: End Combat
**Tool:** `end_combat`

```
end_combat()
```
**Expected:** "Combat ended."

---

## Phase 5: Character Advancement

### Test 5.1: Damage Character
**Tool:** `update_hp`

```
update_hp(amount=5, type="damage")
```
**Expected:** HP reduced, message shows current/max HP

### Test 5.2: Heal Character
**Tool:** `update_hp`

```
update_hp(amount=3, type="healing")
```
**Expected:** HP increased (not exceeding max)

### Test 5.3: Add Experience
**Tool:** `add_experience`

```
add_experience(xp=300)
```
**Expected:** "Added 300 XP. Total: 300. *** LEVEL UP! *** Character is now Level 2!"

### Test 5.4: Verify Level Up
**Tool:** `get_character_sheet`

```
get_character_sheet()
```
**Expected:** `identity.level` = 2, `stats.proficiency_bonus` = 2

### Test 5.5: Update Stat
**Tool:** `update_stat`

```
update_stat(stat="str", value=10)
```
**Expected:** "Updated str to 10."

---

## Phase 6: Spellcasting (Wizard)

### Test 6.1: Get Spell Slots
**Tool:** `get_spell_slots`

```
get_spell_slots()
```
**Expected:** Returns spell slot status (Level 2 Wizard should have slots)

### Test 6.2: Cast Spell
**Tool:** `cast_spell`

```
cast_spell(spell_name="Magic Missile", level=1)
```
**Expected:** Spell cast successfully, slot consumed

### Test 6.3: Verify Slot Consumed
**Tool:** `get_spell_slots`

```
get_spell_slots()
```
**Expected:** Level 1 slot count decreased by 1

---

## Phase 7: Rest Mechanics

### Test 7.1: Use Hit Dice (Short Rest)
**Tool:** `use_hit_dice`

```
use_hit_dice(count=1)
```
**Expected:** Hit die spent, HP restored

### Test 7.2: Short Rest
**Tool:** `rest`

```
rest(type="short")
```
**Expected:** Short rest benefits applied

### Test 7.3: Long Rest
**Tool:** `rest`

```
rest(type="long")
```
**Expected:** HP fully restored, spell slots restored, hit dice partially recovered

---

## Phase 8: Skill Checks & Conditions

### Test 8.1: Skill Check
**Tool:** `make_check`

```
make_check(check_type="skill", skill_or_ability="arcana", dc=15)
```
**Expected:** Roll result with success/failure

### Test 8.2: Ability Check
**Tool:** `make_check`

```
make_check(check_type="ability", skill_or_ability="str", dc=12)
```
**Expected:** Roll result with success/failure

### Test 8.3: Apply Condition
**Tool:** `manage_conditions`

```
manage_conditions(action="apply", condition="Prone", duration=5)
```
**Expected:** "Applied condition Prone for 5 rounds."

### Test 8.4: Check Conditions
**Tool:** `manage_conditions`

```
manage_conditions(action="check")
```
**Expected:** List of active conditions

### Test 8.5: Remove Condition
**Tool:** `manage_conditions`

```
manage_conditions(action="remove", condition="Prone")
```
**Expected:** "Removed condition Prone."

---

## Phase 9: Generator Tools

### Test 9.1: Generate Monster
**Tool:** `generator_monster_tool`

```
generator_monster_tool(concept="Ancient Ice Dragon", target_cr=10.0)
```
**Expected:** Complete custom monster JSON with stats, abilities, actions

### Test 9.2: Generate Magic Item
**Tool:** `generator_item_tool`

```
generator_item_tool(rarity="rare", concept="Ring of Fire Protection")
```
**Expected:** Custom magic item JSON with mechanics and properties

### Test 9.3: Generate Location
**Tool:** `generator_location_tool`

```
generator_location_tool(type="dungeon", difficulty="hard")
```
**Expected:** Detailed location JSON with description and encounters

---

## Phase 10: Session Management

### Test 10.1: Save Session Summary
**Tool:** `save_session_summary`

```
save_session_summary(summary="Aria Stormwind defeated two goblins in the forest clearing. Found 75 gold and a mysterious longsword. Leveled up to 2!")
```
**Expected:** "Session summary saved as session_1."

### Test 10.2: Load Session History
**Tool:** `load_session_history`

```
load_session_history()
```
**Expected:** Returns formatted session log with date and summary

---

## Success Criteria

**ALL tests must pass with:**
- ✅ No "No character found" errors after character creation
- ✅ No "NoneType" errors
- ✅ Character data persists across tool calls
- ✅ Inventory changes are saved
- ✅ Combat system initializes correctly
- ✅ HP/XP updates are saved
- ✅ Spell slots are tracked correctly

## Known Limitations (Memory Backend)

⚠️ **Memory backend does NOT persist after server restart**
- All character data is lost when server stops
- Use disk backend (`STORAGE_BACKEND=disk`) for persistence across restarts

## Test Execution Notes

1. Execute tests in order (some depend on previous tests)
2. Use actual IDs returned from combat tools (don't hardcode)
3. If ANY test in Phase 2 fails, stop and report - nothing else will work
4. For memory backend, all tests must complete in one session
5. Record any error messages verbatim for debugging

## Reporting Results

Report format:
```
Phase X: [PASS/FAIL]
Test X.Y: [PASS/FAIL] - [Brief note if failed]

Total: XX/XX tests passed
```

If failures occur, include:
- Exact tool call made
- Expected result
- Actual result/error message
- Any relevant debug output
