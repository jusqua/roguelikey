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

    entities = set(game_map.entities)
    if not game_map.engine.is_mouse_motion:
        entities -= {game_map.engine.player}

    names = [entity.name for entity in entities if entity.position == position]

    if position == game_map.down_stairs_location:
        names.insert(0, "Down Stairs")

    return ", ".join(names)


def render_bar(
    console: Console,
    current_value: int,
    maximum_value: int,
    total_width: int,
    location: tuple[int, int],
) -> None:
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


def render_name_at_mouse(
    console: Console, engine: Engine, position: tuple[int, int]
) -> None:
    names_at_mouse_position = get_names_at(engine.mouse_location, engine.game_map)
    if len(names_at_mouse_position) == 0:
        return
    elif len(names_at_mouse_position) > 58:
        names_at_mouse_position = names_at_mouse_position[:55] + "..."
    console.print(*position, f"┤ {names_at_mouse_position} ├")


def render_status(console: Console, engine: Engine) -> None:
    player = engine.player
    fighter = player.fighter
    level = player.level
    equipment = player.equipment

    render_name_at_mouse(console, engine, (1, 63))
    console.print(1, 0, f"┤ Floor {engine.game_world.current_floor} ├")

    x, y, w, h = 64, 0, 32, 12
    console.draw_frame(x, y, w, h)
    console.print_box(x, y, w, 1, "┤ Status ├", alignment=tcod.CENTER)
    render_bar(
        console,
        fighter.hp,
        fighter.max_hp,
        30,
        (x + 1, y + 2),
    )

    console.print_box(
        x + 1,
        y + 4,
        w - 2,
        1,
        f"XP: {level.current_xp} / {level.experience_to_next_level}",
        alignment=tcod.RIGHT,
    )
    console.print(x + 1, y + 4, f"Level: {level.current_level}")

    attack_string = f"Attack: {fighter.base_power}"
    if fighter.power_bonus != 0:
        signal = "+" if fighter.power_bonus > 0 else ""
        attack_string += f" ({signal}{fighter.power_bonus})"
    console.print(x + 1, y + 6, attack_string)

    defense_string = f"Defense: {fighter.base_defense}"
    if fighter.defense_bonus != 0:
        signal = "+" if fighter.defense_bonus > 0 else ""
        defense_string += f" ({signal}{fighter.defense_bonus})"
    console.print(x + 1, y + 7, defense_string)

    luck_string = f"Luck: {fighter.base_luck}"
    if fighter.luck_bonus != 0:
        signal = "+" if fighter.luck_bonus > 0 else ""
        luck_string += f" ({signal}{fighter.luck_bonus})"
    console.print(x + 1, y + 8, luck_string)

    y, h = 12, 28
    console.draw_frame(x, y, w, h)
    console.print_box(x, y, w, 1, "┤ Equipment ├", alignment=tcod.CENTER)
    y += 2

    if equipment.weapon and equipment.weapon.equippable:
        console.print(x + 1, y, "Weapon: " + equipment.weapon.name)
        console.print(x + 1, y + 1, equipment.weapon.equippable.description)
        y += 4

    if equipment.armor and equipment.armor.equippable:
        console.print(x + 1, y, "Armor: " + equipment.armor.name)
        console.print(x + 1, y + 1, equipment.armor.equippable.description)
        y += 4

    if equipment.helmet and equipment.helmet.equippable:
        console.print(x + 1, y, "Helmet: " + equipment.helmet.name)
        console.print(x + 1, y + 1, equipment.helmet.equippable.description)
        y += 4

    if equipment.ring and equipment.ring.equippable:
        console.print(x + 1, y, "Ring: " + equipment.ring.name)
        console.print(x + 1, y + 1, equipment.ring.equippable.description)
        y += 4

    if y == 14:
        console.print_box(x, y, w, 1, "(Nothing Equipped)", alignment=tcod.CENTER)
