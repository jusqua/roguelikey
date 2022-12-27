from __future__ import annotations
from copy import deepcopy
from tcod.console import Console
from engine import Engine
from game_map import GameWorld
from input_handling import BaseEventHandler, EventHandler, MainGameEventHandler, PopupMessage
import os
import entity_factory
import color
import tcod
import lzma
import pickle
import traceback


# https://dwarffortresswiki.org/index.php/Tileset_repository#Zilk_16x16.png
tileset = tcod.tileset.load_tilesheet("./assets/tileset.png", 16, 16, tcod.tileset.CHARMAP_CP437)
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
    room_limits = 6, 10
    max_rooms = 30

    player = deepcopy(entity_factory.player)
    engine = Engine(player)

    engine.game_world = GameWorld(
        max_rooms,
        room_limits,
        map_size,
        engine
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message("Hello and welcome, adventure, to this ... roguelike?", color.welcome_text)

    dagger = deepcopy(entity_factory.dagger)
    dagger.parent = player.inventory
    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, False)

    robe = deepcopy(entity_factory.robe)
    robe.parent = player.inventory
    player.inventory.items.append(robe)
    player.equipment.toggle_equip(robe, False)

    player.level.add_xp(340)

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
    def on_render(self, console: Console) -> None:
        """Render the main menu and the background image."""
        console.draw_semigraphics(background_image, 0, 0)
        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "ROGUELIKEY",
            fg=color.menu_title,
            alignment=tcod.CENTER
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By jusqua",
            fg=color.menu_title,
            alignment=tcod.CENTER
        )

        menu_width = 24
        for i, text in enumerate(["[N]ew game", "[C]ontinue", "[Q]uit"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64)
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> BaseEventHandler | None:
        match event.sym:
            case tcod.event.K_q | tcod.event.K_ESCAPE:
                raise SystemExit
            case tcod.event.K_c:
                try:
                    return MainGameEventHandler(load_game(save_file_name))
                except FileNotFoundError:
                    return PopupMessage(self, "No saved game to load.")
                except Exception as exc:
                    traceback.print_exc()
                    return PopupMessage(self, f"Failed to load save:\n{exc}")
            case tcod.event.K_n:
                return MainGameEventHandler(new_game())
        return None

