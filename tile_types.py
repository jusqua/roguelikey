import numpy as np


graphic_dtype = np.dtype([
    ("ch", np.int32),
    ("fg", "3B"),
    ("bg", "3B")
])

tile_dtype = np.dtype([
    ("walkable", np.bool_),
    ("transparent", np.bool_),
    ("dark", graphic_dtype),
    ("light", graphic_dtype)
]);


def new_tile(
        *,
        walkable: bool,
        transparent: bool,
        dark: tuple[int, tuple[int, int, int], tuple[int, int, int]],
        light: tuple[int, tuple[int, int, int], tuple[int, int, int]]
    ) -> np.ndarray:
    """
    Helper function to defining individual tile types
    """
    return np.array((walkable, transparent, dark, light), dtype=tile_dtype)


SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
    light=(ord(" "), (255, 255, 255), (200, 180, 50))
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (0, 0, 150)),
    light=(ord(" "), (255, 255, 255), (130, 110, 50))
)

