from __future__ import annotations
from typing import Iterator, TYPE_CHECKING
from random import choice, choices, randint
from game_map import GameMap
import tile_types
import entity_factory
import tcod

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


max_items_per_floor = [(1, 1), (4, 2)]
max_enemies_per_floor = [(1, 2), (4, 3), (6, 5)]

items_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factory.lesser_health_potion, 35)],
    2: [
        (entity_factory.confusion_scroll, 10),
        (entity_factory.health_potion, 15),
        (entity_factory.rust_ring, 5),
    ],
    4: [
        (entity_factory.lightning_scroll, 25),
        (entity_factory.sword, 5),
        (entity_factory.health_potion, 35),
        (entity_factory.jeweled_ring, 5),
        (entity_factory.leather_cap, 5),
    ],
    6: [
        (entity_factory.fireball_scroll, 25),
        (entity_factory.leather_armor, 15),
    ],
    8: [
        (entity_factory.axe, 5),
        (entity_factory.chain_mail, 5),
        (entity_factory.elden_ring, 5),
    ],
    10: [
        (entity_factory.greater_health_potion, 15),
        (entity_factory.viking_helmet, 15),
    ],
}
enemies_chances: dict[int, list[tuple[Entity, int]]] = {
    0: [(entity_factory.orc, 80)],
    3: [(entity_factory.troll, 15)],
    5: [(entity_factory.troll, 30), (entity_factory.goblin, 60)],
    7: [(entity_factory.troll, 60), (entity_factory.goblin, 80)],
    9: [(entity_factory.hobgoblin, 15)],
}


def get_entities_at_random(
    weighted_chances_by_floor: dict[int, list[tuple[Entity, int]]],
    number_of_entities: int,
    current_floor: int,
) -> list[Entity]:
    entities: list[Entity] = []
    entity_weighted_chance_values: list[int] = []

    for key, values in weighted_chances_by_floor.items():
        if key > current_floor:
            break

        for entity, weighted_chance in values:
            entities.append(entity)
            entity_weighted_chance_values.append(weighted_chance)

    chosen_entities = choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )
    return chosen_entities


def get_max_value_for_floor(
    max_value_per_floor: list[tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_per_floor:
        if floor_minimum > floor:
            break
        current_value = value

    return current_value


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
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(
    start: tuple[int, int], end: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    """Create a L-shaped tunnel between those points"""
    corner = choice(((end[0], start[1]), (start[0], end[1])))

    for x, y in tcod.los.bresenham(start, corner).tolist():
        yield x, y
    for x, y in tcod.los.bresenham(corner, end).tolist():
        yield x, y


def rectangular_room(
    room_limits: tuple[int, int], map_size: tuple[int, int]
) -> RectangularRoom:
    """Generate a room based on given specs"""
    room_size = randint(*room_limits), randint(*room_limits)
    room_position = randint(2, map_size[0] - room_size[0] - 3), randint(
        2, map_size[1] - room_size[1] - 3
    )
    return RectangularRoom(*room_position, *room_size)


def get_random_position_at(room: RectangularRoom) -> tuple[int, int]:
    return randint(room.x1 + 1, room.x2 - 1), randint(room.y1 + 1, room.y2 - 1)


def place_entities(room: RectangularRoom, dungeon: GameMap, current_floor: int) -> None:
    number_of_enemies = randint(
        0, get_max_value_for_floor(max_enemies_per_floor, current_floor)
    )
    number_of_items = randint(
        0, get_max_value_for_floor(max_items_per_floor, current_floor)
    )

    enemies = get_entities_at_random(enemies_chances, number_of_enemies, current_floor)
    items = get_entities_at_random(items_chances, number_of_items, current_floor)

    for entity in enemies + items:
        position = get_random_position_at(room)
        if not any(position == entity.position for entity in dungeon.entities):
            entity.spawn(dungeon, position)


def generate_dungeon(
    max_rooms: int,
    room_limits: tuple[int, int],
    map_size: tuple[int, int],
    engine: Engine,
) -> GameMap:
    """Generates a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_size, entities=[player])

    rooms: list[RectangularRoom] = [rectangular_room(room_limits, map_size)]
    dungeon.tiles[rooms[0].inner] = tile_types.floor
    player.place(rooms[0].center, dungeon)

    for _ in range(max_rooms - 1):
        new_room = rectangular_room(room_limits, map_size)
        if any(new_room.intersects(room) for room in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor
        for position in tunnel_between(rooms[-1].center, new_room.center):
            dungeon.tiles[position] = tile_types.floor
        place_entities(new_room, dungeon, engine.game_world.current_floor)

        last_room_center = new_room.center
        dungeon.tiles[last_room_center] = tile_types.down_stairs
        dungeon.down_stairs_location = last_room_center

        rooms.append(new_room)

    return dungeon
