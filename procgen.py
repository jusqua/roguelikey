from __future__ import annotations
from typing import Iterator, TYPE_CHECKING
from random import choice, randint
from game_map import GameMap
import tile_types
import tcod

if TYPE_CHECKING:
    from entity import Entity


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> tuple[int, int]:
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)

    @property
    def inner(self) -> tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return (
            self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1
        )


def tunnel_between(start: tuple[int, int], end: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Create a L-shaped tunnel between those points"""
    corner = choice(((end[0], start[1]), (start[0], end[1])))

    for x, y in tcod.los.bresenham(start, corner).tolist():
        yield x, y
    for x, y in tcod.los.bresenham(corner, end).tolist():
        yield x, y


def rectangular_room(room_limits: tuple[int, int], map_size: tuple[int, int]) -> RectangularRoom:
    """Generate a room based on given specs"""
    room_size = randint(*room_limits), randint(*room_limits)
    room_position = randint(0, map_size[0] - room_size[0] - 1), randint(0, map_size[1] - room_size[1] - 1)
    return RectangularRoom(*room_position, *room_size)


def generate_dungeon(max_rooms: int, room_limits: tuple[int, int], map_size: tuple[int, int], player: Entity) -> GameMap:
    """Generates a new dungeon map"""
    dungeon = GameMap(*map_size)

    rooms: list[RectangularRoom] = [rectangular_room(room_limits, map_size)]
    dungeon.tiles[rooms[0].inner] = tile_types.floor
    player.x, player.y = rooms[0].center

    for _ in range(max_rooms - 1):
        new_room = rectangular_room(room_limits, map_size)

        if any(new_room.intersects(room) for room in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        for position in tunnel_between(rooms[-1].center, new_room.center):
            dungeon.tiles[position] = tile_types.floor

        rooms.append(new_room)

    return dungeon

