from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from input_handling import GameOverEventHandler
from render_order import RenderOrder
import color
if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, power: int, defense: int) -> None:
        self.max_hp = hp
        self._hp = hp
        self.power = power
        self.defense = defense

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            self.engine.message_log.add_message("You died!", color.player_die)
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            self.engine.message_log.add_message(f"{self.parent.name} is dead!", color.enemy_die)

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

