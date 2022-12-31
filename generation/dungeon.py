from __future__ import annotations
from typing import TYPE_CHECKING
from random import choice, randint
from game_map import GameMap
from generation import build
from generation.spawn import populate_room
from generation.rooms import EllipticalRoom, OvalRoom, RectangularRoom, Room
import tile_types

if TYPE_CHECKING:
    from engine import Engine


def generate_room(room_limits: tuple[int, int], map_size: tuple[int, int]) -> Room:
    w, h = randint(*room_limits), randint(*room_limits)
    x, y = randint(2, map_size[0] - w - 3), randint(2, map_size[1] - h - 3)
    room_types = [RectangularRoom, OvalRoom, EllipticalRoom]
    return choice(room_types)(x, y, w, h)


def generate_dungeon(
    max_rooms: int,
    room_limits: tuple[int, int],
    map_size: tuple[int, int],
    engine: Engine,
) -> GameMap:
    """Generates a new dungeon map"""
    player = engine.player
    current_floor = engine.game_world.current_floor
    dungeon = GameMap(engine, map_size, entities=[player])

    rooms: list[Room] = [generate_room(room_limits, map_size)]
    for position in rooms[0].inner:
        dungeon.tiles[position] = tile_types.floor
    player.place(rooms[0].center, dungeon)

    for _ in range(max_rooms - 1):
        new_room = generate_room(room_limits, map_size)
        if any(new_room.intersects(room) for room in rooms):
            continue

        for position in new_room.inner:
            dungeon.tiles[position] = tile_types.floor
        for position in build.tunnel_between(rooms[-1].center, new_room.center):
            dungeon.tiles[position] = tile_types.floor

        populate_room(dungeon, new_room, current_floor)

        rooms.append(new_room)

    dungeon.tiles[rooms[-1].center] = tile_types.down_stairs
    dungeon.down_stairs_location = rooms[-1].center

    return dungeon
