from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from equipment_type import EquipmentType
if TYPE_CHECKING:
    from entity import Item, Actor


class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Item | None = None, armor: Item | None = None) -> None:
        self.weapon = weapon
        self.armor = armor

    @property
    def defense_bonus(self) -> int:
        bonus = 0
        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.defense_bonus
        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.defense_bonus

        return bonus

    @property
    def power_bonus(self) -> int:
        bonus = 0
        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.power_bonus
        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.power_bonus

        return bonus

    def is_item_equipped(self, item: Item) -> bool:
        return self.weapon is item or self.armor is item

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item: Item = getattr(self, slot)
        if current_item is not None:
            self.unequip_from_slot(slot, add_message)
        setattr(self, slot, item)

        if add_message:
            self.parent.game_map.engine.message_log.add_message(f"You equip the {item.name}.")

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item: Item = getattr(self, slot)
        setattr(self, slot, None)

        if add_message:
            self.parent.game_map.engine.message_log.add_message(f"You remove the {current_item.name}.")

    def toggle_equip(self, item: Item, add_message: bool = True) -> None:
        if not item.equippable:
            return

        match item.equippable.equipment_type:
            case EquipmentType.WEAPON:
                slot = "weapon"
            case EquipmentType.ARMOR:
                slot = "armor"

        if getattr(self, slot) is item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, item, add_message)

