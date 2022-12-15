from __future__ import annotations
from typing import TYPE_CHECKING
from exception import Impossible
import color
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor, Item


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
            raise Impossible("No target to melee")

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
        if (
            not self.engine.game_map.in_bounds(*self.position) or
            not self.engine.game_map.tiles["walkable"][*self.position] or
            self.blocking_entity
        ):
            raise Impossible("That way is blocked")

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class ItemAction(Action):
    def __init__(self, entity: Actor, item: Item, target_position: tuple[int, int] | None = None) -> None:
        super().__init__(entity)
        self.item = item
        if not target_position:
            target_position = self.entity.position
        self.target_position = target_position

    @property
    def target_actor(self) -> Actor | None:
        """Return actor at this location"""
        return self.engine.game_map.get_actor_at(self.target_position)

    def perform(self) -> None:
        """Invoke item ability"""
        self.item.consumable.activate(self)


class PickupAction(Action):
    """Pickup an item and add it to inventory, if there is enougth space for it"""

    def perform(self) -> None:
        actor_position = self.entity.position
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_position == item.position:
                if len(inventory.items) >= inventory.capacity:
                    raise Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)
                self.engine.message_log.add_message(f"You picked up the {item.name}")
                return

        raise Impossible("There is nothing to pick up here.")


class DropAction(ItemAction):
    def perform(self) -> None:
        self.entity.inventory.drop(self.item)

