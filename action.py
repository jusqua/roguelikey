from __future__ import annotations
from typing import TYPE_CHECKING
import color
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor


class Action:
    def __init__(self, entity: Actor) -> None:
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


class WaitAction(Action):
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx, self.dy = dx, dy

    @property
    def position(self) -> tuple[int, int]:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(self.position)

    @property
    def target_actor(self) -> Actor | None:
        """Return the actor at this action destination"""
        return self.engine.game_map.get_actor_at(self.position)


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return

        damage = self.entity.fighter.power - target.fighter.defense
        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"

        if self.entity is self.engine.player:
            attack_color = color.player_attack
        else:
            attack_color = color.enemy_attack

        if damage > 0:
            self.engine.message_log.add_message(f"{attack_description} for {damage} hit points.", attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f"{attack_description} but does no damage.", attack_color)


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
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

