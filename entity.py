class Entity:
    """
    Generic object to represent general propouses entities
    """
    def __init__(self, x: int, y: int, char: str, color: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx: int, dy: int) -> None:
        """
        Move entity by given amount
        """
        self.x += dx
        self.y += dy

    @property
    def info(self) -> tuple[int, int, str, tuple[int, int, int]]:
        return self.x, self.y, self.char, self.color
