COMMANDS = ["HELP"]
SHORT_DESC = "Show available commands."
LONG_DESC = "Usage: HELP or HELP <command>. Shows command list or detailed help for a specific command, including aliases and examples."
EXAMPLES = ["HELP", "HELP MOVE"]


async def handle(world, conn_id: str, _arg: str) -> None:
    from . import registry

    arg = (_arg or "").strip()
    lines = registry.help_detail(arg) if arg else registry.help_lines()
    for ln in lines:
        await world.send_to_conn(conn_id, {"type": "log", "text": ln})
