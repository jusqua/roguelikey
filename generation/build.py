from typing import Iterator
from random import choice
from tcod.los import bresenham


def tunnel_between(
    start: tuple[int, int], end: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    """Create a L-shaped tunnel between those points"""
    corner = choice(((end[0], start[1]), (start[0], end[1])))
    for x, y in bresenham(start, corner):
        yield x, y
    for x, y in bresenham(corner, end):
        yield x, y
