COMMANDS = ["MOVE", "GO"]
SHORT_DESC = "Move to another room."
LONG_DESC = "Usage: MOVE <direction>. Moves you through a valid exit."
EXAMPLES = ["GO RIGHT"]


async def handle(world, conn_id: str, direction: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if not player:
        return
    if not direction:
        await world.send_to_conn(conn_id, {"type": "log", "text": "Go where?"})
        return

    room = world.rooms.get(player.room_id)
    if not room:
        await world.send_to_conn(conn_id, {"type": "log", "text": "(World) You are nowhere."})
        return

    dir_key = direction.strip().lower()
    dest_id = room.exits.get(dir_key)
    if not dest_id:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You can't go that way."})
        return

    if dest_id not in world.rooms:
        await world.send_to_conn(conn_id, {"type": "log", "text": "(World) That exit leads nowhere."})
        return

    # Leave current room
    world.room_players.setdefault(player.room_id, set()).discard(player.id)
    await world.broadcast_room(
        player.room_id,
        {"type": "log", "text": f"{world._display_name(player)} leaves."},
        exclude_player_id=player.id,
    )

    # Enter new room
    player.room_id = dest_id
    world.room_players.setdefault(dest_id, set()).add(player.id)

    await world.broadcast_room(
        dest_id,
        {"type": "log", "text": f"{world._display_name(player)} arrives."},
        exclude_player_id=player.id,
    )

    await world._send_init(conn_id)
