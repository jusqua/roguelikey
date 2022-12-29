from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.console import Console
from tcod.map import compute_fov
from message_log import MessageLog
from exception import Impossible
import lzma
import pickle

from render_functions import render_status

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor) -> None:
        self.player = player
        self.message_log = MessageLog()
        self.mouse_location: tuple[int, int] = (0, 0)
        self.is_mouse_motion: bool = False

    def handle_enemy_turn(self) -> None:
        for enemy in set(self.game_map.actors) - {self.player}:
            if enemy.ai:
                try:
                    enemy.ai.perform()
                except Impossible:
                    pass

    def save_as(self, filename: str) -> None:
        """Save this engine instance in compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as file:
            file.write(save_data)

    def update_fov(self) -> None:
        """Recompute visible area based on the player POV"""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"], self.player.info[0:2], radius=8
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console)
        render_status(console, self)
