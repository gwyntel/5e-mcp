# Solo D&D 5e MCP Server

### *Your Personal AI Dungeon Master Engine*

This is a specialized [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that turns your AI assistant (like Claude Desktop) into a fully capable Dungeon Master for D&D 5th Edition solo play. 

**How it works:** 
The AI tells the story, but **This Server** handles the rules. It rolls the dice, tracks your HP, manages your inventory, and remembers where you are, so the AI can focus on being a great storyteller.

---

**Authors**: Gwyneth & Gemini 3 Pro (in Antigravity Agent Harness)

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

## 🛠️ Tool Cheat Sheet
(The AI uses these automatically, but it's good to know what's happening under the hood!)

| Category | Tool | What it does |
| :--- | :--- | :--- |
| **Action** | `make_skill_check` | Rolls d20 + Mod + Proficiency (e.g. Acrobatics) |
| **Combat** | `start_combat` | Spawns monsters and rolls initiative. |
| **Combat** | `make_attack` | Rolls to hit vs AC. If successful, you deal damage. |
| **Character** | `get_character_sheet` | Reads your current HP, XP, and Stats. |
| **Magic** | `cast_spell` | Uses a spell slot and tracks concentration. |
| **Rest** | `rest` | Performs a Short or Long rest to recover resources. |
| **Status** | `manage_conditions` | Apply or remove conditions like "Prone" or "Exhaustion". |
| **Economy** | `add_gold` | Adds gold to your inventory. |

## 🎲 Solo Balancing
This system is tuned for **One Player**. 
*   **Hero Scale**: You are the main character. Death saves are dramatic.
*   **Fair Fights**: The AI is instructed to build balanced encounters (1-on-1 duels or small groups of weak foes).

---

*Happy Adventuring!*
