from __future__ import annotations
import os
from textwrap import wrap
from typing import TYPE_CHECKING, Callable, Union
from action import Action, DropAction, BumpAction, EquipAction, WaitAction, PickupAction
from tcod.console import Console
from entity import Item
from exception import Impossible, QuitWithoutSave
import tcod.constants
import tcod.event
import color

if TYPE_CHECKING:
    from engine import Engine


MOVE_KEYS = {
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

CURSOR_Y_KEYS = {
    tcod.event.K_k: -1,
    tcod.event.K_j: 1,
}

MODIFIER_KEYS = {
    tcod.event.K_LSHIFT,
    tcod.event.K_RSHIFT,
    tcod.event.K_LCTRL,
    tcod.event.K_RCTRL,
    tcod.event.K_LALT,
    tcod.event.K_RALT,
}

QUIT_KEYS = [tcod.event.K_q, tcod.event.K_ESCAPE]

WAIT_KEYS = tcod.event.K_w
CONFIRM_KEY = tcod.event.K_SPACE
DISCARD_KEY = tcod.event.K_d


class BaseEventHandler(tcod.event.EventDispatch[Union[Action, "BaseEventHandler"]]):
    """
    An event handler return value which can trigger an action or switch active handlers.
    If a handler is returned then it will become the active handler for future events.
    If an action is returned it will be attempted and if it's valid then MainGameEventHandler will become the active handler.
    """

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handles event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} cannot handle actions."
        return self

    def on_render(self, console: Console) -> None:
        raise NotImplementedError

    def ev_quit(self, _: tcod.event.Quit) -> Action | BaseEventHandler | None:
        raise SystemExit


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent: BaseEventHandler, text: str) -> None:
        self.parent = parent
        self.text = text

    def on_render(self, console: Console) -> None:
        """Render a parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.constants.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> BaseEventHandler | None:
        """Return to parent handler on any key pressed."""
        return self.parent


class HelpDialog(PopupMessage):
    def __init__(self, parent: BaseEventHandler) -> None:
        text = "\n".join(
            [
                "\n\n# Movement",
                "[h] to go left",
                "[l] to go right",
                "[j] to go downwards",
                "[k] to go upwards",
                "[y] to go upleft direction",
                "[b] to go downleft direction",
                "[u] to go upright direction",
                "[n] to go downright direction",
                "[w] wait a turn",
                "\n\n# Game",
                "[i] open inventory",
                "[v] show history logs",
                "[f] look around",
                "[g] pickup an item (when avaliable)",
                "[>] move to next floor (when avaliable)",
                "[esc] menu",
                "\n\n# Select Dialogs",
                "[space] select current cursor option",
                "[k] cursor up",
                "[j] cursor down",
                "[q] or [esc] to current quit dialog",
                "\n\n# Inventory",
                "[d] drop item",
            ]
        )
        super().__init__(parent, text)

    def on_render(self, console: Console) -> None:
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 4,
            console.height // 8,
            self.text,
            fg=color.white,
            bg=color.black,
        )


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        elif self.handle_action(action_or_state):
            if not self.engine.player.is_alive:
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine)
        return self

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

    def ev_mousemotion(
        self, event: tcod.event.MouseMotion
    ) -> Action | BaseEventHandler | None:
        position = (event.tile.x, event.tile.y)
        if self.engine.game_map.in_bounds(*position):
            self.engine.is_mouse_motion = True
            self.engine.mouse_location = position


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        player = self.engine.player

        match event.sym:
            case key if key == tcod.event.K_PERIOD and event.mod & tcod.event.KMOD_SHIFT:
                return TakeDownStairsAction(player)
            case key if key in MOVE_KEYS:
                return BumpAction(player, *MOVE_KEYS[key])
            case key if key == WAIT_KEYS:
                return WaitAction(player)
            case tcod.event.K_g:
                return PickupAction(player)
            case tcod.event.K_v:
                return HistoryViewer(self.engine)
            case tcod.event.K_i:
                return InventoryEventHandler(self.engine)
            case tcod.event.K_f:
                return LookHandler(self.engine)
            case tcod.event.K_ESCAPE:
                return InGameMenu(self)

        return None


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handles exit without saving."""
        if os.path.exists("data.sav"):
            os.remove("data.sav")
        raise QuitWithoutSave

    def ev_quit(self, _: tcod.event.Quit) -> Action | BaseEventHandler | None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()
        return None


class TakeDownStairsAction(Action):
    def perform(self) -> None:
        """Take the stairs, if any exists at entity's location."""
        if self.entity.position != self.engine.game_map.down_stairs_location:
            raise Impossible("There are no stairs here.")
        self.engine.game_world.generate_floor()
        self.engine.message_log.add_message("You decend the staircase.", color.decend)


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated"""

    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: Console) -> None:
        super().on_render(console)

        x, y, w, h = 64, 0, 32, 64

        console.draw_frame(x, y, w, h, fg=color.white, bg=color.black)
        console.print_box(x, y, w, 1, "┤ History ├", alignment=tcod.constants.CENTER)
        console.print_box(
            x,
            y + h - 1,
            w - 1,
            1,
            "┤ k to go up, j to go down ├",
            alignment=tcod.constants.RIGHT,
        )
        if self.cursor < self.log_length - 1:
            console.print(x + 1, y + h - 1, "↑")
        if self.cursor > 0:
            console.print(x + 2, y + h - 1, "↓")

        self.engine.message_log.render_messages(
            console, (x, y), (w, h), self.engine.message_log.messages[: self.cursor + 1]
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> MainGameEventHandler | None:
        match event.sym:
            case key if key in CURSOR_Y_KEYS:
                adjust = CURSOR_Y_KEYS[key]
                if (adjust < 0 and self.cursor == 0) or (
                    adjust > 0 and self.cursor == self.log_length - 1
                ):
                    return
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
            case tcod.event.K_HOME:
                self.cursor = 0
            case tcod.event.K_END:
                self.cursor = self.log_length - 1
            case key if key in QUIT_KEYS:
                return MainGameEventHandler(self.engine)


class AskUserEventHandler(EventHandler):
    """Handles input for special actions"""

    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.cursor = 0

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        """By default any key exit this input handler"""
        if event.sym in MODIFIER_KEYS:
            return None
        return self.on_exit()

    def render_select(
        self,
        console: Console,
        elements: list[str],
        location: tuple[int, int],
        fgs: list[tuple[int, int, int]] | None = None,
    ) -> None:
        """Handler selection in position"""
        x, y = location
        if not fgs:
            fgs = [color.white for _ in range(len(elements))]
        printables = zip(elements, fgs)

        for i, printable in enumerate(printables):
            e, fg = printable
            fg, bg = (
                (color.black if fg == color.white else fg, color.white)
                if self.cursor == i
                else (fg, None)
            )
            self.print_element(console, (x, y + i), e, fg=fg, bg=bg, index=i)

    def print_element(
        self,
        console: Console,
        position: tuple[int, int],
        element: str,
        index: int = 0,
        **kwargs,
    ):
        console.print(*position, element, **kwargs)

    def cursor_move(self, event: tcod.event.KeyDown, elements_length: int) -> None:
        match event.sym:
            case key if key in CURSOR_Y_KEYS:
                adjust = CURSOR_Y_KEYS[key]
                if (adjust < 0 and self.cursor == 0) or (
                    adjust > 0 and self.cursor == elements_length - 1
                ):
                    return
                self.cursor = max(0, min(self.cursor + adjust, elements_length - 1))
            case tcod.event.K_HOME:
                self.cursor = 0
            case tcod.event.K_END:
                self.cursor = elements_length - 1

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Action | BaseEventHandler | None:
        """By default any mouse click exit this input handler"""
        return self.on_exit()

    def on_exit(self) -> Action | BaseEventHandler | None:
        """Called when user try to exit or cancel an action"""
        return MainGameEventHandler(self.engine)


class InGameMenu(AskUserEventHandler, PopupMessage):
    def __init__(self, parent: EventHandler) -> None:
        self.parent = parent
        self.engine = parent.engine
        self.cursor = 0

        self.elements = ["Help", "Save and Quit", "Quit without saving"]
        self.functions = [
            lambda: HelpDialog(self.parent),
            lambda: (_ for _ in ()).throw(SystemExit),
            lambda: (_ for _ in ()).throw(QuitWithoutSave),
        ]

    def on_render(self, console: Console) -> None:
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        self.render_select(
            console, self.elements, (console.width // 2, console.height // 2)
        )

    def print_element(
        self,
        console: Console,
        position: tuple[int, int],
        element: str,
        index: int = 0,
        **kwargs,
    ):
        console.print_box(
            0,
            console.height // 2 + index,
            console.width,
            1,
            element,
            **kwargs,
            alignment=tcod.constants.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        if event.sym in QUIT_KEYS:
            return super().ev_keydown(event)

        self.cursor_move(event, len(self.elements))
        if event.sym == CONFIRM_KEY:
            return self.functions[self.cursor]()


class LevelUpEventHandler(AskUserEventHandler):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.options = [
            f"Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
            f"Strength (+1 attack, from {self.engine.player.fighter.base_power})",
            f"Agility (+1 defense, from {self.engine.player.fighter.base_defense})",
            f"Dexterity (+2 luck, from {self.engine.player.fighter.base_luck})",
        ]
        self.functions = [
            self.engine.player.level.increase_max_hp,
            self.engine.player.level.increase_power,
            self.engine.player.level.increase_defense,
            self.engine.player.level.increase_luck,
        ]

    def on_render(self, console: Console) -> None:
        super().on_render(console)

        x, y, w, h = 64, 0, 32, 64

        console.draw_frame(x, y, w, h, fg=color.white, bg=color.black)
        console.print_box(x, y, w, 1, "┤ Level Up ├", alignment=tcod.constants.CENTER)
        console.print_box(
            x,
            y + h - 1,
            w - 1,
            1,
            "┤ [SPACE] to apply changes ├",
            alignment=tcod.constants.RIGHT,
        )

        console.print_box(
            x + 1, y + 2, w, 1, "Congratulations!", alignment=tcod.constants.CENTER
        )
        console.print(x + 1, y + 4, "Select an attribute:")

        self.render_select(console, self.options, (x + 1, y + 6))

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        self.cursor_move(event, len(self.options))
        if event.sym != CONFIRM_KEY:
            return
        self.functions[self.cursor]()

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Action | BaseEventHandler | None:
        """Prevent from exit clicking with mouse."""
        return None


class InventoryEventHandler(AskUserEventHandler):
    def on_render(self, console: Console) -> None:
        """Render an invetory menu far from the player"""
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        x, y, w, h = 64, 0, 32, 64
        console.draw_frame(x, y, w, h, fg=color.white, bg=color.black)
        console.print_box(x + 1, y, w, 1, "┤ Inventory ├")
        console.print_box(
            x,
            y,
            w - 1,
            1,
            f"┤ {number_of_items_in_inventory}/{self.engine.player.inventory.capacity} ├",
            alignment=tcod.constants.RIGHT,
        )

        if number_of_items_in_inventory == 0:
            console.print_box(
                x, y + h // 2, w, 1, "(Empty)", alignment=tcod.constants.CENTER
            )
            return

        items: list[str] = []
        fgs = []
        for item in self.engine.player.inventory.items:
            item_text = f"{item.char} {item.name}"
            if self.engine.player.equipment.is_item_equipped(item):
                item_text += " (E)"
            items.append(item_text)
            fgs.append(item.color)

        self.render_select(console, items, (x + 1, y + 1), fgs=fgs)

        if items:
            y, h = 48, 16
            console.draw_frame(x, y, w, h, fg=color.white, bg=color.black)
            console.print_box(
                x, y, w - 1, 1, "┤ Description ├", alignment=tcod.constants.RIGHT
            )
            console.print(x, y, "├")
            console.print(x + w - 1, y, "┤")
            console.print(
                x + 1,
                y + 1,
                "\n".join(
                    wrap(
                        self.engine.player.inventory.items[self.cursor].description,
                        w - 2,
                    )
                ),
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        number_of_items_in_inventory = len(self.engine.player.inventory.items)
        key = event.sym

        if key in QUIT_KEYS:
            return super().ev_keydown(event)

        if number_of_items_in_inventory == 0:
            return

        self.cursor_move(event, number_of_items_in_inventory)

        item = self.engine.player.inventory.items[self.cursor]
        if key == CONFIRM_KEY:
            if item.consumable:
                return item.consumable.action(self.engine.player)
            elif item.equippable:
                return EquipAction(self.engine.player, item)
        elif key == DISCARD_KEY:
            self.cursor = max(0, self.cursor - 1)
            return DropAction(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index in the map"""

    def __init__(self, engine: Engine) -> None:
        """Set cursor to the player when this handler is constructed."""
        super().__init__(engine)
        engine.mouse_location = self.engine.player.position

    def on_render(self, console: Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        position = self.engine.mouse_location
        console.tiles_rgb["bg"][position] = color.white
        console.tiles_rgb["fg"][position] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        """Check for movement or confirmation."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1
            if event.mod & tcod.event.KMOD_CTRL:
                modifier *= 5
            if event.mod & tcod.event.KMOD_ALT:
                modifier *= 5
            if event.mod & tcod.event.KMOD_SHIFT:
                modifier *= 5

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]

            x += dx * modifier
            y += dy * modifier

            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))

            self.engine.mouse_location = x, y
            return None
        elif key == CONFIRM_KEY:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Action | BaseEventHandler | None:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Action | BaseEventHandler | None:
        """Called when index is selected."""
        raise NotImplementedError


class LookHandler(SelectIndexHandler):
    """Provides to player to look around the map."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an single enemy."""

    def __init__(
        self,
        engine: Engine,
        callback: Callable[[tuple[int, int]], Action | BaseEventHandler | None],
    ) -> None:
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | BaseEventHandler | None:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting multiple enemies an aread within given radius."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[tuple[int, int]], Action | BaseEventHandler | None],
    ) -> None:
        super().__init__(engine)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: Console) -> None:
        """Highlight area under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location
        x = x - self.radius - 1
        y = y - self.radius - 1
        width = self.radius**2
        height = width

        console.draw_frame(x, y, width, height, fg=color.red, clear=False)

    def on_index_selected(self, x: int, y: int) -> Action | BaseEventHandler | None:
        return self.callback((x, y))
