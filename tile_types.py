import numpy as np


graphic_dtype = np.dtype([("ch", np.int32), ("fg", "3B"), ("bg", "3B")])
tile_dtype = np.dtype([("walkable", np.bool_), ("transparent", np.bool_), ("dark", graphic_dtype)]);


def new_tile(walkable: bool, transparent: bool, dark: tuple[int, tuple[int, int, int], tuple[int, int, int]]) -> np.ndarray:
    """
    Helper function to defining individual tile types
    """
    return np.array((walkable, transparent, dark), dtype=tile_dtype)


floor = new_tile(True, True, (ord(" "), (255, 255, 255), (50, 50, 150)))
wall = new_tile(False, False, (ord(" "), (255, 255, 255), (0, 0, 150)))

