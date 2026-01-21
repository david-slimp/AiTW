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

## Core Gameplay Loop
Curiosity → Exploration → Hypothesis → Experiment → Payoff → New curiosity, mapped to a Christian growth arc.

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

## Command Architecture (Planned)
- Prefer one module per command (e.g., `LOOK`, `INVENTORY`, `TAKE`, `DROP`, `PRAY`).
- This should be reviewed against best practices as the command router and plugin system are designed.
- Data-driven command rules first; plugins/modules only when needed.

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
