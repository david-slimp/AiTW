from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from world import World, WorldConfig

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = BASE_DIR / "data"
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"

app = FastAPI(title="Adventures in The Way (Minimal)")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

world = World(WorldConfig(content_dir=CONTENT_DIR, data_dir=DATA_DIR))


@app.on_event("startup")
async def on_startup() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    await world.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await world.stop()


@app.get("/")
async def index() -> HTMLResponse:
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws.accept()

    ip = ws.client.host if ws.client else "unknown"
    conn_id = await world.connect_player(ip=ip, websocket=ws)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                await world.send_to_conn(conn_id, {"type": "log", "text": "(Server) Invalid JSON."})
                continue

            if data.get("type") == "cmd":
                text = str(data.get("text", "")).strip()
                if text:
                    await world.handle_command(conn_id, text)
            else:
                await world.send_to_conn(conn_id, {"type": "log", "text": "(Server) Unknown message type."})

    except WebSocketDisconnect:
        await world.disconnect_player(conn_id)
    except Exception as e:
        await world.send_to_conn(conn_id, {"type": "log", "text": f"(Server) Error: {e}"})
        await world.disconnect_player(conn_id)
