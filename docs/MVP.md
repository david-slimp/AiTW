# MVP

## Summary
Adventures in The Way (AiTW) is a multiplayer, Christian-themed text adventure MMO/MUD with a web client and a Python backend. The MVP focuses on a minimal, data-driven world and a simple UI, while keeping the architecture modular and extensible.

## MVP Goals
- Prove the core loop works: connect, see the world, act, and observe updates.
- Keep all content data-driven with zero hardcoded rooms/items.
- Establish a clean modular code structure that supports future growth.

## MVP Scope (v0.1.0)
- Backend: Python server with WebSockets; authoritative world state in RAM.
- Client: basic 3-column web UI (left: room/exits/players/items, center: transcript + input, right: inventory).
- Identity: IP-based player identity (no login yet).
- World: four rooms total, including one gated by the Bible and one dark room.
- Items: two items (Bible and Candle) that can be `TAKE`/`DROP`.
- Live updates: arrivals, departures, item movement.

## MVP Commands
- `LOOK`, `HELP`, `INVENTORY` (`INV`/`I`), `TAKE`, `DROP`, `GO`, `QUIT`.
- Movement via a simple `GO <direction>` form (no shorthand yet).

## MVP Puzzle Gates
- Bible required to enter a specific room (gate applies both directions).
- Candle provides light in an otherwise dark room; without it, the room description is not visible.

## Content Data Format
- JSON files only.
- One file per room (e.g., `room:core:chapel_001.json`).
- One file per item prototype (e.g., `item:core:bible.json`).
- IDs are human-readable, namespaced strings.
- Prototype + instance model for live state.

## Command Architecture (MVP Direction)
- Prefer one module per command (e.g., `LOOK`, `INVENTORY`, `TAKE`, `DROP`, `PRAY`).
- This is a working hypothesis; validate against best practices as we build out the command router and extensibility model.

## Tooling (MVP)
- Vite + Vitest for front-end tooling and tests.
- TypeScript for client-side strictness.
- ESLint + Prettier for consistent code quality and formatting.
