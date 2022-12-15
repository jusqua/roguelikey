from copy import deepcopy
from engine import Engine
from procgen import generate_dungeon
import tcod
import entity_factory
import color
import traceback


def main() -> None:
    screen_size = 80, 50
    map_size = 80, 40
    room_limits = 6, 10
    max_rooms = 30
    max_enemies_per_room = 2
    max_items_per_room = 2

    tileset = tcod.tileset.load_tilesheet("./assets/tileset.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    player = deepcopy(entity_factory.player)
    engine = Engine(player)
    engine.game_map = generate_dungeon(
        max_rooms,
        max_enemies_per_room,
        max_items_per_room,
        room_limits,
        map_size,
        engine
    )

    engine.message_log.add_message("Hello and welcome, adventure, to this ... roguelike?", color.welcome_text)
    engine.update_fov()

    with tcod.context.new_terminal(*screen_size, tileset=tileset, title="Roguelike", vsync=True) as context:
        root_console = tcod.Console(*screen_size, order="F")

        while True:
            root_console.clear()
            engine.event_handler.on_render(root_console)
            context.present(root_console)
            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:
                traceback.print_exc()
                engine.message_log.add_message(traceback.format_exc(), color.error)


if __name__ == "__main__":
    main()

