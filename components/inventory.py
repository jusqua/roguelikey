from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items: list[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes item from inventory and puts it to current player location
        """
        self.items.remove(item)
        item.place(self.parent.position, self.game_map)
        self.engine.message_log.add_message(f"You dropped the {item.name}.")

