from __future__ import annotations
from typing import TYPE_CHECKING
from random import choice, choices, randint
from game_map import GameMap
from generation import build
from generation.rooms import EllipticalRoom, RectangularRoom, Room
import tile_types
import entity_factory

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
    7: [
        (entity_factory.troll, 60),
        (entity_factory.goblin, 80),
        (entity_factory.hobgoblin, 15),
    ],
    9: [(entity_factory.golem, 5)],
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


def get_floor_max_value(max_value_list: list[tuple[int, int]], floor: int) -> int:
    for floor_min, value in max_value_list:
        if floor < floor_min:
            return value
    return max_value_list[-1][1]


def generate_room(room_limits: tuple[int, int], map_size: tuple[int, int]) -> Room:
    w, h = randint(*room_limits), randint(*room_limits)
    x, y = randint(2, map_size[0] - w - 3), randint(2, map_size[1] - h - 3)
    room_types = [RectangularRoom, EllipticalRoom]
    return choice(room_types)(x, y, w, h)


def populate_room(dungeon: GameMap, room: Room, floor: int) -> None:
    number_of_enemies = randint(0, get_floor_max_value(max_enemies_per_floor, floor))
    number_of_items = randint(0, get_floor_max_value(max_items_per_floor, floor))

    enemies = get_entities_at_random(enemies_chances, number_of_enemies, floor)
    items = get_entities_at_random(items_chances, number_of_items, floor)

    for entity in enemies + items:
        position = choice(list(room.inner))
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
