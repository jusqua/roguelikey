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


class ActionWithDirection(Action):
    def __init__(self, dx: int, dy: int) -> None:
        self.dx, self.dy = dx, dy


class MeleeAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = entity.x + self.dx, entity.y + self.dy
        target = engine.game_map.get_blocking_entity_at_position(dest)
        if not target:
            return

        print(f"{target.name} was DESTROYED! Of course not.")


class MovementAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = entity.x + self.dx, entity.y + self.dy

        if not engine.game_map.in_bounds(*dest):
            return
        if not engine.game_map.tiles["walkable"][*dest]:
            return
        if engine.game_map.get_blocking_entity_at_position(dest):
            return

        entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self, engine: Engine, entity: Entity) -> None:
        dest = entity.x + self.dx, entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_position(dest):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)

