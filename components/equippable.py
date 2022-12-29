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
        defense_bonus: int = 0,
        luck_bonus: int = 0,
    ) -> None:
        self.equipment_type = equipment_type
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.luck_bonus = luck_bonus

    @property
    def description(self) -> str:
        modifiers: list[str] = []
        if self.power_bonus:
            signal = "+" if self.power_bonus > 0 else ""
            modifiers.append(f"{signal}{self.power_bonus} attack")
        if self.defense_bonus:
            signal = "+" if self.defense_bonus > 0 else ""
            modifiers.append(f"{signal}{self.defense_bonus} defense")
        if self.luck_bonus:
            signal = "+" if self.luck_bonus > 0 else ""
            modifiers.append(f"{signal}{self.luck_bonus} luck")

        if not len(modifiers):
            return "No modifiers"
        return "\n".join(modifiers)


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 1, 0)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 2)


class Axe(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.WEAPON, 3, -1)


class Robe(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, defense_bonus=1)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, defense_bonus=2)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.ARMOR, -1, 4)


class Hood(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.HELMET)


class LeatherCap(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.HELMET, defense_bonus=1)


class VikingHelmet(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.HELMET, 1, 2)


class RustRing(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.RING, luck_bonus=2)


class JeweledRing(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.RING, luck_bonus=5)


class EldenRing(Equippable):
    def __init__(self) -> None:
        super().__init__(EquipmentType.RING, luck_bonus=10)
