from input_handling import BaseEventHandler, EventHandler
from exception import QuitWithoutSave
import tcod.context
import tcod.event
import tcod.console
import color
import traceback
import setup_game


def main() -> None:
    handler: BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(
        *setup_game.screen_size,
        tileset=setup_game.tileset,
        title="Roguelikey",
        sdl_window_flags=tcod.context.SDL_WINDOW_FULLSCREEN_DESKTOP
    ) as context:
        root_console = tcod.console.Console(*setup_game.screen_size, order="F")
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
                        handler.engine.message_log.add_message(traceback.format_exc(), color.error)
        except QuitWithoutSave:
            raise
        except (SystemExit, BaseException):
            setup_game.save_game(handler, setup_game.save_file_name)
            raise


if __name__ == "__main__":
    main()

