# Adventures in The Way (Minimal Multiplayer Prototype)

This is the **smallest end-to-end** version:
- ALL THIS ORIGINAL / LEGACY CODE WAS 1-SHOT FROM CHATGPT 5.2 (2026-01-19) - very good initial base and worked the first time!
- Python backend (FastAPI + WebSockets) on **port 26472**
- 1 room: `room:core:chapel_001`
- 1 item prototype: `item:core:bible`
- 1 item instance on the ground: `inst:core:bible_001`
- Players identified by IP (no login yet)
- Basic 3-column web UI (left: room awareness, center: transcript/input, right: inventory)

## Run locally

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 26472
```

Open:
- `http://localhost:26472`

## Commands
- `HELP`
- `LOOK` (or `L`)
- `TAKE BIBLE`
- `DROP BIBLE`
- `INVENTORY` (or `I`)

## Content files
- Rooms: `content/packs/core/rooms/*.json`
- Items: `content/packs/core/items.json`

The server hot-reloads content (best-effort) using `watchfiles` (inotify-backed on Linux), with a polling fallback.

## Notes
- This is intentionally minimal. Next steps are: additional rooms/exits, more items, NPCs, and an admin build command set.
