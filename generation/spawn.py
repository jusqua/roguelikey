from __future__ import annotations
from typing import TYPE_CHECKING
from random import choice, choices, randint
import entity_factory

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap
    from generation.rooms import Room

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


def populate_room(dungeon: GameMap, room: Room, floor: int) -> None:
    number_of_enemies = randint(0, get_floor_max_value(max_enemies_per_floor, floor))
    number_of_items = randint(0, get_floor_max_value(max_items_per_floor, floor))

    enemies = get_entities_at_random(enemies_chances, number_of_enemies, floor)
    items = get_entities_at_random(items_chances, number_of_items, floor)

    for entity in enemies + items:
        position = choice(list(room.inner))
        if not any(position == entity.position for entity in dungeon.entities):
            entity.spawn(dungeon, position)
