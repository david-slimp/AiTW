COMMANDS = ["TAKE", "GET"]
SHORT_DESC = "Pick up an item."
LONG_DESC = "Usage: TAKE <thing>. Moves an item from the room to your inventory."
EXAMPLES = ["TAKE BIBLE"]


async def handle(world, conn_id: str, what: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if not player:
        return

    if not what:
        await world.send_to_conn(conn_id, {"type": "log", "text": "Take what?"})
        return

    inst_id = world._find_item_in_room_by_name(player.room_id, what)
    if not inst_id:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You don't see that here."})
        return

    world._move_item_instance(inst_id, to_type="player", to_id=player.id)

    proto = world.item_protos.get(world.item_instances[inst_id].proto_id)
    item_name = proto.name if proto else "that"

    await world.send_to_conn(conn_id, {"type": "log", "text": f"Taken: {item_name}."})
    await world.broadcast_room(
        player.room_id,
        {"type": "log", "text": f"{world._display_name(player)} picks up {item_name}."},
        exclude_player_id=player.id,
    )

    await world._send_inventory_state(conn_id)
    await world._broadcast_room_state(player.room_id)
