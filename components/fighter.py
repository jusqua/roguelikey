from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from render_order import RenderOrder
import color

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(
        self, hp: int, base_power: int = 0, base_defense: int = 0, base_luck: int = 0
    ) -> None:
        self.max_hp = hp
        self._hp = hp
        self.base_power = base_power
        self.base_defense = base_defense
        self.base_luck = base_luck

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def luck(self) -> int:
        return self.base_luck + self.luck_bonus

    @property
    def power_bonus(self) -> int:
        return self.parent.equipment.power_bonus if self.parent.equipment else 0

    @property
    def defense_bonus(self) -> int:
        return self.parent.equipment.defense_bonus if self.parent.equipment else 0

    @property
    def luck_bonus(self) -> int:
        return self.parent.equipment.luck_bonus if self.parent.equipment else 0

    def heal(self, amount: int) -> int:
        new_hp_value = min(self.hp + amount, self.max_hp)
        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def die(self) -> None:
        if self.engine.player is self.parent:
            self.engine.message_log.add_message("You died!", color.player_die)
        else:
            self.engine.message_log.add_message(
                f"{self.parent.name} is dead!", color.enemy_die
            )

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.player.level.add_xp(self.parent.level.xp_given)
