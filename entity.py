from __future__ import annotations
from copy import deepcopy
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from game_map import GameMap


class Entity:
    """
    Generic object to represent general propouses entities
    """
    def __init__(self,
            name: str = "<Unnamed>",
            char: str = "?",
            color: tuple[int, int, int] = (255, 255, 255),
            position: tuple[int, int] = (0, 0),
            blocks_movement: bool = True
        ) -> None:
        self.name = name
        self.char = char
        self.color = color
        self.x, self.y = position
        self.blocks_movement = blocks_movement

    def spawn(self, game_map: GameMap, position: tuple[int, int]) -> Entity:
        """Spawn a copy of this instance at the given location in the game map"""
        clone = deepcopy(self)
        clone.x, clone.y = position
        game_map.entities.add(clone)
        return clone

    def move(self, dx: int, dy: int) -> None:
        """
        Move entity by given amount
        """
        self.x += dx
        self.y += dy

    @property
    def info(self) -> tuple[int, int, str, tuple[int, int, int]]:
        return self.x, self.y, self.char, self.color

