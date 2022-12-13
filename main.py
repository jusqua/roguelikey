from copy import deepcopy
from engine import Engine
from input_handling import EventHandler
from procgen import generate_dungeon
import tcod
import entity_factory


def main() -> None:
    screen_size = 80, 50
    map_size = 80, 40
    room_limits = 6, 10
    max_rooms = 30
    max_enemies_per_room = 2

    tileset = tcod.tileset.load_tilesheet("./assets/tileset.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    player = deepcopy(entity_factory.player)
    game_map = generate_dungeon(max_rooms, max_enemies_per_room, room_limits, map_size, player)

    event_handler = EventHandler()
    engine = Engine(player, game_map, event_handler)

    with tcod.context.new_terminal(*screen_size, tileset=tileset, title="Roguelike", vsync=True) as context:
        root_console = tcod.Console(*screen_size, order="F")

        while True:
            engine.render(root_console, context)
            engine.handle_events(tcod.event.wait())


if __name__ == "__main__":
    main()

