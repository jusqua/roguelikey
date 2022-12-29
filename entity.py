from __future__ import annotations
from typing import TYPE_CHECKING
from copy import deepcopy
from math import sqrt
from render_order import RenderOrder
from components.inventory import Inventory
from components.equipment import Equipment

if TYPE_CHECKING:
    from game_map import GameMap
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.consumable import Consumable
    from components.equippable import Equippable
    from components.level import Level


class Entity:
    """
    Generic object to represent general propouses entities
    """

    parent: GameMap

    def __init__(
        self,
        name: str = "<Unnamed>",
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        position: tuple[int, int] = (0, 0),
        blocks_movement: bool = False,
        parent: GameMap | None = None,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ) -> None:
        self.name = name
        self.char = char
        self.color = color
        self.x, self.y = position
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            self.parent = parent
            parent.entities.add(self)

    def spawn(self, game_map: GameMap, position: tuple[int, int]) -> Entity:
        """Spawn a copy of this instance at the given location in the game map"""
        clone = deepcopy(self)
        clone.x, clone.y = position
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    def distance_between(self, x: int, y: int) -> float:
        """Return the distance between self and other position"""
        return sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def place(self, position: tuple[int, int], game_map: GameMap | None = None) -> None:
        """Handle moving across new location, i.e. game maps"""
        self.x, self.y = position
        if game_map:
            if hasattr(self, "parent") and not isinstance(self.parent, Inventory):
                self.game_map.entities.remove(self)
            self.parent = game_map
            game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        """
        Move entity by given amount
        """
        self.x += dx
        self.y += dy

    @property
    def info(self) -> tuple[int, int, str, tuple[int, int, int]]:
        return self.x, self.y, self.char, self.color

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    @property
    def game_map(self) -> GameMap:
        return self.parent


class Actor(Entity):
    def __init__(
        self,
        ai: type[BaseAI],
        fighter: Fighter,
        level: Level,
        name: str = "<Unnamed>",
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        position: tuple[int, int] = (0, 0),
        blocks_movement: bool = True,
        game_map: GameMap | None = None,
        inventory: Inventory | None = None,
        equipment: Equipment | None = None,
    ) -> None:
        super().__init__(
            name, char, color, position, blocks_movement, game_map, RenderOrder.ACTOR
        )

        self.ai: BaseAI | None = ai(self)

        self.fighter = fighter
        self.fighter.parent = self

        self.level = level
        self.level.parent = self

        if inventory is None:
            inventory = Inventory(0)

        self.inventory = inventory
        self.inventory.parent = self

        if equipment is None:
            equipment = Equipment()

        self.equipment = equipment
        self.equipment.parent = self

    @property
    def is_alive(self) -> bool:
        """Verify if this actor can perform actions"""
        return bool(self.ai)


class Item(Entity):
    parent: Inventory | GameMap

    def __init__(
        self,
        name: str = "<Unnamed>",
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        position: tuple[int, int] = (0, 0),
        blocks_movement: bool = False,
        parent: GameMap | None = None,
        consumable: Consumable | None = None,
        equippable: Equippable | None = None,
    ) -> None:
        super().__init__(
            name, char, color, position, blocks_movement, parent, RenderOrder.ITEM
        )

        self.consumable = consumable
        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable
        if self.equippable:
            self.equippable.parent = self
