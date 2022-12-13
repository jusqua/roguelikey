from __future__ import annotations
from typing import TYPE_CHECKING

# Prevent circular import, and use for only type checking
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def __init__(self, entity: Entity) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        """
        Perform this action with the objects to determine its scope

        `self.engine` is the scope this action being performed in
        `self.entity` is the object performing action

        This method must be overrided by subclasses
        """
        raise NotImplementedError


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit


class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx, self.dy = dx, dy

    @property
    def position(self) -> tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(self.position)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return

        print(f"{target.name} was DESTROYED! Of course not.")


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        if not self.engine.game_map.in_bounds(*self.position):
            return
        if not self.engine.game_map.tiles["walkable"][*self.position]:
            return
        if self.blocking_entity:
            return

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

