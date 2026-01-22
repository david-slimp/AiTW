COMMANDS = ["LOOK", "L"]
SHORT_DESC = "Show the current room description."
LONG_DESC = "Redisplays the room name, description, exits, and visible items."
EXAMPLES = ["LOOK"]


async def handle(world, conn_id: str, _arg: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if not player:
        return
    room = world.rooms.get(player.room_id)
    if not room:
        await world.send_to_conn(conn_id, {"type": "log", "text": "(World) You are nowhere."})
        return

    await world.send_to_conn(conn_id, {"type": "log", "text": f"{room.name}"})
    await world.send_to_conn(conn_id, {"type": "log", "text": room.description})

    items = world._room_item_summaries(player.room_id)
    if items:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You see here: " + ", ".join(items)})

    others = [
        world._display_name(world.players[pid])
        for pid in sorted(world.room_players.get(player.room_id, set()))
        if pid != player.id and pid in world.players
    ]
    if others:
        await world.send_to_conn(conn_id, {"type": "log", "text": "Also here: " + ", ".join(others)})

    await world._broadcast_room_state(player.room_id)
