import tcod.event
from action import Action, EscapeAction, MovementAction


class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Action | None:
        raise SystemExit
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        match event.sym:
            case tcod.event.K_UP:
                return MovementAction(dx=0, dy=-1)
            case tcod.event.K_DOWN:
                return MovementAction(dx=0, dy=1)
            case tcod.event.K_RIGHT:
                return MovementAction(dx=1, dy=0)
            case tcod.event.K_LEFT:
                return MovementAction(dx=-1, dy=0)
            case tcod.event.K_ESCAPE:
                return EscapeAction()
            case _:
                return None


