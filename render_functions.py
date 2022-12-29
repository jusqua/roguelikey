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
    x, y, w, h = 64, 0, 32, 20

    render_name_at_mouse(console, engine, (1, 63))

    match engine.game_world.current_floor:
        case 1:
            floor = "1st"
        case 2:
            floor = "2nd"
        case 3:
            floor = "3rd"
        case _:
            floor = f"{engine.game_world.current_floor}th"
    console.print(1, 0, f"┤ {floor} Floor ├")

    console.draw_frame(x, y, w, h)
    console.print_box(x, y, w, 1, "┤ Status ├", alignment=tcod.CENTER)
    render_bar(
        console,
        engine.player.fighter.hp,
        engine.player.fighter.max_hp,
        30,
        (x + 1, y + 2),
    )

    console.print_box(
        x + 1,
        y + 4,
        w - 2,
        1,
        f"XP: {engine.player.level.current_xp} / {engine.player.level.experience_to_next_level}",
        alignment=tcod.RIGHT,
    )
    console.print(x + 1, y + 4, f"Level: {engine.player.level.current_level}")

    attack_string = f"Attack: {engine.player.fighter.base_power}"
    if engine.player.fighter.power_bonus != 0:
        signal = "+" if engine.player.fighter.power_bonus > 0 else ""
        attack_string += f" ({signal}{engine.player.fighter.power_bonus})"
    console.print(x + 1, y + 6, attack_string)

    defense_string = f"Defense: {engine.player.fighter.base_defense}"
    if engine.player.fighter.defense_bonus != 0:
        signal = "+" if engine.player.fighter.defense_bonus > 0 else ""
        defense_string += f" ({signal}{engine.player.fighter.defense_bonus})"
    console.print(x + 1, y + 7, defense_string)

    luck_string = f"Luck: {engine.player.fighter.base_luck}"
    if engine.player.fighter.luck_bonus != 0:
        signal = "+" if engine.player.fighter.luck_bonus > 0 else ""
        luck_string += f" ({signal}{engine.player.fighter.luck_bonus})"
    console.print(x + 1, y + 8, luck_string)

    y = 20
    console.draw_frame(x, y, w, h)
    console.print_box(x, y, w, 1, "┤ Equipment ├", alignment=tcod.CENTER)
    console.print_box(x, y + 2, w, 1, "Weapon", alignment=tcod.CENTER)
    if engine.player.equipment.weapon and engine.player.equipment.weapon.equippable:
        console.print(x + 1, y + 3, engine.player.equipment.weapon.name)
        console.print(
            x + 1,
            y + 4,
            f"Attack Modifier: {engine.player.equipment.weapon.equippable.power_bonus}",
        )
        console.print(
            x + 1,
            y + 5,
            f"Defense Modifier: {engine.player.equipment.weapon.equippable.defense_bonus}",
        )
        console.print(
            x + 1,
            y + 6,
            f"Luck Modifier: {engine.player.equipment.weapon.equippable.luck_bonus}",
        )
    else:
        console.print_box(x, y + 4, w, 1, "No Weapon Equipped", alignment=tcod.CENTER)

    console.print_box(x, y + 8, w, 1, "Armor", alignment=tcod.CENTER)
    if engine.player.equipment.armor and engine.player.equipment.armor.equippable:
        console.print(x + 1, y + 9, engine.player.equipment.armor.name)
        console.print(
            x + 1,
            y + 10,
            f"Attack Modifier: {engine.player.equipment.armor.equippable.power_bonus}",
        )
        console.print(
            x + 1,
            y + 11,
            f"Defense Modifier: {engine.player.equipment.armor.equippable.defense_bonus}",
        )
        console.print(
            x + 1,
            y + 12,
            f"Luck Modifier: {engine.player.equipment.armor.equippable.luck_bonus}",
        )
    else:
        console.print_box(x, y + 10, w, 1, "No Armor Equipped", alignment=tcod.CENTER)
