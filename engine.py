from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.console import Console
from tcod.map import compute_fov
from input_handling import MainGameEventHandler
from render_functions import render_bar, render_name_at_mouse
from message_log import MessageLog
from exception import Impossible
if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handling import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor) -> None:
        self.player = player
        self.message_log = MessageLog()
        self.mouse_location: tuple[int, int] = (0, 0)
        self.event_handler: EventHandler = MainGameEventHandler(self)

    def handle_enemy_turn(self) -> None:
        for enemy in set(self.game_map.actors) - {self.player}:
            if enemy.ai:
                try:
                    enemy.ai.perform()
                except Impossible:
                    pass

    def update_fov(self) -> None:
        """Recompute visible area based on the player POV"""
        self.game_map.visible[:] = compute_fov(self.game_map.tiles["transparent"], self.player.info[0:2], radius=8)
        self.game_map.explored |= self.game_map.visible
    
    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console, (21, 45), (40, 5))
        render_bar(console, self.player.fighter.hp, self.player.fighter.max_hp, 20)
        render_name_at_mouse(console, self, (21, 44))

