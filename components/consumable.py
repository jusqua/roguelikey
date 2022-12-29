from __future__ import annotations
from typing import TYPE_CHECKING
from components.ai import ConfusedEnemy
from components.base_component import BaseComponent
from components.inventory import Inventory
from action import Action, ItemAction
from exception import Impossible
from input_handling import (
    SingleRangedAttackHandler,
    AreaRangedAttackHandler,
    BaseEventHandler,
)
import color

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def action(self, consumer: Actor) -> Action | BaseEventHandler | None:
        """Try to resolve action for this consumable"""
        return ItemAction(consumer, self.parent)

    def activate(self, action: ItemAction) -> None:
        """
        Invoke item action
        `action` is the context for this activation
        """
        raise NotImplementedError

    def consume(self) -> None:
        """Remove the consumed item form inventory"""
        item = self.parent
        inventory = item.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(item)


class HealingConsumable(Consumable):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered <= 0:
            raise Impossible("Your health already full.")

        self.engine.message_log.add_message(
            f"You consume {self.parent.name} and recover {amount_recovered} HP!",
            color.health_recovered,
        )
        self.consume()


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int) -> None:
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.engine.game_map.visible[actor.position]:
                distance = consumer.distance_between(*actor.position)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if not target:
            raise Impossible("No enemy is close enough to strike.")

        self.engine.message_log.add_message(
            f"A lightning bolt strikes the {target.name} with loud thunder, for {self.damage} damage!"
        )
        target.fighter.take_damage(self.damage)
        self.consume()


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int) -> None:
        self.number_of_turns = number_of_turns

    def action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine, lambda position: ItemAction(consumer, self.parent, position)
        )

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_position]:
            raise Impossible("You cannot target something that you cannot see.")
        if not target:
            raise Impossible("You must select a target.")
        if consumer is target:
            raise Impossible("You cannot target yourself.")

        self.engine.message_log.add_message(
            f"The {target.name} eyes look vacant, as it starts to stumble around!"
        )
        target.ai = ConfusedEnemy(target, target.ai, self.number_of_turns)
        self.consume()


class FireballDamageConsumable(Consumable):
    def __init__(self, radius: int, damage: int) -> None:
        self.radius = radius
        self.damage = damage

    def action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            self.radius,
            lambda position: ItemAction(consumer, self.parent, position),
        )

    def activate(self, action: ItemAction) -> None:
        if not self.engine.game_map.visible[action.target_position]:
            raise Impossible("You cannot target something that you cannot see.")

        is_target_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance_between(*action.target_position) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                is_target_hit = True

        if not is_target_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()
