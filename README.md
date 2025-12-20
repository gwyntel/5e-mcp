# Solo D&D 5e MCP Server

### *Your Personal AI Dungeon Master Engine*

This is a specialized [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that turns your AI assistant (like Claude Desktop) into a fully capable Dungeon Master for D&D 5th Edition solo play. 

**How it works:** 
The AI tells the story, but **This Server** handles the rules. It rolls the dice, tracks your HP, manages your inventory, and remembers where you are, so the AI can focus on being a great storyteller.

---

**Authors**: Gwyneth & Gemini 3 Pro (in Antigravity Agent Harness) & GLM 4.6 (in Cline Agent Harness)

## 🚀 Getting Started (For In-Laws & friends!)

### 1. Prerequisites
You need an AI interface that supports MCP, like **Claude Desktop**.

### 2. Installation
1.  **Download this folder** to your computer.
2.  Open your AI Client configuration (e.g., `claude_desktop_config.json`).
3.  Add the `dnd-server` to your configuration:

```json
{
  "mcpServers": {
    "dnd-server": {
      "command": "python3",
      "args": ["-m", "dnd_mcp_server.server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/this/folder" 
      }
    }
  }
}
```
*(Make sure to replace `/absolute/path/...` with the real path where you saved this folder!)*

### 3. How to Play
1.  Open your AI chat.
2.  **Copy and Paste** the entire text from `system_prompt.md` into the chat.
    *   *Pro Tip: If your client supports MCP Prompts (like Claude Desktop), just type `/` and select `dnd_dm`!*
    *   *Tip: This tells the AI exactly how to use its new D&D superpowers.*
3.  Start talking! 
    *   *"I want to create a new character. I'll be a Human Fighter named Garrick."*
    *   *"I explore the dark cave."*
    *   *"I attack the goblin with my longsword!"*

---

## ✨ Features

*   **Persistent World**: Your character, loot, and progress are saved automatically. Close the chat, come back tomorrow, and pick up right where you left off.
*   **Real D&D Rules**: 
    *   **Combat**: Initiative, AC, Attack Rolls, and Damage are calculated using real 5e math.
    *   **Resting**: Short Rests heal you using Hit Dice. Long Rests restore everything.
    *   **Leveling**: Earn XP and level up to get stronger.
*   **Infinite Content**: 
    *   Encounter ANY monster from the 5e SRD (Goblins, Dragons, Liches) instantly.
    *   Find ANY magic item (Flametongue, Bag of Holding) without typing stats.
*   **Multi-Campaign Support**: Play multiple different adventures in parallel. Just give each one a unique name (e.g., "Gwyn's Campaign", "Test Run") and the server keeps their save files separate.
*   **Session Continuity**: The server remembers what happened! AI DMs can save/load session summaries to pick up the story exactly where you left off.
*   **Economy**: Track gold, buy items, and manage your wealth (`add_gold`, `remove_gold`).

## 🗺️ Roadmap

Based on comprehensive testing and user feedback, here's our development roadmap to make the 5e MCP Server even better:

### 🔄 API Consolidation (v1.1) ✅ COMPLETED
**Goal**: Reduce tool count from ~35 to ~25 for cleaner, more efficient interactions
- [x] Merge `update_hp` and `deal_damage` into unified `update_hp(amount, type, target_id, campaign_id)`
- [x] Combine `make_skill_check` and `make_ability_check` into `make_check(check_type, skill_or_ability, ...)`
- [x] Integrate level-up detection into `add_experience` to eliminate separate XP checks
- [x] Streamline `add_item` + `equip_item` workflow for new loot with `equip_to_slot` parameter
- [x] Evaluate `prepare_spell` necessity vs `cast_spell` slot tracking - integrated `prepare` parameter

### 🤖 Small LLM Compatibility (v1.2) ✅ COMPLETED
**Goal**: Enable reliable operation with local 7B-13B models
- [x] Add one-shot examples to every tool description
- [x] Create workflow guides for common sequences (combat, rest, level-up)
- [x] Implement client-side JSON schema validation
- [x] Simplify tool descriptions to <50 words each
- [x] Add constraint/validation layer with helpful error messages
  +++++++ REPLACE

### 📚 Documentation Enhancements (v1.1)
**Goal**: Clarify edge cases and improve DM guidance
- [ ] Document temporary HP damage absorption rules
- [ ] Clarify spell preparation vs casting mechanics
- [ ] Add condition duration tracking documentation
- [ ] Specify campaign ID naming conventions (alphanumeric + underscores)
- [ ] Add death save recovery path documentation
- [ ] Create "Common Workflows" section with step-by-step examples

### 🐛 Bug Fixes & Polish (v1.0.1)
**Goal**: Address issues found during comprehensive testing
- [ ] Fix HP display bug (goblins showing 187 HP instead of ~7)
- [ ] Improve initiative order formatting (add indices: "Goblin #1", "Goblin #2")
- [ ] Verify monster initialization doesn't accidentally scale HP
- [ ] Test spell slot consumption and restoration mechanics
- [ ] Validate concentration tracking functionality

### ✨ New Features (v1.3)
**Goal**: Add quality-of-life improvements based on user feedback
- [ ] Implement `generate_loot(monster_name, campaign_id)` helper tool
- [ ] Add auto-expiration for conditions with duration timers
- [ ] Create comprehensive test suite with mock wizard character
- [ ] Add loot generation based on monster CR and treasure tables
- [ ] Implement party management for multi-character campaigns

### 🚀 Performance & Stability (v1.4)
**Goal**: Optimize for production use
- [ ] Add comprehensive error handling and recovery
- [ ] Implement data validation at all entry points
- [ ] Optimize save/load performance for large campaigns
- [ ] Add backup and migration tools for save data
- [ ] Create automated testing pipeline

### 🎯 Stretch Goals (v2.0)
**Goal**: Advanced features for power users
- [ ] Multi-character party support
- [ ] Custom monster and item creation tools
- [ ] Campaign import/export (JSON, Markdown)
- [ ] Integration with external VTT platforms
- [ ] Homebrew content support system

---
**Note**: Version numbers are tentative and may shift based on development priorities. Community feedback and contributions will help shape the final roadmap!

## 🛠️ Tool Cheat Sheet
(The AI uses these automatically, but it's good to know what's happening under the hood!)

| Category | Tool | What it does |
| :--- | :--- | :--- |
| **Action** | `make_check` | Unified skill/ability checks (e.g. `make_check("skill", "athletics")`) |
| **Combat** | `start_combat` | Spawns monsters and rolls initiative. |
| **Combat** | `make_attack` | Rolls to hit vs AC. If successful, you deal damage. |
| **Character** | `get_character_sheet` | Reads your current HP, XP, and Stats. |
| **Character** | `update_hp` | Unified damage/healing/temp HP for characters or combat targets. |
| **Magic** | `cast_spell` | Uses a spell slot, tracks concentration, can prepare spells. |
| **Rest** | `rest` | Performs a Short or Long rest to recover resources. |
| **Status** | `manage_conditions` | Apply or remove conditions like "Prone" or "Exhaustion". |
| **Inventory** | `add_item` | Add items and optionally equip them in one step. |
| **Economy** | `add_gold` | Adds gold to your inventory. |

## 🎲 Solo Balancing
This system is tuned for **One Player**. 
*   **Hero Scale**: You are the main character. Death saves are dramatic.
*   **Fair Fights**: The AI is instructed to build balanced encounters (1-on-1 duels or small groups of weak foes).

---

*Happy Adventuring!*
