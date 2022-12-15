from __future__ import annotations
from typing import TYPE_CHECKING
from copy import deepcopy
from render_order import RenderOrder
from components.inventory import Inventory
if TYPE_CHECKING:
    from game_map import GameMap
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.consumable import Consumable


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
        render_order: RenderOrder = RenderOrder.CORPSE
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
    
    def place(self, position: tuple[int, int], game_map: GameMap | None = None) -> None:
        """Handle moving across new location, i.e. game maps"""
        self.x, self.y = position
        if game_map:
            if hasattr(self, "parent"):
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
        name: str = "<Unnamed>",
        char: str = "?",
        color: tuple[int, int, int] = (255, 255, 255),
        position: tuple[int, int] = (0, 0),
        blocks_movement: bool = True,
        game_map: GameMap | None = None,
        inventory: Inventory | None = None
    ) -> None:
        super().__init__(name, char, color, position, blocks_movement, game_map, RenderOrder.ACTOR)

        self.ai: BaseAI | None = ai(self)

        self.fighter = fighter
        self.fighter.parent = self

        if inventory is None:
            inventory = Inventory(0)

        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        """Verify if this actor can perform actions"""
        return bool(self.ai)


class Item(Entity):
    parent: Inventory | GameMap

    def __init__(self, consumable: Consumable, name: str = "<Unnamed>", char: str = "?", color: tuple[int, int, int] = (255, 255, 255), position: tuple[int, int] = (0, 0), blocks_movement: bool = False, parent: GameMap | None = None) -> None:
        super().__init__(name, char, color, position, blocks_movement, parent, RenderOrder.ITEM)
        self.consumable = consumable
        self.consumable.parent = self

