from tcod.console import Console
import numpy as np
import tile_types


class GameMap:
    def __init__(self, size: tuple[int, int]) -> None:
        self.width, self.height = size
        self.tiles = np.full(size, fill_value=tile_types.wall, order="F")
        self.visible = np.full(size, fill_value=False, order="F")
        self.explored = np.full(size, fill_value=False, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        """Verify if the x and y are inside of the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map

        In `visible` array tiles are draw with `light` colors,
        In `explored` array tiles are draw with `dark` colors,
        Otherwise the default is `SHROUD`
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD
        )

