from typing import Any, Iterator
from tcod.context import Context
from tcod.console import Console
from game_map import GameMap
from input_handling import EventHandler
from entity import Entity


class Engine:
    def __init__(self, player: Entity, entities: set[Entity], game_map: GameMap, event_handler: EventHandler) -> None:
        self.player = player
        self.entities = entities
        self.game_map = game_map
        self.event_handler = event_handler

    def handle_events(self, events: Iterator[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)
    
    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.entities:
            console.print(*entity.info)

        context.present(console)
        console.clear()

