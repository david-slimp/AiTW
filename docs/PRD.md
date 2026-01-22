# PRD

## Product Overview
Adventures in The Way (AiTW) is a multiplayer, Christian-themed text adventure MMO/MUD with a web client and a Python backend. Players connect through a browser, interact via text commands, and progress through puzzles, story arcs, and spiritual growth themes.

## Goals
- Build a persistent, multiplayer world with live updates.
- Keep the game highly modular and data-driven (no hardcoded rooms/items/commands).
- Enable admins to add/edit content in-game and hot-reload content safely.
- Provide a simple, readable UI with clear situational awareness.

## Target Platform
- Backend: Python server with WebSockets on port 26472 (initial target).
- Client: Web browser.
- Deployment target: CentOS 7 (initial).
## Production Hosting
- Deploy target is configured via `.env` (server and path are authoritative).
- Public gameplay URL: https://MinistriesForChrist.net/games/
- GitHub: https://github.com/david-slimp/AiTW

## Core Gameplay Loop
Curiosity → Exploration → Hypothesis → Experiment → Payoff → New curiosity, mapped to a Christian growth arc.

## Goal Conveyance (Design Principle)
- Do not state objectives directly at the start.
- Use a scenario-driven opening: entering a church, an altar call, being given a Bible, and a general charge to “do good.”
- Use Bible reading and Holy Spirit prompts to guide players if they drift.
- REPENT should be a core command for missteps and sin/temptation loops.

## Milestones
- v0.0.1: minimal server/client wiring; single room; single item; basic HUD.
- v0.1.0 (MVP): 4 rooms, 2 items (Bible + Candle), Bible-gated room, dark-room lighting, core commands (`GO`, `LOOK`, `TAKE`, `DROP`, `INVENTORY`, `HELP`, `QUIT`).
- v0.2.x: early content packs, more rooms/items, richer puzzles, and basic admin build tools.
- v0.3.x: expanded command set (e.g., `PRAY`, `READ`), more quests/arcs, improved hinting.
- v0.5.x: persistence hardening, analytics for stuck points, refined UI panels and filters.
- v1.0.0: content-rich world with many rooms/items/puzzles, stable live updates, robust admin tooling, and polished onboarding.

## Data and Content System
- JSON-only content files.
- One JSON file per room.
- One JSON file per item prototype.
- IDs are human-readable, namespaced strings (e.g., `room:core:chapel_001`).
- Prototype + instance model for live state.
- Hot reload strategy: watch + validate + apply.
- Versioning and migrations for content schemas.
 - Items should support weight and inventory slot rules (e.g., hand, bag, ring).
 - Item instances should store mutable state (durability, charges, on/off, cooked/burnt, etc.) in runtime state, not per-file prototypes.
 - World/region maps should support: starting locations, item spawns, and per-room spawn rules.
 - Support private tutorial rooms (per-player instances) and public social rooms.

### Item Instance Schema (Draft)
This schema keeps item prototypes in JSON files and stores per-instance state in runtime.

Example instance record:
```json
{
  "instance_id": "inst:core:bible_001",
  "prototype_id": "item:core:bible",
  "location_type": "room",
  "location_id": "room:core:chapel_001",
  "quantity": 1,
  "state": {
    "durability": "intact",
    "charges": null,
    "lit": null,
    "condition": "normal"
  }
}
```

Notes:
- Use `quantity` for stacks (e.g., 100 apples).
- Use `state` for mutable values (durability, on/off, charge level, cooked/burnt, etc.).
- Do not create one file per instance; instances live in runtime state.

## Content Targets (Initial Core Release)
- Rooms: ~20–30
- Items: ~10–20
- Puzzles: ~7–12 (see `docs/puzzles.md`)

## Command Architecture (Planned)
- Prefer one module per command (e.g., `LOOK`, `INVENTORY`, `TAKE`, `DROP`, `PRAY`).
- This should be reviewed against best practices as the command router and plugin system are designed.
- Data-driven command rules first; plugins/modules only when needed.

## Modular Engine Philosophy (Reusable Command Packs)
- Server code should remain generic for text adventure/IF structure (rooms/items/world/commands).
- Different admins can supply their own content files and command packs to build a different game on the same engine.
- Standard IF command modules (LOOK/TAKE/DROP/INVENTORY/HELP) are reusable across games.
- Feature modules (e.g., lighting, combat systems) should be optional plug-ins that can be included or excluded per game.
- Long-term goal: multiple combat modules that can be swapped without changing core server code.

## UI/HUD
- Three-column layout:
  - Left: exits, who is here, items on ground.
  - Center: transcript + input.
  - Right: inventory + status.
- Live updates for players/NPCs/items.

## Tooling
- Vite + Vitest for front-end tooling and tests (target port 8008).
- TypeScript for client code.
- ESLint + Prettier for linting and formatting.
- Husky for git hooks.
- Git/GitHub for version control (URL TBD).
- Howler (audio/SFX) is a future consideration only.

## Conventions
- CHANGELOG dates use `YYYY-MM-DD`.
