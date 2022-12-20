from input_handling import BaseEventHandler, EventHandler
from exception import QuitWithoutSave
import tcod
import color
import traceback
import setup_game


def save_game(handler: BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, EventHandler):
        handler.engine.save_as(filename)


def main() -> None:
    screen_size = 80, 50
    tileset = tcod.tileset.load_tilesheet("./assets/tileset.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    handler: BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(*screen_size, tileset=tileset, title="Roguelikey") as context:
        root_console = tcod.Console(*screen_size, order="F")

        try:
            while True:
                root_console.clear()
                handler.on_render(root_console)
                context.present(root_console)
                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, EventHandler):
                        handler.engine.message_log.add_message(traceback.format_exc(), color.error)
        except QuitWithoutSave:
            raise
        except (SystemExit, BaseException):
            save_game(handler, "data.sav")
            raise


if __name__ == "__main__":
    main()

