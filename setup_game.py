from __future__ import annotations
from copy import deepcopy
from tcod.console import Console
from engine import Engine
from game_map import GameWorld
from input_handling import BaseEventHandler, MainGameEventHandler, PopupMessage
import entity_factory
import color
import tcod
import lzma
import pickle
import traceback


background_image = tcod.image.load("./assets/menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game as an Engine instance."""
    map_size = 80, 40
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

    return engine


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
                    return MainGameEventHandler(load_game("data.sav"))
                except FileNotFoundError:
                    return PopupMessage(self, "No saved game to load.")
                except Exception as exc:
                    traceback.print_exc()
                    return PopupMessage(self, f"Failed to load save:\n{exc}")
            case tcod.event.K_n:
                return MainGameEventHandler(new_game())
        return None

