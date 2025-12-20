# D&D 5e MCP Server - Common Workflows

This guide provides step-by-step workflows for common D&D scenarios using the MCP tools. These workflows are designed to help small LLMs understand the proper sequence of tool calls for various situations.

## 🎯 Combat Workflow

**Starting Combat:**
1. `start_combat(["Goblin", "2 Wolves"])` - Begin combat with monsters
2. `roll_initiative_for_all()` - Roll initiative for all combatants
3. `get_initiative_order()` - Display turn order with HP status

**Combat Turn (Player):**
1. `make_attack("pc_abc123", "goblin_1", "Longsword")` - Attack target
2. `update_hp(8, "damage", "goblin_1")` - Apply damage if hit
3. `next_turn()` - Advance to next combatant

**Combat Turn (Monster):**
1. `make_attack("goblin_1", "pc_abc123", "Scimitar")` - Monster attacks
2. `update_hp(6, "damage")` - Apply damage to player
3. `make_death_save()` - If player at 0 HP, roll death saves

**Ending Combat:**
1. `add_experience(150)` - Award XP for defeating monsters
2. `end_combat()` - Clean up combat state

## 🏨 Rest Workflow

**Short Rest (1 hour):**
1. `rest("short")` - Perform short rest
2. `use_hit_dice(2)` - Spend hit dice to heal (optional)
3. `get_character_sheet()` - Check updated HP and resources

**Long Rest (8 hours):**
1. `rest("long")` - Perform long rest
2. `get_character_sheet()` - Verify full HP and spell slot restoration

## ⚔️ Level Up Workflow

**After Gaining Enough XP:**
1. `get_character_sheet()` - Check current stats
2. `update_stat("str", 16)` - Increase ability scores
3. `calculate_ac()` - Recalculate Armor Class with new stats
4. `get_character_sheet()` - Verify updated character sheet

## 🛡️ Equipment Management Workflow

**Acquiring New Item:**
1. `add_item("magic_sword", "main_hand")` - Add and equip item
2. `get_inventory()` - Verify item added and equipped
3. `calculate_ac()` - Update AC if armor/weapon changed

**Managing Inventory:**
1. `get_inventory()` - View current items and equipment
2. `unequip_item("main_hand")` - Remove current item
3. `equip_item("new_weapon", "main_hand")` - Equip different item

## ✨ Spellcasting Workflow

**Preparing Spells (Wizard/Cleric):**
1. `get_spell_list("Wizard")` - View available spells
2. `prepare_spell("Fireball")` - Add spell to prepared list
3. `get_spell_slots()` - Check available spell slots

**Casting Spells:**
1. `cast_spell("Fireball", 3, True, True)` - Cast with concentration and preparation
2. `get_spell_slots()` - Verify slot consumption
3. `get_character_sheet()` - Check concentration status

## 🔍 Skill Check Workflow

**Making Ability Checks:**
1. `make_check("ability", "strength", 15)` - Raw ability check
2. `make_check("skill", "athletics", 12, True)` - Skill check with advantage

**Complex Skill Challenge:**
1. `make_check("skill", "perception", 14)` - Notice something
2. `make_check("skill", "investigation", 13)` - Investigate further
3. `make_check("skill", "stealth", 15, False, True)` - Stealth with disadvantage

## 💰 Economy Workflow

**Buying Items:**
1. `get_inventory()` - Check current gold
2. `remove_gold(50)` - Pay for item
3. `add_item("potion", None)` - Add purchased item

**Selling Loot:**
1. `add_gold(100)` - Receive payment
2. `remove_item("gem")` - Remove sold item

## 🎲 Damage & Healing Workflow

**Taking Damage:**
1. `update_hp(12, "damage")` - Apply damage
2. `get_character_sheet()` - Check new HP total
3. `make_death_save()` - Start death saves if at 0 HP

**Healing:**
1. `update_hp(8, "healing")` - Apply healing
2. `manage_conditions("remove", "Unconscious")` - Remove unconscious condition
3. `get_character_sheet()` - Verify recovery

## 📋 Session Management Workflow

**Starting Session:**
1. `load_session_history()` - Review previous sessions
2. `get_character_sheet()` - Check current character state

**Ending Session:**
1. `save_session_summary("Explored dungeon, defeated goblins, found treasure")` - Save story progress
2. `get_character_sheet()` - Final state snapshot

## 🔄 Error Recovery Workflow

**If Tool Fails:**
1. `get_character_sheet()` - Verify current state
2. Check error message for missing requirements
3. Retry with corrected parameters

**Common Error Patterns:**
- "No character found" → Use `create_character()` first
- "No active combat" → Use `start_combat()` first  
- "Not in inventory" → Use `add_item()` first
- "No spell slots remaining" → Use `rest("long")` to restore

## 📝 Pro Tips

**Always Check State:**
- Call `get_character_sheet()` before major actions
- Call `get_initiative_order()` each combat round
- Call `get_spell_slots()` before casting spells

**Use Examples:**
- Each tool description includes usage examples
- Follow the exact parameter formats shown
- Copy-paste examples when learning the system

**Sequence Matters:**
- Combat: Start → Initiative → Attack → Damage → Next Turn
- Rest: Short/Long → Heal → Check Resources  
- Spells: Prepare → Check Slots → Cast → Track Effects

These workflows ensure reliable operation with small LLMs by providing clear, repeatable patterns for common D&D scenarios.
