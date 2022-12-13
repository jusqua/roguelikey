from __future__ import annotations
from action import Action, EscapeAction, BumpAction
from typing import TYPE_CHECKING
import tcod.event

if TYPE_CHECKING:
    from engine import Engine


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()
            self.engine.handle_enemy_turn()
            self.engine.update_fov()

    def ev_quit(self, event: tcod.event.Quit) -> Action | None:
        raise SystemExit
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        player = self.engine.player

        match event.sym:
            case tcod.event.K_UP:
                return BumpAction(player, dx=0, dy=-1)
            case tcod.event.K_DOWN:
                return BumpAction(player, dx=0, dy=1)
            case tcod.event.K_RIGHT:
                return BumpAction(player, dx=1, dy=0)
            case tcod.event.K_LEFT:
                return BumpAction(player, dx=-1, dy=0)
            case tcod.event.K_ESCAPE:
                return EscapeAction(player)
            case _:
                return None


