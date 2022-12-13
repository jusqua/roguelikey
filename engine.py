from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov
from input_handling import EventHandler
if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap


class Engine:
    game_map: GameMap

    def __init__(self, player: Entity) -> None:
        self.player = player
        self.event_handler = EventHandler(self)

    def handle_enemy_turn(self) -> None:
        for enemy in self.game_map.entities - {self.player}:
            print(f"{enemy.name} stay stoned for its sake.")

    def update_fov(self) -> None:
        """Recompute visible area based on the player POV"""
        self.game_map.visible[:] = compute_fov(self.game_map.tiles["transparent"], self.player.info[0:2], radius=8)
        self.game_map.explored |= self.game_map.visible
    
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        context.present(console)
        console.clear()

