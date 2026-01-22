COMMANDS = ["QUIT"]
SHORT_DESC = "Save and exit."
LONG_DESC = "Saves your state and closes the connection."
EXAMPLES = ["QUIT"]


async def handle(world, conn_id: str, _arg: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if player:
        world._save_player(player)
    await world.send_to_conn(conn_id, {"type": "log", "text": "Goodbye."})
    await world.disconnect_player(conn_id)
