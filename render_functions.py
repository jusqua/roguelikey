from __future__ import annotations
from typing import TYPE_CHECKING
import color
import tcod
if TYPE_CHECKING:
    from tcod import Console
    from game_map import GameMap
    from engine import Engine


def get_names_at(position: tuple[int, int], game_map: GameMap) -> str:
    if not game_map.in_bounds(*position) or not game_map.visible[position]:
        return ""

    x, y = position
    entities = set(game_map.entities)
    if not game_map.engine.is_mouse_motion:
        entities -= { game_map.engine.player }

    names = ", ".join(
        entity.name
        for entity in entities
        if entity.x == x and entity.y == y
    )
    return names.capitalize()


def render_dungeon_level(console: Console, dungeon_level: int, location: tuple[int, int]) -> None:
    """Render the current dungeon level were the player on."""
    console.print(*location, f"DL {dungeon_level}")


def render_bar(console: Console, current_value: int, maximum_value: int, total_width: int, location: tuple[int, int]) -> None:
    gap = 3
    total_width -= gap
    x, y = location

    bar_width = int(float(current_value) / maximum_value * total_width)
    hp_status = f"{current_value}/{maximum_value}"

    console.draw_rect(x + gap, y, total_width, 1, 1, bg=color.bar_empty)
    if bar_width > 0:
        console.draw_rect(x + gap, y, bar_width, 1, 1, bg=color.bar_filled)
    console.print(x, y, "HP")
    console.print(x + gap + int((total_width - len(hp_status)) / 2), y, hp_status)


def render_name_at_mouse(console: Console, engine: Engine, position: tuple[int, int]) -> None:
    names_at_mouse_position = get_names_at(engine.mouse_location, engine.game_map)
    if len(names_at_mouse_position) == 0:
        return
    elif len(names_at_mouse_position) > 58:
        names_at_mouse_position = names_at_mouse_position[:55] + "..."
    console.print(*position, f"┤ {names_at_mouse_position} ├")


def render_status(console: Console, engine: Engine) -> None:
    console.draw_frame(64, 0, 32, 20)
    console.print_box(64, 0, 32, 1, "┤ Status ├", alignment=tcod.CENTER)
    render_bar(console, engine.player.fighter.hp, engine.player.fighter.max_hp, 30, (65, 2))

    console.print_box(
        65, 4, 30, 1,
        f"XP: {engine.player.level.current_xp} / {engine.player.level.experience_to_next_level}",
        alignment=tcod.RIGHT
    )
    console.print(65, 4, f"Level: {engine.player.level.current_level}")

    attack_string = f"Attack: {engine.player.fighter.base_power}"
    if engine.player.fighter.power_bonus != 0:
        signal = "+" if engine.player.fighter.power_bonus > 0 else ""
        attack_string += f" ({signal}{engine.player.fighter.power_bonus})"
    console.print(65, 6, attack_string)

    defense_string = f"Defense: {engine.player.fighter.base_defense}"
    if engine.player.fighter.defense_bonus != 0:
        signal = "+" if engine.player.fighter.defense_bonus > 0 else ""
        defense_string += f" ({signal}{engine.player.fighter.defense_bonus})"
    console.print(65, 7, defense_string)

    render_name_at_mouse(console, engine, (1, 63))

