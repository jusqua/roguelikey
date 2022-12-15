from __future__ import annotations
from typing import TYPE_CHECKING
from action import Action, DropAction, BumpAction, WaitAction, PickupAction
from tcod.console import Console
from exception import Impossible
import tcod.constants
import tcod.event
import color
if TYPE_CHECKING:
    from engine import Engine
    from entity import Item


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CURSOR_Y_KEYS = {
    tcod.event.K_k: -1,
    tcod.event.K_j: 1,
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

MODIFIER_KEYS = {
    tcod.event.K_LSHIFT,
    tcod.event.K_RSHIFT,
    tcod.event.K_LCTRL,
    tcod.event.K_RCTRL,
    tcod.event.K_LALT,
    tcod.event.K_RALT,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Action | None) -> bool:
        if action is None:
            return False
        try:
            action.perform()
        except Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turn()
        self.engine.update_fov()
        return True

    def on_render(self, console: Console) -> None:
        self.engine.render(console)

    def ev_quit(self, _: tcod.event.Quit) -> Action | None:
        raise SystemExit

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> Action | None:
        position = (event.tile.x, event.tile.y)
        if self.engine.game_map.in_bounds(*position):
            self.engine.mouse_location = position


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        player = self.engine.player
        key = event.sym

        if key in MOVE_KEYS:
            return BumpAction(player, *MOVE_KEYS[key])
        elif key in WAIT_KEYS:
            return WaitAction(player)
        elif key == tcod.event.K_g:
            return PickupAction(player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.K_i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            self.engine.event_handler = InvetoryDropHandler(self.engine)

        return None


class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit

        return None

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated"""
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: Console) -> None:
        super().on_render(console)
        
        log_console = Console(console.width - 6, console.height - 6)
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(0, 0, log_console.width, 1, "┤ Message history ├", alignment=tcod.constants.CENTER)

        self.engine.message_log.render_messages(
            log_console,
            (1, 1),
            (log_console.width - 2, log_console.height - 2),
            self.engine.message_log.messages[:self.cursor + 1]
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        key = event.sym
        if key in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[key]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif key == tcod.event.K_HOME:
            self.cursor = 0
        elif key == tcod.event.K_END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)


class AskUserEventHandler(EventHandler):
    """Handles input for special actions"""

    def handle_action(self, action: Action | None) -> bool:
        """Return to main event handler when a valid action was performed"""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        """By default any key exit this input handler"""
        if event.sym in MODIFIER_KEYS:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Action | None:
        """By default any mouse click exit this input handler"""
        return self.on_exit()

    def on_exit(self) -> Action | None:
        """Called when user try to exit or cancel an action"""
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler):
    """Handles user item selection"""

    TITLE = "<Missing title>"

    def on_render(self, console: Console) -> None:
        """Render an invetory menu far from the player"""
        super().on_render(console)
        inventory = self.engine.player.inventory
        number_of_items_in_inventory = len(inventory.items)

        size = len(self.TITLE) + 4, min(number_of_items_in_inventory + 2, 3)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        console.draw_frame(x, y, *size, self.TITLE, fg=(255, 255, 255), bg=(0, 0, 0))
        if number_of_items_in_inventory > 0:
            for i, item in enumerate(inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + 1 + i, f"[{item_key}] {item.name}")
        else:
            console.print(x + 1, y + 1, f"(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a
        
        if not 0 <= index <= 26:
            return super().ev_keydown(event)

        try:
            selected_item = player.inventory.items[index]
        except IndexError:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            return None

        return self.on_item_selected(selected_item)

    def on_item_selected(self, item: Item) -> Action | None:
        """Called when the user selects a valid item"""
        raise NotImplementedError


class InventoryActivateHandler(InventoryEventHandler):
    """Handles inventory item usage"""
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Action | None:
        """Return action for selected item"""
        return item.consumable.action(self.engine.player)


class InvetoryDropHandler(InventoryEventHandler):
    """Handles inventory item drop"""
    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Action | None:
        return DropAction(self.engine.player, item)

