from __future__ import annotations
from typing import Iterator, TYPE_CHECKING
from random import choice, randint, random
from game_map import GameMap
import tile_types
import entity_factory
import tcod
if TYPE_CHECKING:
    from engine import Engine


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


def get_random_position_at(room: RectangularRoom) -> tuple[int, int]:
    return randint(room.x1 + 1, room.x2 - 1), randint(room.y1 + 1, room.y2 - 1)


def place_entities(room: RectangularRoom, dungeon: GameMap, max_enemies_per_room: int, max_items_per_room: int) -> None:
    number_of_enemies = randint(0, max_enemies_per_room)
    number_of_items = randint(0, max_items_per_room)

    for _ in range(number_of_enemies):
        x, y = get_random_position_at(room)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random() < 0.8:
                entity_factory.orc.spawn(dungeon, (x, y))
            else:
                entity_factory.troll.spawn(dungeon, (x, y))

    for _ in range(number_of_items):
        x, y = get_random_position_at(room)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            match random():
                case n if n < 0.7:
                    entity_factory.health_potion.spawn(dungeon, (x, y))
                case n if n < 0.8:
                    entity_factory.fireball_scroll.spawn(dungeon, (x, y))
                case n if n < 0.9:
                    entity_factory.confusion_scroll.spawn(dungeon, (x, y))
                case _:
                    entity_factory.lightning_scroll.spawn(dungeon, (x, y))


def generate_dungeon(
        max_rooms: int,
        max_enemies_per_room: int,
        max_items_per_room: int,
        room_limits: tuple[int, int],
        map_size: tuple[int, int],
        engine: Engine
    ) -> GameMap:
    """Generates a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_size, entities=[player])

    rooms: list[RectangularRoom] = [rectangular_room(room_limits, map_size)]
    dungeon.tiles[rooms[0].inner] = tile_types.floor
    player.place(rooms[0].center, dungeon)
    center_of_last_room = rooms[0].center

    for _ in range(max_rooms - 1):
        new_room = rectangular_room(room_limits, map_size)

        if any(new_room.intersects(room) for room in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        for position in tunnel_between(rooms[-1].center, new_room.center):
            dungeon.tiles[position] = tile_types.floor

        center_of_last_room = new_room.center

        place_entities(new_room, dungeon, max_enemies_per_room, max_items_per_room)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.down_stairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon

