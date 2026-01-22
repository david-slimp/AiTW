import importlib
import json
from pathlib import Path
from typing import Awaitable, Callable, Dict, List

CommandHandler = Callable[[object, str, str], Awaitable[None]]

COMMANDS: Dict[str, CommandHandler] = {}
_MODULES: List[object] = []


def reload_from_packs(content_dir: Path) -> None:
    global COMMANDS, _MODULES

    packs_dir = content_dir / "packs"
    modules: List[object] = []

    for pack_dir in packs_dir.iterdir():
        if not pack_dir.is_dir():
            continue
        manifest_path = pack_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        commands_path = pack_dir / manifest.get("commands_path", "")
        if not commands_path.exists():
            continue
        cmd_data = json.loads(commands_path.read_text(encoding="utf-8"))
        for entry in cmd_data.get("commands", []):
            mod_name = entry.get("module")
            if not mod_name:
                continue
            mod = importlib.import_module(f"commands.{mod_name}")
            modules.append(mod)

    registry: Dict[str, CommandHandler] = {}
    for mod in modules:
        for alias in getattr(mod, "COMMANDS", []):
            registry[alias] = mod.handle

    COMMANDS = registry
    _MODULES = modules


async def dispatch(world: object, conn_id: str, cmd: str, arg: str) -> bool:
    handler = COMMANDS.get(cmd)
    if not handler:
        return False
    await handler(world, conn_id, arg)
    return True


def help_lines() -> list[str]:
    lines = ["Commands:"]
    for mod in _MODULES:
        aliases = getattr(mod, "COMMANDS", [])
        short = getattr(mod, "SHORT_DESC", "")
        if not aliases:
            continue
        primary = aliases[0]
        lines.append(f"  {primary} - {short}")
    lines.append("")
    lines.append("Tip: use HELP <command> for detailed help (e.g., HELP MOVE).")
    return lines


def help_detail(cmd: str) -> list[str]:
    cmd_u = cmd.strip().upper()
    for mod in _MODULES:
        aliases = getattr(mod, "COMMANDS", [])
        if cmd_u in aliases:
            short = getattr(mod, "SHORT_DESC", "")
            long_desc = getattr(mod, "LONG_DESC", "")
            examples = getattr(mod, "EXAMPLES", [])
            alias_list = ", ".join(aliases)
            lines = [f"{aliases[0]} - {short}", f"Aliases: {alias_list}"]
            if long_desc:
                lines.append(long_desc)
            if examples:
                lines.append("Examples:")
                for ex in examples:
                    lines.append(f"  {ex}")
            return lines
    return [f"No help found for '{cmd_u}'."]


def command_meta() -> list[dict]:
    meta: list[dict] = []
    for mod in _MODULES:
        aliases = getattr(mod, "COMMANDS", [])
        if not aliases:
            continue
        meta.append(
            {
                "name": aliases[0],
                "aliases": aliases,
                "short": getattr(mod, "SHORT_DESC", ""),
                "long": getattr(mod, "LONG_DESC", ""),
                "examples": getattr(mod, "EXAMPLES", []),
            }
        )
    return meta
