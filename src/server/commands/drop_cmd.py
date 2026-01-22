COMMANDS = ["DROP"]
SHORT_DESC = "Drop an item from your inventory."
LONG_DESC = "Usage: DROP <thing>. Moves an item from your inventory to the room."
EXAMPLES = ["DROP BIBLE"]


async def handle(world, conn_id: str, what: str) -> None:
    player = world._get_player_for_conn(conn_id)
    if not player:
        return

    if not what:
        await world.send_to_conn(conn_id, {"type": "log", "text": "Drop what?"})
        return

    inst_id = world._find_item_in_inventory_by_name(player, what)
    if not inst_id:
        await world.send_to_conn(conn_id, {"type": "log", "text": "You aren't carrying that."})
        return

    world._move_item_instance(inst_id, to_type="room", to_id=player.room_id)

    proto = world.item_protos.get(world.item_instances[inst_id].proto_id)
    item_name = proto.name if proto else "that"

    await world.send_to_conn(conn_id, {"type": "log", "text": f"Dropped: {item_name}."})
    await world.broadcast_room(
        player.room_id,
        {"type": "log", "text": f"{world._display_name(player)} drops {item_name}."},
        exclude_player_id=player.id,
    )

    await world._send_inventory_state(conn_id)
    await world._broadcast_room_state(player.room_id)
