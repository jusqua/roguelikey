from __future__ import annotations
from typing import TYPE_CHECKING

# Prevent circular import, and use for only type checking
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """
        Perform this action with the objects to determine its scope

        `engine` is the scope this action being performed in
        `entity` is the object performing action

        This method must be overrided by subclasses
        """
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit


class MovementAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = entity.x + self.dx, entity.y + self.dy

        if not engine.game_map.in_bounds(*dest):
            return
        if not engine.game_map.tiles["walkable"][*dest]:
            return

        entity.move(self.dx, self.dy)

