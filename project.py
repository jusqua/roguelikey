from __future__ import annotations
from input_handling import BaseEventHandler, EventHandler
from exception import QuitWithoutSave
from copy import deepcopy
from tcod.console import Console
from engine import Engine
from game_map import GameWorld
from input_handling import (
    CONFIRM_KEY,
    CURSOR_Y_KEYS,
    BaseEventHandler,
    EventHandler,
    MainGameEventHandler,
    PopupMessage,
)
import tcod.context
import tcod.event
import tcod.console
import color
import traceback
import os
import entity_factory
import color
import tcod
import lzma
import pickle


# Screen Size
screen_size = 96, 64
# Save file name
save_file_name = "data.sav"


def main() -> None:
    handler: BaseEventHandler = MainMenu()

    # https://dwarffortresswiki.org/index.php/Tileset_repository#Zilk_16x16.png
    tileset = tcod.tileset.load_tilesheet(
        "./assets/tileset.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    # Reduce sharp corners from tileset rendering
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "linear"

    with tcod.context.new_terminal(
        *screen_size,
        tileset=tileset,
        title="Roguelikey",
        sdl_window_flags=tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP,
    ) as context:
        root_console = tcod.console.Console(*screen_size, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(root_console)
                context.present(root_console, keep_aspect=True, integer_scaling=True)
                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except QuitWithoutSave:
            raise
        except (SystemExit, BaseException):
            save_game(handler, save_file_name)
            raise


def new_game() -> Engine:
    """Return a brand new game as an Engine instance."""
    map_size = screen_size[0] - 32, screen_size[1]
    room_limits = 8, 12
    max_rooms = 30

    player = deepcopy(entity_factory.player)
    engine = Engine(player)

    engine.game_world = GameWorld(max_rooms, room_limits, map_size, engine)

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "You enter into the depths of the dungeon...", color.welcome_text
    )

    dagger = deepcopy(entity_factory.dagger)
    dagger.parent = player.inventory
    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, False)

    robe = deepcopy(entity_factory.robe)
    robe.parent = player.inventory
    player.inventory.items.append(robe)
    player.equipment.toggle_equip(robe, False)

    hood = deepcopy(entity_factory.hood)
    hood.parent = player.inventory
    player.inventory.items.append(hood)
    player.equipment.toggle_equip(hood, False)

    confusion_scroll = deepcopy(entity_factory.confusion_scroll)
    confusion_scroll.parent = player.inventory
    player.inventory.items.append(confusion_scroll)
    player.equipment.toggle_equip(confusion_scroll, False)

    return engine


def save_game(handler: BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, EventHandler):
        handler.engine.save_as(filename)


def load_game(filename: str) -> Engine:
    """Load an Engine instance from file."""
    with open(filename, "rb") as file:
        engine = pickle.loads(lzma.decompress(file.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self) -> None:
        self.cursor = 0
        self.elements = ["New Game", "Continue previous Game", "Quit"]
        self.functions = [
            lambda: MainGameEventHandler(new_game()),
            lambda: MainGameEventHandler(load_game(save_file_name))
            if save_file_name in os.listdir()
            else PopupMessage(self, "No saved game to load."),
            lambda: (_ for _ in ()).throw(SystemExit),
        ]

    def on_render(self, console: Console) -> None:
        """Render the main menu and the background image."""
        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "ROGUELIKEY",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By jusqua",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        for i, e in enumerate(self.elements):
            fg, bg = (
                (color.black, color.white) if self.cursor == i else (color.white, None)
            )
            console.print_box(
                0,
                console.height // 2 + i,
                console.width,
                1,
                e,
                fg=fg,
                bg=bg,
                alignment=tcod.CENTER,
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> BaseEventHandler | None:
        elements_length = len(self.elements)

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
            case key if key == CONFIRM_KEY:
                return self.functions[self.cursor]()


if __name__ == "__main__":
    main()
