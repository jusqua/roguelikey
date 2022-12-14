from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov
from input_handling import MainGameEventHandler
if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handling import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor) -> None:
        self.player = player
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.logs: list[str] = ["", "", "Game starts!"]

    def handle_enemy_turn(self) -> None:
        for enemy in set(self.game_map.actors) - {self.player}:
            if enemy.ai:
                enemy.ai.perform()

    def update_fov(self) -> None:
        """Recompute visible area based on the player POV"""
        self.game_map.visible[:] = compute_fov(self.game_map.tiles["transparent"], self.player.info[0:2], radius=8)
        self.game_map.explored |= self.game_map.visible

    def new_log(self, txt: str) -> None:
        self.logs.append(txt)
        self.logs.pop(0)

    def display_hud(self, console: Console) -> None:
        console.print(1, 47, f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}")

        console.print(40, 46, "-" * 13 + "Logs" + "-" * 13)
        console.print(40, 47, self.logs[-1][:30])
        console.print(40, 48, self.logs[-2][:30])
        console.print(40, 49, self.logs[-3][:30])
    
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        self.display_hud(console)

        context.present(console)
        console.clear()

