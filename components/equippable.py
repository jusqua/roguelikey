from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from equipment_type import EquipmentType
if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0
    ) -> None:
        self.equipment_type = equipment_type
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 2, 1)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 3)


class Axe(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 4, -1)


class Robe(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, defense_bonus=1)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, defense_bonus=2)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, -1, 3)
