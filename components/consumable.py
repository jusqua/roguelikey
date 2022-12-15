from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from components.inventory import Inventory
from action import Action, ItemAction
from exception import Impossible
import color
if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def action(self, consumer: Actor) -> Action | None:
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

        if amount_recovered > 0:
            self.engine.message_log.add_message(f"You consume {self.parent.name} and recover {amount_recovered} HP!", color.health_recovered)
            self.consume()
        else:
            raise Impossible("Your health already full.")


