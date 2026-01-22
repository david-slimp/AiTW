COMMANDS = ["INVENTORY", "INV", "I"]
SHORT_DESC = "Show what you are carrying."
LONG_DESC = "Lists items in your inventory."
EXAMPLES = ["INVENTORY"]


async def handle(world, conn_id: str, _arg: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if not player:
        return

    items = world._inventory_item_summaries(player)
    if not items:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You are carrying nothing."})
    else:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You are carrying: " + ", ".join(items)})

    await world._send_inventory_state(conn_id)
