from typing import Any, Iterator
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov
from game_map import GameMap
from input_handling import EventHandler
from entity import Entity


class Engine:
    def __init__(self, player: Entity, entities: set[Entity], game_map: GameMap, event_handler: EventHandler) -> None:
        self.player = player
        self.entities = entities
        self.game_map = game_map
        self.event_handler = event_handler
        self.update_fov()

    def handle_events(self, events: Iterator[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)

            self.update_fov()

    def update_fov(self) -> None:
        """Recompute visible area based on the player POV"""
        self.game_map.visible[:] = compute_fov(self.game_map.tiles["transparent"], self.player.info[0:2], radius=8)
        self.game_map.explored |= self.game_map.visible
    
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.entities:
            if self.game_map.visible[entity.info[0:2]]:
                console.print(*entity.info)

        context.present(console)
        console.clear()

