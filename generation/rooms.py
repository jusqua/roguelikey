from __future__ import annotations
from typing import Iterator
import numpy as np


class Room:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.width = width
        self.height = height

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def center(self) -> tuple[int, int]:
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)

    def intersects(self, other: Room) -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

    @property
    def limits(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return (self.x1, self.y1), (self.x2, self.y2)

    @property
    def inner(self) -> list[tuple[int, int]]:
        """Return the inner area of this room as a list of coordinates."""
        raise NotImplementedError


class RectangularRoom(Room):
    @property
    def inner(self) -> Iterator[tuple[int, int]]:
        for x, y in np.ndindex(self.size):
            yield self.x1 + x, self.y1 + y


class EllipticalRoom(Room):
    @property
    def inner(self) -> Iterator[tuple[int, int]]:
        # cx and cy are the center and the radius because are based on an arbitrary position
        w, h = self.size
        cx, cy = w / 2, h / 2
        for x, y in np.ndindex(w, h):
            dx = ((x - cx) ** 2) / (cx**2)
            dy = ((y - cy) ** 2) / (cy**2)
            if dx + dy <= 1:
                yield self.x1 + x, self.y1 + y
