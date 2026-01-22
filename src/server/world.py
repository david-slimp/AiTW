from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import WebSocket

from commands import registry


# ---------------------------
# Config + Data Models
# ---------------------------


@dataclass(frozen=True)
class WorldConfig:
    content_dir: Path
    data_dir: Path
    hot_reload_poll_seconds: int = 300  # 5 minutes


@dataclass
class RoomProto:
    id: str
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)  # direction -> room_id


@dataclass
class ItemProto:
    id: str
    name: str
    short: str
    description: str
    verbs: Set[str] = field(default_factory=set)


@dataclass
class ItemInstance:
    id: str
    proto_id: str
    location_type: str  # "room" or "player"
    location_id: str


@dataclass
class PlayerState:
    id: str
    ip: str
    room_id: str
    inventory: Set[str] = field(default_factory=set)  # instance ids


# ---------------------------
# World Engine (Minimal)
# ---------------------------


class World:
    def __init__(self, cfg: WorldConfig):
        self.cfg = cfg

        # Prototypes (hot-reloadable)
        self.rooms: Dict[str, RoomProto] = {}
        self.item_protos: Dict[str, ItemProto] = {}

        # Live instances/state (preserved across proto reloads)
        self.item_instances: Dict[str, ItemInstance] = {}
        self.room_contents: Dict[str, Set[str]] = {}  # room_id -> instance ids

        # Presence
        self.players: Dict[str, PlayerState] = {}  # player_id -> state
        self.room_players: Dict[str, Set[str]] = {}  # room_id -> player_ids

        # Connections
        self.connections: Dict[str, WebSocket] = {}  # conn_id -> ws
        self.conn_to_player: Dict[str, str] = {}  # conn_id -> player_id
        self.ip_to_conn: Dict[str, str] = {}  # ip -> conn_id (one active conn per IP)
        self._conn_seq = 0

        self._reload_task: Optional[asyncio.Task] = None
        self._last_seen_mtimes: Dict[str, float] = {}

        # Defaults (overridden by world.json when present)
        self.start_room_id = ""
        self.initial_instances: List[ItemInstance] = []

    async def start(self) -> None:
        (self.cfg.data_dir / "players").mkdir(parents=True, exist_ok=True)
        await self.reload_content(initial=True)
        self._ensure_initial_instances()

        self._reload_task = asyncio.create_task(self._hot_reload_loop())

    async def stop(self) -> None:
        if self._reload_task:
            self._reload_task.cancel()
            try:
                await self._reload_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        # Best effort: save players
        for player in list(self.players.values()):
            self._save_player(player)

    # ---------------------------
    # Content Loading + Hot Reload
    # ---------------------------

    async def reload_content(self, initial: bool = False) -> None:
        """Load prototypes from content packs.

        This is designed to be safe to call while players are online:
        - prototypes replace prototypes
        - live instances are NOT reset
        """
        packs_dir = self.cfg.content_dir / "packs"
        if not packs_dir.exists():
            raise RuntimeError(f"Missing content directory: {packs_dir}")

        new_rooms: Dict[str, RoomProto] = {}
        new_items: Dict[str, ItemProto] = {}

        # Minimal: load all packs
        for pack_dir in packs_dir.iterdir():
            if not pack_dir.is_dir():
                continue

            manifest_path = pack_dir / "manifest.json"
            if not manifest_path.exists():
                continue

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            rooms_path = pack_dir / manifest.get("rooms_path", "rooms")
            items_path = pack_dir / manifest.get("items_path", "items.json")
            world_path = pack_dir / manifest.get("world_path", "world.json")

            # Rooms (per-room files)
            if rooms_path.exists():
                for room_file in rooms_path.glob("*.json"):
                    room_data = json.loads(room_file.read_text(encoding="utf-8"))
                    self._validate_room(room_data, source=str(room_file))
                    rid = room_data["id"]
                    exits = room_data.get("exits", {}) or {}
                    # exits may be {}, or a dict of direction -> {to, ...}; for now allow direction -> str
                    normalized_exits: Dict[str, str] = {}
                    for d, v in exits.items():
                        if isinstance(v, str):
                            normalized_exits[d.lower()] = v
                        elif isinstance(v, dict) and "to" in v:
                            normalized_exits[d.lower()] = str(v["to"])

                    new_rooms[rid] = RoomProto(
                        id=rid,
                        name=room_data.get("name", rid),
                        description=room_data.get("description", ""),
                        exits=normalized_exits,
                    )

            # Items (directory or single file)
            if items_path.exists():
                if items_path.is_dir():
                    for item_file in items_path.glob("*.json"):
                        item = json.loads(item_file.read_text(encoding="utf-8"))
                        self._validate_item_proto(item, source=str(item_file))
                        pid = item["id"]
                        verbs = set(v.upper() for v in item.get("verbs", []) or [])
                        new_items[pid] = ItemProto(
                            id=pid,
                            name=item.get("name", pid),
                            short=item.get("short", item.get("name", pid)),
                            description=item.get("description", ""),
                            verbs=verbs,
                        )
                else:
                    items_data = json.loads(items_path.read_text(encoding="utf-8"))
                    self._validate_items(items_data, source=str(items_path))
                    for item in items_data.get("items", []):
                        pid = item["id"]
                        verbs = set(v.upper() for v in item.get("verbs", []) or [])
                        new_items[pid] = ItemProto(
                            id=pid,
                            name=item.get("name", pid),
                            short=item.get("short", item.get("name", pid)),
                            description=item.get("description", ""),
                            verbs=verbs,
                        )

        # World config (start room + initial instances)
        self._load_world_config(world_path, new_rooms, new_items)
        registry.reload_from_packs(self.cfg.content_dir)

        if self.start_room_id not in new_rooms:
            raise RuntimeError(
                f"Start room '{self.start_room_id}' not found in loaded content."
            )

        # Swap prototypes atomically
        self.rooms = new_rooms
        self.item_protos = new_items

        # Ensure room containers exist
        for rid in self.rooms.keys():
            self.room_contents.setdefault(rid, set())
            self.room_players.setdefault(rid, set())

        if not initial:
            # notify players with a soft message (no spam)
            await self._broadcast_global({"type": "log", "text": "(World) Content updated."})

    def _ensure_initial_instances(self) -> None:
        """Create initial item instances from world config if missing."""
        for inst in self.initial_instances:
            if inst.id in self.item_instances:
                continue
            self.item_instances[inst.id] = inst
            if inst.location_type == "room":
                self.room_contents.setdefault(inst.location_id, set()).add(inst.id)

    async def _hot_reload_loop(self) -> None:
        """Best-effort hot reload.

        CentOS 7 supports inotify. We'll try watchfiles for immediate reload,
        and keep a polling fallback.
        """
        # Try immediate watcher
        try:
            from watchfiles import awatch

            async for _changes in awatch(self.cfg.content_dir, stop_event=asyncio.Event()):
                # Debounce slightly so batch uploads settle
                await asyncio.sleep(0.3)
                try:
                    await self.reload_content(initial=False)
                except Exception as e:
                    await self._broadcast_global({"type": "log", "text": f"(World) Reload failed: {e}"})
        except asyncio.CancelledError:
            return
        except Exception:
            # Poll fallback
            try:
                while True:
                    await asyncio.sleep(self.cfg.hot_reload_poll_seconds)
                    try:
                        # Simple mtime scan to avoid needless reloads
                        if self._content_changed_since_last_scan():
                            await self.reload_content(initial=False)
                    except Exception as e:
                        await self._broadcast_global({"type": "log", "text": f"(World) Reload failed: {e}"})
            except asyncio.CancelledError:
                return

    def _content_changed_since_last_scan(self) -> bool:
        changed = False
        for p in self.cfg.content_dir.rglob("*.json"):
            try:
                mtime = p.stat().st_mtime
            except Exception:
                continue
            key = str(p)
            if key not in self._last_seen_mtimes:
                self._last_seen_mtimes[key] = mtime
                changed = True
            elif mtime != self._last_seen_mtimes[key]:
                self._last_seen_mtimes[key] = mtime
                changed = True
        return changed

    # ---------------------------
    # Connections + Presence
    # ---------------------------

    async def connect_player(self, ip: str, websocket: WebSocket) -> str:
        # One active connection per IP for now (as requested)
        if ip in self.ip_to_conn:
            old = self.ip_to_conn[ip]
            await self.send_to_conn(old, {"type": "log", "text": "(Server) Reconnected elsewhere; closing this session."})
            await self.disconnect_player(old)

        self._conn_seq += 1
        conn_id = f"conn:{ip}:{self._conn_seq}"
        self.connections[conn_id] = websocket
        self.ip_to_conn[ip] = conn_id

        player = self._load_or_create_player(ip)
        self.players[player.id] = player
        self.conn_to_player[conn_id] = player.id

        # Add to room presence
        self.room_players.setdefault(player.room_id, set()).add(player.id)

        # Send initial state
        await self._send_init(conn_id)

        # Broadcast join
        await self.broadcast_room(
            player.room_id,
            {
                "type": "log",
                "text": f"{self._display_name(player)} arrives.",
            },
            exclude_player_id=player.id,
        )
        await self._broadcast_room_state(player.room_id)

        return conn_id

    async def disconnect_player(self, conn_id: str) -> None:
        player_id = self.conn_to_player.get(conn_id)
        ip = None
        if player_id and player_id in self.players:
            player = self.players[player_id]
            ip = player.ip
            # Remove from room
            if player.room_id in self.room_players:
                self.room_players[player.room_id].discard(player_id)

            # Persist
            self._save_player(player)

            # Broadcast leave
            await self.broadcast_room(
                player.room_id,
                {"type": "log", "text": f"{self._display_name(player)} leaves."},
                exclude_player_id=player_id,
            )
            await self._broadcast_room_state(player.room_id)

            # Keep player state in memory for simplicity; could evict here

        # Cleanup connection
        ws = self.connections.pop(conn_id, None)
        self.conn_to_player.pop(conn_id, None)

        if ip and self.ip_to_conn.get(ip) == conn_id:
            self.ip_to_conn.pop(ip, None)

        try:
            if ws:
                await ws.close()
        except Exception:
            pass

    # ---------------------------
    # Command Handling
    # ---------------------------

    async def handle_command(self, conn_id: str, text: str) -> None:
        player = self._get_player_for_conn(conn_id)
        if not player:
            return

        raw = text.strip()
        if not raw:
            return

        # Echo command into transcript (client-side could do this too)
        await self.send_to_conn(conn_id, {"type": "log", "text": f"> {raw}"})

        cmd, arg = self._split_cmd(raw)
        cmd_u = cmd.upper()

        handled = await registry.dispatch(self, conn_id, cmd_u, arg)
        if handled:
            return
        await self.send_to_conn(conn_id, {"type": "log", "text": "I don't understand that yet. Try HELP."})

    # ---------------------------
    # Messaging helpers
    # ---------------------------

    async def send_to_conn(self, conn_id: str, payload: Dict[str, Any]) -> None:
        ws = self.connections.get(conn_id)
        if not ws:
            return
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            # ignore, disconnect handler will clean up
            pass

    async def broadcast_room(self, room_id: str, payload: Dict[str, Any], exclude_player_id: Optional[str] = None) -> None:
        for pid in list(self.room_players.get(room_id, set())):
            if exclude_player_id and pid == exclude_player_id:
                continue
            conn = self._conn_for_player(pid)
            if conn:
                await self.send_to_conn(conn, payload)

    async def _broadcast_global(self, payload: Dict[str, Any]) -> None:
        for conn_id in list(self.connections.keys()):
            await self.send_to_conn(conn_id, payload)

    async def _send_init(self, conn_id: str) -> None:
        player = self._get_player_for_conn(conn_id)
        if not player:
            return

        room = self.rooms.get(player.room_id)
        if not room:
            player.room_id = self.start_room_id
            room = self.rooms.get(self.start_room_id)
        if not room:
            await self.send_to_conn(conn_id, {"type": "log", "text": "(World) No valid start room loaded."})
            return

        payload = {
            "type": "init",
            "player": {"id": player.id, "ip": player.ip, "room_id": player.room_id},
            "room": self._room_state(room.id),
            "inventory": self._inventory_state(player),
        }
        await self.send_to_conn(conn_id, payload)

        # also show initial look
        await self.send_to_conn(conn_id, {"type": "log", "text": "Welcome to Adventures in The Way (minimal)."})
        await self.send_to_conn(conn_id, {"type": "log", "text": "Type HELP for commands."})
        await registry.dispatch(self, conn_id, "LOOK", "")

    async def _broadcast_room_state(self, room_id: str) -> None:
        state = {"type": "room_state", "room": self._room_state(room_id)}
        await self.broadcast_room(room_id, state)

    async def _send_inventory_state(self, conn_id: str) -> None:
        player = self._get_player_for_conn(conn_id)
        if not player:
            return
        await self.send_to_conn(conn_id, {"type": "inv_state", "inventory": self._inventory_state(player)})

    def _room_state(self, room_id: str) -> Dict[str, Any]:
        room = self.rooms.get(room_id)
        if not room:
            return {"id": room_id, "name": "Unknown", "description": "", "exits": {}, "players": [], "items": []}

        players = [
            self._display_name(self.players[pid])
            for pid in sorted(self.room_players.get(room_id, set()))
            if pid in self.players
        ]
        items = self._room_item_summaries(room_id)

        return {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "exits": room.exits,
            "players": players,
            "items": items,
        }

    def _inventory_state(self, player: PlayerState) -> Dict[str, Any]:
        return {
            "items": self._inventory_item_summaries(player)
        }

    # ---------------------------
    # Item lookup + movement
    # ---------------------------

    def _room_item_summaries(self, room_id: str) -> List[str]:
        out: List[str] = []
        for inst_id in sorted(self.room_contents.get(room_id, set())):
            inst = self.item_instances.get(inst_id)
            if not inst:
                continue
            proto = self.item_protos.get(inst.proto_id)
            out.append(proto.short if proto else inst_id)
        return out

    def _inventory_item_summaries(self, player: PlayerState) -> List[str]:
        out: List[str] = []
        for inst_id in sorted(player.inventory):
            inst = self.item_instances.get(inst_id)
            if not inst:
                continue
            proto = self.item_protos.get(inst.proto_id)
            out.append(proto.short if proto else inst_id)
        return out

    def _find_item_in_room_by_name(self, room_id: str, query: str) -> Optional[str]:
        q = query.strip().lower()
        for inst_id in self.room_contents.get(room_id, set()):
            inst = self.item_instances.get(inst_id)
            if not inst:
                continue
            proto = self.item_protos.get(inst.proto_id)
            if not proto:
                continue
            if self._matches_item_query(proto, q):
                return inst_id
        return None

    def _find_item_in_inventory_by_name(self, player: PlayerState, query: str) -> Optional[str]:
        q = query.strip().lower()
        for inst_id in player.inventory:
            inst = self.item_instances.get(inst_id)
            if not inst:
                continue
            proto = self.item_protos.get(inst.proto_id)
            if not proto:
                continue
            if self._matches_item_query(proto, q):
                return inst_id
        return None

    @staticmethod
    def _matches_item_query(proto: ItemProto, q: str) -> bool:
        if q == proto.name.lower():
            return True
        if q == proto.short.lower():
            return True
        # Allow partial match
        if q and (q in proto.name.lower() or q in proto.short.lower()):
            return True
        return False

    def _move_item_instance(self, inst_id: str, to_type: str, to_id: str) -> None:
        inst = self.item_instances[inst_id]
        # Remove from old location
        if inst.location_type == "room":
            self.room_contents.get(inst.location_id, set()).discard(inst_id)
        elif inst.location_type == "player":
            p = self.players.get(inst.location_id)
            if p:
                p.inventory.discard(inst_id)

        # Add to new
        inst.location_type = to_type
        inst.location_id = to_id
        if to_type == "room":
            self.room_contents.setdefault(to_id, set()).add(inst_id)
        elif to_type == "player":
            p = self.players.get(to_id)
            if p:
                p.inventory.add(inst_id)

    # ---------------------------
    # Player persistence (minimal)
    # ---------------------------

    def _player_path(self, ip: str) -> Path:
        safe_ip = ip.replace(":", "_")
        return self.cfg.data_dir / "players" / f"{safe_ip}.json"

    def _load_or_create_player(self, ip: str) -> PlayerState:
        pid = f"player:ip:{ip}"
        ppath = self._player_path(ip)
        if ppath.exists():
            try:
                data = json.loads(ppath.read_text(encoding="utf-8"))
                room_id = data.get("room_id") or self.start_room_id
                inv = set(data.get("inventory", []) or [])
                # NOTE: inventory instances may not exist after restart; we'll ignore missing
                inv = {iid for iid in inv if iid in self.item_instances}
                if room_id not in self.rooms:
                    room_id = self.start_room_id
                return PlayerState(id=pid, ip=ip, room_id=room_id, inventory=inv)
            except Exception:
                pass
        return PlayerState(id=pid, ip=ip, room_id=self.start_room_id)

    def _save_player(self, player: PlayerState) -> None:
        ppath = self._player_path(player.ip)
        data = {
            "schema_version": 1,
            "player_id": player.id,
            "room_id": player.room_id,
            "inventory": sorted(player.inventory),
        }
        tmp = ppath.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(ppath)

    # ---------------------------
    # Utilities
    # ---------------------------

    def _get_player_for_conn(self, conn_id: str) -> Optional[PlayerState]:
        pid = self.conn_to_player.get(conn_id)
        if not pid:
            return None
        return self.players.get(pid)

    def _conn_for_player(self, player_id: str) -> Optional[str]:
        # reverse lookup (one conn per ip)
        p = self.players.get(player_id)
        if not p:
            return None
        return self.ip_to_conn.get(p.ip)

    @staticmethod
    def _split_cmd(raw: str) -> Tuple[str, str]:
        parts = raw.strip().split(maxsplit=1)
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    @staticmethod
    def _display_name(player: PlayerState) -> str:
        # Minimal: friendly name from IP
        return f"Disciple@{player.ip}"

    @staticmethod
    def _validate_room(data: Dict[str, Any], source: str = "") -> None:
        required = ["schema_version", "content_version", "id", "name", "description"]
        for k in required:
            if k not in data:
                raise ValueError(f"Room missing '{k}' ({source})")
        if not isinstance(data["id"], str) or not data["id"].startswith("room:"):
            raise ValueError(f"Room id must be a string starting with 'room:' ({source})")

    @staticmethod
    def _validate_items(data: Dict[str, Any], source: str = "") -> None:
        required = ["schema_version", "content_version", "items"]
        for k in required:
            if k not in data:
                raise ValueError(f"Items file missing '{k}' ({source})")
        if not isinstance(data["items"], list):
            raise ValueError(f"Items 'items' must be a list ({source})")
        for item in data["items"]:
            for k in ["id", "name", "short", "description"]:
                if k not in item:
                    raise ValueError(f"Item missing '{k}' ({source})")
            if not isinstance(item["id"], str) or not item["id"].startswith("item:"):
                raise ValueError(f"Item id must start with 'item:' ({source})")

    @staticmethod
    def _validate_item_proto(data: Dict[str, Any], source: str = "") -> None:
        required = ["schema_version", "content_version", "id", "name", "short", "description"]
        for k in required:
            if k not in data:
                raise ValueError(f"Item proto missing '{k}' ({source})")
        if not isinstance(data["id"], str) or not data["id"].startswith("item:"):
            raise ValueError(f"Item id must start with 'item:' ({source})")

    def _load_world_config(
        self,
        path: Path,
        rooms: Dict[str, RoomProto],
        items: Dict[str, ItemProto],
    ) -> None:
        if not path.exists():
            raise RuntimeError(f"Missing world config: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        self._validate_world_config(data, source=str(path))
        self.start_room_id = data["start_room_id"]
        self.initial_instances = []
        for inst in data.get("initial_instances", []):
            iid = inst["instance_id"]
            pid = inst["prototype_id"]
            if pid not in items:
                raise RuntimeError(f"World config references missing item: {pid}")
            self.initial_instances.append(
                ItemInstance(
                    id=iid,
                    proto_id=pid,
                    location_type=inst["location_type"],
                    location_id=inst["location_id"],
                )
            )

    @staticmethod
    def _validate_world_config(data: Dict[str, Any], source: str = "") -> None:
        required = ["schema_version", "content_version", "start_room_id", "initial_instances"]
        for k in required:
            if k not in data:
                raise ValueError(f"World config missing '{k}' ({source})")
        if not isinstance(data["start_room_id"], str) or not data["start_room_id"].startswith("room:"):
            raise ValueError(f"World start_room_id must start with 'room:' ({source})")
        if not isinstance(data["initial_instances"], list):
            raise ValueError(f"World initial_instances must be a list ({source})")
        for inst in data["initial_instances"]:
            for k in ["instance_id", "prototype_id", "location_type", "location_id"]:
                if k not in inst:
                    raise ValueError(f"World instance missing '{k}' ({source})")
