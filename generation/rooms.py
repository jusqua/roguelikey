from __future__ import annotations
from typing import Iterator


class Room:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

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
        """Return the inner area of this room as a 2D array index."""
        raise NotImplementedError


class RectangularRoom(Room):
    @property
    def inner(self) -> Iterator[tuple[int, int]]:
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                yield x, y
