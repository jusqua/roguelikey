from __future__ import annotations
from typing import TYPE_CHECKING
import color
if TYPE_CHECKING:
    from tcod import Console
    from game_map import GameMap
    from engine import Engine


def get_names_at(position: tuple[int, int], game_map: GameMap) -> str:
    if not game_map.in_bounds(*position) or not game_map.visible[position]:
        return ""

    x, y = position
    names = ", ".join(entity.name for entity in game_map.entities if entity.x == x and entity.y == y)
    return names.capitalize()


def render_bar(console: Console, current_value: int, maximum_value: int, total_width: int) -> None:
    gap = 3
    total_width -= gap

    bar_width = int(float(current_value) / maximum_value * total_width)
    hp_status = f"{current_value}/{maximum_value}"

    console.draw_rect(gap, 45, total_width, 1, 1, bg=color.bar_empty)
    if bar_width > 0:
        console.draw_rect(3, 45, bar_width, 1, 1, bg=color.bar_filled)
    console.print(0, 45, "HP")
    console.print(gap + int((total_width - len(hp_status)) / 2), 45, hp_status)


def render_name_at_mouse(console: Console, engine: Engine, position: tuple[int, int]) -> None:
    names_at_mouse_position = get_names_at(engine.mouse_location, engine.game_map)
    console.print(*position, names_at_mouse_position)

