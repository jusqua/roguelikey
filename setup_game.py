from __future__ import annotations
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
import os
import entity_factory
import color
import tcod
import lzma
import pickle


# https://dwarffortresswiki.org/index.php/Tileset_repository#Zilk_16x16.png
tileset = tcod.tileset.load_tilesheet(
    "./assets/tileset.png", 16, 16, tcod.tileset.CHARMAP_CP437
)
# [:, :, :3] removes the alpha channel from background
background_image = tcod.image.load("./assets/menu_background.png")[:, :, :3]
# Reduce sharp corners from tileset rendering
os.environ["SDL_RENDER_SCALE_QUALITY"] = "linear"
# Screen Size
screen_size = 96, 64
# Save file name
save_file_name = "data.sav"


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
        console.draw_semigraphics(background_image, 0, 0)
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
